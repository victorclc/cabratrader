import numpy as np
from exchange.models import ChartData, Ticker, TradeStream


class BinanceChartData(ChartData):
    def __init__(self, data):
        date, high, low, open, close, volume, quote_volume, weighted_average = [], [], [], [], [], [], [], []
        for candle in data:
            date.append(candle[0])
            high.append(candle[2])
            low.append(candle[3])
            open.append(candle[1])
            close.append(candle[4])
            volume.append(candle[5])
            quote_volume.append(candle[7])

        self.date = date
        self.high = np.float64(high)
        self.low = np.float64(low)
        self.open = np.float64(open)
        self.close = np.float64(close)
        self.volume = np.float64(volume)
        self.quote_volume = np.float64(quote_volume)
        self.weighted_average = np.float64(weighted_average)

    def __getitem__(self, item):
        chart = {
            'high': self.high[item],
            'low': self.low[item],
            'open': self.open[item],
            'close': self.close[item],
            'volume': self.volume[item],
            'quote_volume': self.quote_volume[item]
        }
        return chart


class BinanceTicker(Ticker):
    @classmethod
    def init_web_socket(cls, data):
        ticker = cls()
        ticker.quote_volume = data['q']
        ticker.last = np.float64(data['a'])
        ticker.lowest_ask = np.float64(data['a'])
        ticker.highest_bid = np.float64(data['b'])
        ticker.base_volume = data['v']
        ticker.percent_change = data['P']
        return ticker

    @classmethod
    def init_rest(cls, data):
        ticker = cls()
        ticker.quote_volume = np.float64(data['quoteVolume'])
        ticker.last = np.float64(data['lastPrice'])
        ticker.lowest_ask = np.float64(data['askPrice'])
        ticker.highest_bid = np.float64(data['bidPrice'])
        ticker.base_volume = np.float64(data['quoteVolume'])
        ticker.percent_change = data['priceChange']
        return ticker

    def update_ticker(self, data):
        self.quote_volume = data['q']
        self.last = np.float64(data['a'])
        self.lowest_ask = np.float64(data['a'])
        self.highest_bid = np.float64(data['b'])
        self.base_volume = data['v']
        self.percent_change = data['P']


class Restrictions(object):
    def __init__(self, json):
        filters = json['filters']
        lot_rest = list(filter(lambda y: y['filterType'] == "LOT_SIZE", filters))[0]
        min_notional = list(filter(lambda y: y['filterType'] == "MIN_NOTIONAL", filters))[0]
        price_filter = list(filter(lambda y: y['filterType'] == "PRICE_FILTER", filters))[0]

        self.raw = json
        self.min_amt = np.float64(lot_rest['minQty'])
        self.step = np.float64(lot_rest['stepSize'])
        self.min_notional = np.float64(min_notional['minNotional'])
        self.price_tick = np.float64(price_filter['tickSize'])


class BinanceTradeStream(TradeStream):
    def __init__(self):
        super().__init__()
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

    @classmethod
    def init_web_socket(cls, data):
        trade = cls()
        trade.event_time = data['E']
        trade.symbol = data['s']
        trade.trade_id = data['t']
        trade.price = np.float64(data['p'])
        trade.amount = np.float64(data['q'])
        trade.buyer_order_id = data['b']
        trade.seller_order_id = data['a']
        trade.ref_date = data['T'] / 1000
        return trade
