from analysis.abstract.analysis import ChartAnalysis


class BBands(ChartAnalysis):
    from exchange.binance.models import BinanceChartData

    def __init__(self):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

    def clean(self):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

    def analyze(self, chart: BinanceChartData):
        self.clean()
        upper, middle, lower = chart.indicator_value({"indicator": "bbands"})

        # print("BB", lower[-1])
        # print(chart.close[-1])

        # print(upper[-1], middle[-1], lower[-1])
        if lower[-1] >= chart.close[-1]:
            self.suggestion = 'BUY'
        elif upper[-1] <= chart.close[-1]:
            self.suggestion = 'SELL'
        else:
            # print('HOLD')
            self.suggestion = 'HODL'

        self.price = chart.close[-1]
        self.ref_date = int(chart.date[-1]/1000)
        self.analysis = 'bbands: {}, {}, {}'.format(upper[-1], middle[-1], lower[-1])

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

    @property
    def symbol(self):
        return self.__symbol

    @symbol.setter
    def symbol(self, symbol):
        self.__symbol = symbol

    @property
    def run_id(self):
        return self.__run_id

    @run_id.setter
    def run_id(self, run_id):
        self.__run_id = run_id


d_analysis = BBands()
