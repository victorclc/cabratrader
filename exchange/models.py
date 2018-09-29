import ta.algorithms as algo
import numpy as np

from core.runconstants import RunConstants
from database.abstract.persistable import PersistableObject
import common.helper as helper


class ChartData(object):
    def __init__(self):
        self.date = []
        self.high = []
        self.low = []
        self.open = []
        self.close = []
        self.volume = []
        self.quote_volume = []
        self.weighted_average = []

    def indicator_value(self, config):
        params = {
            'close': self.close,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            **config
        }
        func = getattr(algo, params['indicator'].upper())
        return func(**params)


class Ticker(object):
    def __init__(self):
        self.last = None
        self.lowest_ask = None
        self.highest_bid = None
        self.percent_change = None
        self.base_volume = None
        self.quote_volume = None


class Order(PersistableObject):
    logger = helper.load_logger('Order')

    def __init__(self, side, symbol, price, amount, simulation):
        self.order_id = None
        self.side = side
        self.symbol = symbol
        self.price = price
        self.amount = amount
        self.simulation = simulation
        self.active = True
        self.ref_date = 0
        self.cycle_id = 0

        if simulation:
            self.avg_price = np.float64(price)
            self.exec_amount = np.float64(amount)
            self.gross_total = self.avg_price * self.exec_amount
            self.net_total = self.gross_total * (1 - 0.05 / 100)
            self.fee_asset = 'BTC'
            self.fee = self.gross_total * (0.05 / 100)
            self.active = False
        else:
            self.avg_price = np.float64(0)
            self.exec_amount = np.float64(0)
            self.gross_total = np.float64(0)
            self.net_total = np.float64(0)
            self.fee_asset = None
            self.fee = np.float64(0)

    def persistables(self):
        pers = {
            'order_id': self.order_id,
            'cycle_id': self.cycle_id,
            'run_id': RunConstants.run_id,
            'type': self.side,
            'symbol': self.symbol,
            'price': self.price,
            'amount': self.amount,
            'simulation': self.simulation,
            'avg_price': self.avg_price,
            'exec_amount': self.exec_amount,
            'gross_total': self.gross_total,
            'net_total': self.net_total,
            'fee_asset': self.fee_asset,
            'fee': self.fee,
            'active': self.active,
            'ref_date': 'to_timestamp(%d)' % self.ref_date,
            '__key__': 'order_id'
        }
        return pers

    def fill_summary(self, summary):
        self.avg_price = summary['avg_price']
        self.exec_amount = summary['exec_amount']
        self.gross_total = summary['gross_total']
        self.net_total = summary['net_total']
        self.fee_asset = summary['fee_asset']
        self.fee = summary['fee']
        self.active = summary['active']
        self.ref_date = summary['ref_date']
        self.logger.info('{} - ORDER UPDATED ({})'.format(self.symbol, self.order_id))

    def is_buy(self):
        return self.side == OrderSide.BUY

    def is_sell(self):
        return self.side == OrderSide.SELL


class OrderSide(object):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderType(object):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'


class TradeStream(object):
    def __init__(self):
        self.event_time = None
        self.symbol = None
        self.market = None
        self.coin = None
        self.trade_id = None
        self.price = None
        self.amount = None
        self.buyer_order_id = None
        self.seller_order_id = None
        self.ref_date = None
