from abc import ABC, abstractmethod
from exchange.models import TradeStream, Ticker, ChartData
import common.helper as helper
from numpy import float64


class Strategy(ABC):
    def __init__(self, broker, symbol, amount, setup, simulation):
        self.broker = broker
        self.symbol = symbol
        self.amount = float64(amount)
        self.setup = self.SetupWrapper(setup)
        self.simulation = simulation
        self.setup_callbacks()

    def setup_callbacks(self):
        self.broker.register_chart_callback(self.symbol, self.setup.period, self.setup.zoom, self.on_chart_update)
        self.broker.register_ticker_callback(self.symbol, self.on_ticker_update)
        self.broker.register_trade_callback(self.symbol, self.on_trade_update)
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
        """

        :param summary: dictionary
        :return:
        """
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
