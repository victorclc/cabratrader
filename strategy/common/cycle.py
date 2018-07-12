from database.datamanager import DataManager
from abstract.database import PersistableObject
from enum import Enum
from numpy import float64
from core.run import Run


class Cycle(PersistableObject):
    def __init__(self, symbol):
        self.symbol = symbol
        self.buy_orders = []
        self.sell_orders = []
        self.ref_date = 0.0
        self.cycle_id = None
        self.ZERO = float64(0)

    def persistables(self):
        self.cycle_id = self.cycle_id if self.cycle_id else DataManager.next_sequence('s_cycle_id')
        pers = {
            'cycle_id': self.cycle_id,
            'run_id': Run.run_id,
            'symbol': self.symbol,
            'status': 'COMPLETED' if self.is_completed() else 'ACTIVE',
            'profit': 0.0 if self.is_completed() is False else self.profit,
            'profit_perc': self.profit_percent,
            'base_amount': self.base_amount,
            'ref_date': None if self.is_completed() is False else 'to_timestamp(%d)' % self.sell_orders[-1].ref_date,
            '__key__': 'cycle_id'
        }
        return pers

    @property
    def state(self):
        if self.bought_amount == 0.0 and not self.has_open_buy_orders():
            return CycleState.WATCHING
        if self.has_open_buy_orders():
            return CycleState.BUYING
        if self.bought_amount > 0.0 and not self.has_open_sell_orders() and not self.is_completed():
            return CycleState.BOUGHT
        if self.has_open_sell_orders():
            return CycleState.SELLING
        if self.is_completed():
            return CycleState.COMPLETED
        return CycleState.UNKNOWN

    @property
    def orders(self):
        return self.buy_orders + self.sell_orders

    @property
    def profit(self):
        spent = sum(x.gross_total for x in self.buy_orders)
        sold = sum(x.net_total for x in self.sell_orders)
        return sold - spent

    @property
    def sold_amount(self):
        if self.sell_orders:
            return sum(order.exec_amount for order in self.sell_orders)
        return self.ZERO

    @property
    def bought_amount(self):
        if self.buy_orders:
            return sum(order.exec_amount for order in self.buy_orders)
        return self.ZERO

    @property
    def spent(self):
        if self.buy_orders:
            return sum(order.gross_total for order in self.buy_orders)
        return self.ZERO

    @property
    def sold(self):
        if self.sell_orders:
            return sum(x.net_total for x in self.sell_orders)
        return self.ZERO

    @property
    def profit_percent(self):
        if not self.is_completed():
            return self.ZERO
        return (self.profit * 100) / self.base_amount

    @property
    def base_amount(self):
        if not self.is_completed():
            return self.ZERO
        return sum(order.amount * order.price for order in self.buy_orders)

    @property
    def open_buy_orders(self):
        orders = []
        for order in self.buy_orders:
            if order.active:
                orders.append(order)
        return orders

    @property
    def open_sell_orders(self):
        orders = []
        for order in self.sell_orders:
            if order.active:
                orders.append(order)
        return orders

    @property
    def avg_buy_price(self):
        # todo where exec_Amount > 0
        return (sum(order.avg_price for order in self.buy_orders) / len(self.buy_orders)).round(8)
    
    @property
    def on_buy_orders(self):
        total = float64(0)
        for order in self.buy_orders:
            if order.active:
                total = order.price * (order.amount - order.exec_amount)
        return total

    def is_completed(self):
        if not self.buy_orders or not self.sell_orders:
            return False

        bought = sum(order.exec_amount for order in self.buy_orders).round(8)
        sold = sum(order.exec_amount for order in self.sell_orders).round(8)
        return bought == sold

    def has_open_buy_orders(self):
        for order in self.buy_orders:
            if order.active:
                return True
        return False

    def has_open_sell_orders(self):
        for order in self.sell_orders:
            if order.active:
                return True
        return False

    def is_holding(self):
        return self.bought_amount > 0.0


class CycleState(Enum):
    WATCHING = 1
    BUYING = 2
    BOUGHT = 3
    SELLING = 4
    SOLD = 5
    COMPLETED = 6
    UNKNOWN = 7
