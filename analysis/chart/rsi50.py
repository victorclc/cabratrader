from abstract.analysis import ChartAnalysis


class Rsi50(ChartAnalysis):
    from exchange.binance.models import BinanceChartData

    def __init__(self):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None

    def analyze(self, chart: BinanceChartData):
        rsi = chart.indicator_value({"indicator": "rsi"})
        self.suggestion = 'BUY' if rsi[-1] < 50 else 'SELL'
        self.price = chart.close[-1]
        self.ref_date = int(chart.date[-1]/1000)
        self.analysis = 'rsi: {}'.format(rsi[-1])

        return self

    @property
    def suggestion(self):
        return self.__suggestion

    @suggestion.setter
    def suggestion(self, suggestion):
        self.__suggestion = suggestion

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        self.__price = price

    @property
    def analysis(self):
        return self.__analysis

    @analysis.setter
    def analysis(self, analysis):
        self.__analysis = analysis

    @property
    def ref_date(self):
        return self.__ref_date

    @ref_date.setter
    def ref_date(self, ref_date):
        self.__ref_date = ref_date

    @property
    def order_id(self):
        return self.__order_id

    @order_id.setter
    def order_id(self, order_id):
        self.__order_id = order_id


d_analysis = Rsi50()
