from decimal import Decimal

from binance.client import Client

import exchange.abstract.broker as abc
from exchange.binance.models import Restrictions
from exchange.binance.stalkers import AccountStalker, TradeStalker, TickerStalker, ChartStalker
from exchange.models import *
import numpy as np
from database.datamanager import DataManager


class Broker(abc.Broker):
    logger = helper.load_logger('Broker')
    DEC_PLACES = 8

    def __init__(self, key, secret):
        self.binance = Client(key, secret)
        if key and secret:
            self.account_stalker = AccountStalker(key, secret, self.on_order_update)

        self.account_stalkers = {}
        self.chart_stalkers = {}
        self.ticker_stalkers = {}
        self.trade_stalkers = {}
        self.ex_info = self.binance.get_exchange_info()
        self.restrictions = {}

        for reg in self.ex_info['symbols']:
            self.restrictions[reg['symbol']] = Restrictions(reg)

    def on_order_update(self, summary):
        symbol = summary['symbol']

        if symbol in self.account_stalkers:
            for cb in self.account_stalkers[symbol]:
                cb(summary)

    def register_chart_callback(self, symbol, period, zoom, func):
        hash_ = '{}{}{}'.format(symbol, period, zoom)
        if hash_ not in self.chart_stalkers:
            self.logger.info("Registering chart stalker for: {}".format({hash_}))
            self.chart_stalkers[hash_] = ChartStalker(symbol, period, zoom, False, func)
        else:
            self.logger.info("Appending  for chart stalker: {}".format({hash_}))
            self.chart_stalkers[hash_].cbs.append(func)

    def register_ticker_callback(self, symbol, func):
        if symbol not in self.ticker_stalkers:
            self.logger.info("Registering ticker stalker for: {}".format({symbol}))
            self.ticker_stalkers[symbol] = TickerStalker(symbol, func)
        else:
            self.logger.info("Appending ticker stalker callback for: {}".format({symbol}))
            self.ticker_stalkers[symbol].cbs.append(func)

    def register_trade_callback(self, symbol, func):
        if symbol not in self.trade_stalkers:
            self.logger.info("Registering trade stalker for: {}".format({symbol}))
            self.trade_stalkers[symbol] = TradeStalker(symbol, func)
        else:
            self.logger.info("Appending trade stalker callback for: {}".format({symbol}))
            self.trade_stalkers[symbol].cbs.append(func)

    def register_account_callback(self, symbol, func):
        if symbol not in self.account_stalkers:
            self.logger.info("Registering account stalker for: {}".format({symbol}))
            self.account_stalkers[symbol] = [func]
        else:
            self.logger.info("Appending account stalker callback for: {}".format({symbol}))
            self.account_stalkers[symbol].append(func)

    @helper.callstalker
    def place_limit_order(self, side, symbol, price, amount, simulation):
        step = Decimal('%.8f' % self.restrictions[symbol].step)
        tick = Decimal('%.8f' % self.restrictions[symbol].price_tick)
        amount = Decimal('%.8f' % amount)
        price = Decimal('%.8f' % price)

        amount = np.float64(amount - amount % step)
        price = np.float64(price - price % tick)

        if amount <= self.restrictions[symbol].min_amt or amount * price <= self.restrictions[symbol].min_notional:
            self.logger.debug('Restrictions not satisfied!')
            return

        order = Order(side, symbol, price, amount, simulation)

        if simulation:
            order.order_id = DataManager.next_sequence('s_fake_order_id')
            return order
        else:
            ret = self.binance.create_order(symbol=symbol,
                                            side=side,
                                            type=OrderType.LIMIT,
                                            timeInForce='GTC',
                                            price='%.8f' % price.round(self.DEC_PLACES),
                                            quantity='%.8f' % amount.round(self.DEC_PLACES))
            self.logger.debug("Create order return: {}".format(str(ret)))
            order.order_id = ret['orderId']
            return order

    @helper.callstalker
    def place_market_order(self, side, symbol, price, amount, simulation):
        pass

    @helper.callstalker
    def place_take_profit_order(self, side, symbol, stop_price, price, amount):
        pass

    @helper.callstalker
    def place_limit_take_profit_order(self, side, symbol, stop_price, price, amount):
        pass

    @helper.callstalker
    def cancel_order(self, order):
        if not order.simulation:
            ret = self.binance.cancel_order(symbol=order.symbol, orderId=order.order_id)
            self.logger.debug("Cancel order return: {}".format(str(ret)))
