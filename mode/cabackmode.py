from abstract.mode import Mode
import common.helper as helper
from binance.client import Client
import requests
from exchange.binance.broker import Broker
from exchange.binance.models import BinanceChartData
from exchange.models import TradeStream, ChartData
from strategy.fop import Fop
from strategy.technicalonly import TechnicalOnly
from external.notification.telegram import PushNotification
from datetime import time


class CabackMode(Mode):
    def __init__(self):
        super().__init__()
        self.config = helper.load_config("mode/caback.cfg")
        self.logger = helper.load_logger('Mode')
        self.client = Client(None, None)
        self.market = self.config['market']
        self.coins = self.config['coins']
        self.min_volume = self.config['min_volume']
        self.begin_date = self.config['begin_date']
        self.end_date = self.config['end_date']
        self.start_amount = self.config['start_amount']
        self.setup = self.config['setup']
        self.work_start = time(*[int(x) for x in self.config['work_start'].split(':')])
        self.work_end = time(*[int(x) for x in self.config['work_end'].split(':')])
        PushNotification.active = False

    @staticmethod
    def get_all_coins(market, volume):
        tickers = requests.get("https://api.binance.com/api/v1/ticker/24hr").json()
        coins = []

        for ticker in tickers:
            if ticker['symbol'][-len(market):] == market and float(ticker['quoteVolume']) >= volume:
                coins.append(ticker['symbol'][0:-len(market)])
        return coins

    def start(self):
        broker = Broker(None, None)

        if not self.coins:
            self.coins = self.get_all_coins(self.market, self.min_volume)

        self.logger.info("StartAmount: " + str(self.start_amount))

        for coin in self.coins:
            index = 0
            symbol = coin + self.market

            params = {
                "run_id": self.run.run_id,
                "broker": broker,
                "symbol": symbol,
                "amount": self.start_amount,
                "setup": self.setup,
                "simulation": True,
                "work_start": self.work_start,
                "work_end": self.work_end
            }
            instance = self.spawn_strategy_instance(params)
            klines = self.client.get_historical_klines(symbol, instance.setup.period, self.begin_date, self.end_date)
            zoom = int(helper.config2seconds(instance.setup.zoom) / helper.config2seconds(instance.setup.period))

            while index + zoom <= len(klines):
                chart = BinanceChartData(klines[index:zoom + index])
                instance.on_chart_update(chart)
                instance.check_triggers(chart)
                index += 1

            self.logger.info("Currency: %s (%s)" % (symbol, str(instance.amount)))

    def spawn_strategy_instance(self, info):
        return SimTechnical(**info)


class SimTechnical(Fop):
    def setup_callbacks(self):
        pass

    def on_chart_update(self, chart):
        if self.cycle.is_completed():
            self.handle_cycle_completed()

        super().on_chart_update(chart)

    def check_triggers(self, chart: ChartData):
        trade_high = TradeStream()
        trade_high.symbol = self.symbol
        trade_high.price = chart.high[-1]
        trade_high.ref_date = int(chart.date[-1] / 1000)
        super().on_trade_update(trade_high)

        trade_low = TradeStream()
        trade_low.symbol = self.symbol
        trade_low.price = chart.low[-1]
        trade_low.ref_date = int(chart.date[-1] / 1000)
        super().on_trade_update(trade_low)
