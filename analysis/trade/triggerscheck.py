from analysis.abstract.analysis import TradeAnalysis


class TriggerCheck(TradeAnalysis):
    def __init__(self):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

    def analyze(self, trade, buy_price, target, max_loss):
        self.__suggestion = None
        self.__price = None
        self.__analysis = None
        self.__order_id = None
        self.__ref_date = None
        self.__symbol = None
        self.__run_id = None

        if target > 0 and buy_price > 0 and buy_price * target <= trade.price:
            if buy_price.round(8) == (buy_price * target).round(8):
                self.suggestion = "HOLD"
            else:
                self.suggestion = "SELL"
                self.price = buy_price * target
                self.analysis = "TARGET_REACHED"
        elif buy_price * max_loss >= trade.price:
            self.price = buy_price * max_loss
            self.suggestion = "SELL"
            self.analysis = "STOP_LOSS"
        else:
            self.suggestion = "HOLD"
            self.analysis = "HOLD"
            self.price = 0.0
        self.ref_date = trade.ref_date
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


d_analysis = TriggerCheck()
