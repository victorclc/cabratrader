from analysis.abstract.analysis import TimeAnalysis


class StopTime(TimeAnalysis):
    def __init__(self):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

    def analyze(self, cycle, chart):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

        from core.strategy import CycleState
        if cycle.state == CycleState.BOUGHT:
            buy_time = None
            for order in cycle.buy_orders:
                if order.exec_amount > 0.0:
                    buy_time = order.ref_date
            now = chart.date[-1] / 1000

            if now - buy_time >= 10800:
                print(now, buy_time)
                self.suggestion = "SELL"
                self.analysis = "STOP_TIME"
                self.price = chart.close[-1]
                self.ref_date = now

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


d_analysis = StopTime()
