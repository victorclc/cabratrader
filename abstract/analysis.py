from abc import ABC, abstractmethod

from abstract.database import PersistableObject
from exchange.models import ChartData, TradeStream
from core.run import Run


class Analysis(ABC):
    @abstractmethod
    def analyze(self, **kwargs):
        pass

    @property
    @abstractmethod
    def suggestion(self):
        pass

    @suggestion.setter
    @abstractmethod
    def suggestion(self, suggestion):
        pass

    @property
    @abstractmethod
    def price(self):
        pass

    @price.setter
    @abstractmethod
    def price(self, price):
        pass

    @property
    @abstractmethod
    def analysis(self):
        pass

    @analysis.setter
    @abstractmethod
    def analysis(self, analysis):
        pass

    @property
    @abstractmethod
    def ref_date(self):
        pass

    @ref_date.setter
    @abstractmethod
    def ref_date(self, ref_date):
        pass

    @property
    @abstractmethod
    def order_id(self):
        pass

    @order_id.setter
    @abstractmethod
    def order_id(self, order_id):
        pass

    def persistables(self):
        pers = {
            'run_id': Run.run_id,
            'suggestion': self.suggestion,
            'price': self.price,
            'analysis': self.analysis,
            'ref_date': 'to_timestamp({})'.format(self.ref_date),
            'order_id': self.order_id,
            '__table__': 'c_analysis'
        }
        return pers


class ChartAnalysis(Analysis, PersistableObject):
    @abstractmethod
    def analyze(self, chart: ChartData):
        pass


class TradeAnalysis(Analysis, PersistableObject):
    @abstractmethod
    def analyze(self, trade: TradeStream, buy_price, target, max_loss):
        pass
