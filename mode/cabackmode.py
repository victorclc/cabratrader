from time import sleep

from core.mode import Mode
import common.helper as helper
from binance.client import Client
import requests
from exchange.binance.broker import Broker
from exchange.binance.models import BinanceChartData
from exchange.models import TradeStream, ChartData
from datetime import time
import threading


class CabackMode(Mode):
    def __init__(self):
        super().__init__()
        data = helper.load_config("caback.cfg")
        self.logger = helper.load_logger('Mode')
        self.client = Client(None, None)
        self.market = data['market']
        self.coins = data['coins']
        self.min_volume = data['min_volume']
        self.begin_date = data['begin_date']
        self.end_date = data['end_date']
        self.start_amount = data['start_amount']
        self.setup = data['setup']
        self.strategy = data['strategy']
        self.work_start = time(*[int(x) for x in data['work_start'].split(':')]) if data['work_start'] else None
        self.work_end = time(*[int(x) for x in data['work_end'].split(':')]) if data['work_end'] else None
        self._active_threads = 0

    @staticmethod
    def get_all_coins(market, volume):
        tickers = requests.get("https://api.binance.com/api/v1/ticker/24hr").json()
        coins = []

        # TODO CRIAR CONFIG PARA VALOR MINIMO DA MOEDA
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
            symbol = coin + self.market

            params = {
                "broker": broker,
                "symbol": symbol,
                "amount": self.start_amount,
                "setup": self.setup,
                "simulation": True,
                "work_start": self.work_start,
                "work_end": self.work_end
            }
            instance = self.spawn_strategy_instance(self.strategy, params)
            klines = self.client.get_historical_klines(symbol, instance.setup.period, self.begin_date, self.end_date)
            zoom = int(helper.config2seconds(instance.setup.zoom) / helper.config2seconds(instance.setup.period))

            t = threading.Thread(target=self._run, args=[symbol, instance, klines, zoom])
            while self._active_threads >= 10:
                sleep(5)
            t.start()

    def _run(self, symbol, instance, klines, zoom):
        self._active_threads += 1
        index = 0
        while index + zoom <= len(klines):
            chart = BinanceChartData(klines[index:zoom + index])
            self.check_triggers(symbol, chart, instance)
            instance.on_chart_update(chart)
            index += 1

        self.logger.info("Currency: %s (%s)" % (symbol, str(instance.amount)))
        self._active_threads -= 1

    @staticmethod
    def check_triggers(symbol, chart: ChartData, instance):
        trade_high = TradeStream()
        trade_high.symbol = symbol
        trade_high.price = chart.high[-1]
        trade_high.ref_date = int(chart.date[-1] / 1000)
        instance.on_trade_update(trade_high)

        trade_low = TradeStream()
        trade_low.symbol = symbol
        trade_low.price = chart.low[-1]
        trade_low.ref_date = int(chart.date[-1] / 1000)
        instance.on_trade_update(trade_low)
