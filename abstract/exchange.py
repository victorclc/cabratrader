from abc import ABC, abstractmethod


class Broker(ABC):
    @abstractmethod
    def on_order_update(self, order):
        pass

    @abstractmethod
    def register_chart_callback(self, symbol, period, zoom, func):
        pass

    @abstractmethod
    def register_ticker_callback(self, symbol, func):
        pass

    @abstractmethod
    def register_trade_callback(self, symbol, func):
        pass

    @abstractmethod
    def register_account_callback(self, symbol, func):
        pass

    @abstractmethod
    def place_limit_order(self, side, symbol, price, amount, simulation):
        pass

    @abstractmethod
    def place_market_order(self, side, symbol, price, amount, simulation):
        pass

    @abstractmethod
    def place_take_profit_order(self, side, symbol, stop_price, price, amount):
        pass

    @abstractmethod
    def place_limit_take_profit_order(self, side, symbol, stop_price, price, amount):
        pass

    @abstractmethod
    def cancel_order(self, order):
        pass
