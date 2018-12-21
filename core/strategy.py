from abc import ABC, abstractmethod
from collections import deque
from enum import Enum

from numpy import float64

from core.runconstants import RunConstants
from database.abstract.persistable import PersistableObject
from database.datamanager import DataManager
from exchange.models import TradeStream, Ticker, ChartData, OrderSide
import common.helper as helper
from datetime import datetime


class Strategy(ABC):
    logger = helper.load_logger('Strategy')

    def __init__(self, broker, symbol, amount, setup, simulation):
        self.broker = broker
        self.symbol = symbol
        self.amount = float64(amount)
        self.setup = self.SetupWrapper(setup)
        self.simulation = simulation
        self.instance = Instance(symbol, amount)

        if RunConstants.mode != 'CabackMode':
            self.setup_callbacks()

        DataManager.persist(self.instance)

    def setup_callbacks(self, account=True, chart=True, ticker=True, trade=True):
        if chart:
            self.broker.register_chart_callback(self.symbol, self.setup.period, self.setup.zoom, self.on_chart_update)
        if ticker:
            self.broker.register_ticker_callback(self.symbol, self.on_ticker_update)
        if trade:
            self.broker.register_trade_callback(self.symbol, self.on_trade_update)
        if account:
            self.broker.register_account_callback(self.symbol, self.on_order_update)

    @abstractmethod
    def on_trade_update(self, trade: TradeStream):
        pass

    @abstractmethod
    def on_ticker_update(self, ticker: Ticker):
        pass

    @abstractmethod
    def on_chart_update(self, chart: ChartData):
        pass

    @abstractmethod
    def on_order_update(self, summary):
        pass

    class SetupWrapper:
        def __init__(self, name):
            config = helper.load_config('setup.cfg')[name]
            self.name = name
            self.period = config['period']
            self.zoom = config['zoom']
            self.max_loss = config['max_loss']
            self.target = config['target']
            self.analysis = self.AnalysisWrapper(config['analysis'])

        class AnalysisWrapper:
            def __init__(self, analysis):
                self.chart = self.ScriptWrapper(analysis['chart'])
                self.trade = self.ScriptWrapper(analysis['trade'])

            class ScriptWrapper:
                def __init__(self, chart):
                    self.watching = helper.load_analyser(chart['watching'])
                    self.holding = helper.load_analyser(chart['holding'])


class Cycle(PersistableObject):

    def __init__(self, symbol):
        self.symbol = symbol
        self.buy_orders = []
        self.sell_orders = []
        self.ref_date = 0.0
        self.cycle_id = None
        self.ZERO = float64(0)

    def persistables(self):
        self.cycle_id = self.cycle_id if self.cycle_id else DataManager.next_sequence('s_cycle_id')
        pers = {
            'cycle_id': self.cycle_id,
            'run_id': RunConstants.run_id,
            'symbol': self.symbol,
            'status': 'COMPLETED' if self.is_completed() else 'ACTIVE',
            'profit': 0.0 if self.is_completed() is False else self.profit,
            'profit_perc': self.profit_percent,
            'base_amount': self.base_amount,
            'ref_date': None if self.is_completed() is False else 'to_timestamp(%d)' % self.sell_orders[-1].ref_date,
            '__key__': 'cycle_id'
        }
        return pers

    @property
    def state(self):
        if self.bought_amount == 0.0 and not self.has_open_buy_orders():
            return CycleState.WATCHING
        if self.has_open_buy_orders():
            return CycleState.BUYING
        if self.bought_amount > 0.0 and not self.has_open_sell_orders() and not self.is_completed():
            return CycleState.BOUGHT
        if self.has_open_sell_orders():
            return CycleState.SELLING
        if self.is_completed():
            return CycleState.COMPLETED
        return CycleState.UNKNOWN

    @property
    def orders(self):
        return self.buy_orders + self.sell_orders

    @property
    def profit(self):
        spent = sum(x.gross_total for x in self.buy_orders)
        sold = sum(x.net_total for x in self.sell_orders)
        return sold - spent

    @property
    def sold_amount(self):
        if self.sell_orders:
            return sum(order.exec_amount for order in self.sell_orders)
        return self.ZERO

    @property
    def bought_amount(self):
        if self.buy_orders:
            return sum(order.exec_amount for order in self.buy_orders)
        return self.ZERO

    @property
    def spent(self):
        if self.buy_orders:
            return sum(order.gross_total for order in self.buy_orders)
        return self.ZERO

    @property
    def sold(self):
        if self.sell_orders:
            return sum(x.net_total for x in self.sell_orders)
        return self.ZERO

    @property
    def profit_percent(self):
        if not self.is_completed():
            return self.ZERO
        return (self.profit * 100) / self.base_amount

    @property
    def base_amount(self):
        if not self.is_completed():
            return self.ZERO
        return sum(order.amount * order.price for order in self.buy_orders)

    @property
    def open_buy_orders(self):
        orders = []
        for order in self.buy_orders:
            if order.active:
                orders.append(order)
        return orders

    @property
    def open_sell_orders(self):
        orders = []
        for order in self.sell_orders:
            if order.active:
                orders.append(order)
        return orders

    @property
    def avg_buy_price(self):
        return (sum(order.avg_price for order in self.buy_orders) / len(self.buy_orders)).round(8)

    @property
    def on_buy_orders(self):
        total = float64(0)
        for order in self.buy_orders:
            if order.active:
                total = order.price * (order.amount - order.exec_amount)
        return total

    def is_completed(self):
        if not self.buy_orders or not self.sell_orders:
            return False

        bought = sum(order.exec_amount for order in self.buy_orders).round(8)
        sold = sum(order.exec_amount for order in self.sell_orders).round(8)
        return bought == sold

    def has_open_buy_orders(self):
        for order in self.buy_orders:
            if order.active:
                return True
        return False

    def has_open_sell_orders(self):
        for order in self.sell_orders:
            if order.active:
                return True
        return False

    def is_holding(self):
        return self.bought_amount > 0.0


class CycleState(Enum):
    WATCHING = 1
    BUYING = 2
    BOUGHT = 3
    SELLING = 4
    SOLD = 5
    COMPLETED = 6
    UNKNOWN = 7


class CycleStrategy(Strategy, ABC):
    def __init__(self, broker, symbol, amount, setup, simulation, work_start, work_end):
        super().__init__(broker, symbol, amount, setup, simulation)
        self.summaries_queue = deque()
        self.cycle = Cycle(symbol)
        self.ticker = None
        self.lock_buy = False
        self.work_start = work_start
        self.work_end = work_end
        self.logger.info('New Instance: Symbol {} Simulation {}'.format(symbol, str(simulation)))

    def in_working_range(self, now_time):
        if self.work_start is None or self.work_end is None:
            return True
        if self.work_start < self.work_end:
            return self.work_start <= now_time <= self.work_end
        else:
            return now_time >= self.work_start or now_time <= self.work_end

    @property
    def available_amt(self):
        return self.amount - self.cycle.on_buy_orders - self.cycle.spent + self.cycle.sold

    @helper.callstalker
    def on_order_update(self, summary):
        for order in self.cycle.orders:
            if order.order_id == summary['order_id']:
                order.fill_summary(summary)
                self.logger.info('{} - ORDER UPDATED ({})'.format(self.symbol, order.order_id))
                DataManager.persist(order)
                break
        else:
            self.summaries_queue.append(summary)

        if self.cycle.state == CycleState.COMPLETED:
            self.handle_cycle_completed()

    def on_ticker_update(self, ticker: Ticker):
        self.ticker = ticker

        if self.summaries_queue:
            self.on_order_update(self.summaries_queue.popleft())

    def handle_buy_action(self, analysis):
        if not self.in_working_range(datetime.utcfromtimestamp(analysis.ref_date).time()):
            return

        self.logger.info('{} - {}'.format(self.symbol, analysis.__dict__))
        if self.cycle.state == CycleState.BUYING:
            for order in self.cycle.open_buy_orders:
                if analysis.price > order.price:
                    self.broker.cancel_order(order)
        if self.cycle.state == CycleState.SELLING:
            for order in self.cycle.open_sell_orders:
                self.broker.cancel_order(order)

        amount = self.available_amt / analysis.price

        try:
            order = self.broker.place_limit_order(OrderSide.BUY, self.symbol, analysis.price, amount,
                                                  self.simulation)
            if order:
                self.logger.info('{} - BUY ORDER PLACED ({})'.format(self.symbol, order.order_id))
                analysis.order_id = order.order_id
                DataManager.persist(self.cycle)
                analysis.order_id = order.order_id
                order.ref_date = analysis.ref_date
                order.cycle_id = self.cycle.cycle_id
                self.cycle.buy_orders.append(order)
                DataManager.persist(order)
        except Exception as ex:
            helper.dump_to_file(self, extra=str(ex), prefix=self.symbol)

    def handle_sell_action(self, analysis):
        self.logger.info('{} - {}'.format(self.symbol, analysis.__dict__))
        if self.cycle.state == CycleState.BUYING:
            for order in self.cycle.open_buy_orders:
                self.broker.cancel_order(order)
        if self.cycle.state == CycleState.SELLING:
            for order in self.cycle.open_sell_orders:
                if analysis.price < order.price:
                    self.broker.cancel_order(order)

        try:
            order = self.broker.place_limit_order(OrderSide.SELL, self.symbol, analysis.price,
                                                  self.cycle.bought_amount - self.cycle.sold_amount, self.simulation)
            if order:
                self.logger.info('{} - SELL ORDER PLACED ({})'.format(self.symbol, order.order_id))
                analysis.order_id = order.order_id
                order.ref_date = analysis.ref_date
                order.cycle_id = self.cycle.cycle_id
                self.cycle.sell_orders.append(order)
                DataManager.persist(self.cycle)
                DataManager.persist(order)
        except Exception as ex:
            helper.dump_to_file(self, extra=str(ex), prefix=self.symbol)

    def handle_cycle_completed(self):
        self.logger.info('%s - CYCLE COMPLETED | Profit: %.8f' % (self.symbol, self.cycle.profit.round(8)))
        self.amount += self.cycle.profit.round(8)
        self.instance.amount = self.amount

        DataManager.persist(self.instance)
        DataManager.persist(self.cycle)

        self.cycle = Cycle(self.symbol)

    def take_action(self, analysis):
        if analysis.suggestion == 'BUY':
            if self.lock_buy is False:
                self.handle_buy_action(analysis)
        elif analysis.suggestion == 'SELL':
            self.handle_sell_action(analysis)


class Instance(PersistableObject):
    def __init__(self, symbol, start_amount):
        self.symbol = symbol
        self.start_amount = start_amount
        self.amount = start_amount

    def persistables(self):
        pers = {
            'run_id': RunConstants.run_id,
            'symbol': self.symbol,
            'start_amount': self.start_amount,
            'end_amount': self.amount,
            'perc': float('%.4f' % ((self.amount - self.start_amount) * 100 / self.start_amount)),
            '__key__': ['run_id', 'symbol']
        }
        return pers
