from abc import ABC, abstractmethod
from core.run import Run


class Mode(ABC):
    def __init__(self):
        self.run = Run(type(self).__name__)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def spawn_strategy_instance(self, info):
        pass

    @classmethod
    def init_run(cls):
        Run(cls.__name__)
