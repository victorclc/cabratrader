from abstract.strategy import Strategy
import common.helper as helper
from database.datamanager import DataManager
from exchange.models import OrderSide
from strategy.common.cycle import Cycle, CycleState
from external.notification.telegram import PushNotification
from collections import deque


class TechnicalOnly(Strategy):
    logger = helper.load_logger('Strategy')

    def __init__(self, broker, symbol, amount, setup, simulation):
        self.logger.info('New Instance: Symbol {} Simulation {}'.format(symbol, str(simulation)))
        super().__init__(broker, symbol, amount, setup, simulation)
        self.ticker = None
        self.cycle = Cycle(symbol)
        self.summaries_queue = deque()
        self.lock_buy = False

    @property
    def available_amt(self):
        return self.amount - self.cycle.spent + self.cycle.sold

    def on_trade_update(self, trade):
        if self.cycle.state == CycleState.WATCHING or self.cycle.state == CycleState.BUYING:
            analysis = self.setup.analysis.trade.watching.analyze(trade, 0.0, self.setup.target, self.setup.max_loss)
        else:
            analysis = self.setup.analysis.trade.holding.analyze(trade, self.cycle.avg_buy_price, self.setup.target,
                                                                 self.setup.max_loss)
        self.take_action(analysis)

    def on_ticker_update(self, ticker):
        self.ticker = ticker

        if self.summaries_queue:
            self.on_order_update(self.summaries_queue.popleft())

        if self.cycle.state == CycleState.COMPLETED:
            self.handle_cycle_completed()

    def on_order_update(self, summary):
        for order in self.cycle.orders:
            if order.order_id == summary['order_id']:
                self.logger('{} - ORDER UPDATED ({})'.format(self.symbol, order.order_id))
                order.fill_summary(order)
                DataManager.persist(order)
                break
        else:
            self.logger('{} - ORDER NOT FOUND ({}) YET'.format(self.symbol, summary['order_id']))
            self.summaries_queue.append(summary)

        if self.cycle.is_completed():
            self.handle_cycle_completed()

    def on_chart_update(self, chart):
        if self.cycle.state == CycleState.WATCHING or self.cycle.state == CycleState.BUYING:
            analysis = self.setup.analysis.chart.watching.analyze(chart)
        else:
            analysis = self.setup.analysis.chart.holding.analyze(chart)
        self.take_action(analysis)

    def take_action(self, analysis):
        if analysis.suggestion == 'BUY':
            if self.lock_buy is False:
                self.handle_buy_action(analysis)
        elif analysis.suggestion == 'SELL':
            self.handle_sell_action(analysis)

    def handle_buy_action(self, analysis):
        self.logger.info(analysis.__dict__)
        if self.cycle.state == CycleState.BUYING:
            for order in self.cycle.open_buy_orders:
                if analysis.price > order.price:
                    self.broker.cancel_order(order)
        if self.cycle.state == CycleState.SELLING:
            for order in self.cycle.open_sell_orders:
                self.broker.cancel_order(order)

        amount = self.available_amt / analysis.price
        order = self.broker.place_limit_order(OrderSide.BUY, self.symbol, analysis.price, amount,
                                              self.simulation)
        if order:
            self.logger.info('{} - BUY ORDER PLACED ({})'.format(self.symbol, order.order_id))
            analysis.order_id = order.order_id
            order.ref_date = analysis.ref_date
            order.cycle_id = self.cycle.cycle_id
            self.cycle.buy_orders.append(order)
            DataManager.persist(self.cycle)
            DataManager.persist(order)

        DataManager.persist(analysis)

    def handle_sell_action(self, analysis):
        self.logger.info(analysis.__dict__)
        if self.cycle.state == CycleState.BUYING:
            for order in self.cycle.open_buy_orders:
                self.broker.cancel_order(order)
        if self.cycle.state == CycleState.SELLING:
            for order in self.cycle.open_sell_orders:
                if analysis.price < order.price:
                    self.broker.cancel_order(order)

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

        DataManager.persist(analysis)

    def handle_cycle_completed(self):
        self.logger.info('%s - CYCLE COMPLETED | Profit: %.8f' % (self.symbol, self.cycle.profit.round(8)))
        PushNotification.send('%s - CYCLE COMPLETED | Profit: %.8f' % (self.symbol, self.cycle.profit.round(8)))
        self.amount += self.cycle.profit.round(8)
        DataManager.persist(self.cycle)
        self.cycle = Cycle(self.symbol)
