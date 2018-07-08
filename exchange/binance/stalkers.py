from exchange.binance.models import BinanceChartData, BinanceTicker, BinanceTradeStream
from binance.websockets import BinanceSocketManager
from binance.client import Client
import common.helper as helper
import numpy as np
import requests
import time


class OrderUpdate(object):
    EVENT_TYPE = 'e'
    EVENT_TIME = 'E'
    SYMBOL = 's'
    CLIENT_ORDER_ID = 'c'
    SIDE = 'S'
    ORDER_TYPE = 'o'
    TIME_IN_FORCE = 'f'
    ORDER_QUANTITY = 'q'
    ORDER_PRICE = 'p'
    STOP_PRICE = 'P'
    ICEBERG_QUANTITY = 'F'
    ORIGINAL_CLIENT_ORDER_ID = 'C'
    EXEC_TYPE = 'x'
    ORDER_STATUS = 'X'
    REJECT_REASON = 'r'
    ORDER_ID = 'i'
    LAST_EXEC_QTY = 'l'
    CUMULATIVE_FILLED_QTY = 'z'
    LAST_EXEC_PRICE = 'L'
    FEE = 'n'
    FEE_ASSET = 'N'


class ChartStalker(object):
    def __init__(self, symbol, period, zoom, quantic=False, cb=None):
        self.symbol = symbol
        self.ksize = period
        self.zoom = zoom
        self.period = period
        self.quantic = quantic
        self.cbs = []
        if cb:
            self.cbs.append(cb)
        self.conn_key = None
        self.raw_chart = self.get_chart()
        self.bm = BinanceSocketManager(None)
        self.start()

    def get_chart(self):
        start = int(time.time() - helper.config2seconds(self.zoom)) * 1000
        period = self.period

        ret = requests.get("https://api.binance.com/api/v1/klines?symbol=%s&interval=%s&startTime=%d" % (self.symbol,
                                                                                                         period,
                                                                                                         start)).json()

        return ret

    def update_candle(self, msg):
        if not self.quantic and not msg['k']['x']:
            return

        candle = [msg['k']['t'], msg['k']['o'], msg['k']['h'], msg['k']['l'], msg['k']['c'], msg['k']['v'],
                  msg['k']['T'], msg['k']['v'], msg['k']['n'], msg['k']['V'], msg['k']['Q']]

        if msg['k']['x']:
            self.raw_chart = self.raw_chart[1:]

            if self.raw_chart[-1][0] == candle[0]:
                self.raw_chart[-1] = candle
            else:
                self.raw_chart.append(candle)
            for cb in self.cbs:
                cb(BinanceChartData(self.raw_chart))
        elif self.quantic:
            if self.raw_chart[-1][0] == candle[0]:
                self.raw_chart[-1] = candle
            else:
                self.raw_chart.append(candle)
            for cb in self.cbs:
                cb(BinanceChartData(self.raw_chart))

    def stop(self):
        self.bm.stop_socket(self.conn_key)

    def start(self):
        self.conn_key = self.bm.start_kline_socket(self.symbol, self.update_candle, self.ksize)
        self.bm.start()


class AccountStalker(object):

    def __init__(self, key, secret, cb=None):
        client = Client(key, secret)
        self.bm = BinanceSocketManager(client)
        self.cbs = []
        if cb:
            self.cbs.append(cb)
        self.bm.start_user_socket(self.update_order)
        self.bm.start()
        self.orders = {}

    def update_order(self, msg):
        if msg[OrderUpdate.EVENT_TYPE] != 'executionReport':
            return

        number = msg[OrderUpdate.ORDER_ID]

        if number not in self.orders:
            self.orders[number] = []

        self.orders[number].append(msg)

        self.wrap_info_and_send(self.orders[number])

        if msg[OrderUpdate.ORDER_STATUS] == 'FILLED' or msg[OrderUpdate.ORDER_STATUS] == 'CANCELED':
            self.orders.pop(number)

    def wrap_info_and_send(self, order):
        amount = np.float64(0)
        avg_price = np.float64(0)
        total = np.float64(0)
        fee = np.float64(0)
        fee_asset = ""
        active = True
        symbol = ""
        order_id = None
        ref_date = 0
        reg_count = 0

        for reg in order:
            if reg[OrderUpdate.EXEC_TYPE] not in ['TRADE', 'CANCELED']:
                continue

            if reg[OrderUpdate.EXEC_TYPE] == 'TRADE':
                reg_count += 1

            order_id = reg[OrderUpdate.ORDER_ID]
            symbol = reg[OrderUpdate.SYMBOL]
            amount += np.float64(reg[OrderUpdate.LAST_EXEC_QTY])
            avg_price += np.float64(reg[OrderUpdate.LAST_EXEC_PRICE])
            total += np.float64(reg[OrderUpdate.LAST_EXEC_QTY]) * np.float64(reg[OrderUpdate.LAST_EXEC_PRICE])
            fee += np.float64(reg[OrderUpdate.FEE])
            if not fee_asset:
                fee_asset = reg[OrderUpdate.FEE_ASSET]
            ref_date = reg[OrderUpdate.EVENT_TIME]

            if reg[OrderUpdate.ORDER_STATUS] == 'FILLED' or reg[OrderUpdate.ORDER_STATUS] == 'CANCELED':
                active = False

        if reg_count > 0:
            avg_price /= reg_count

        if fee_asset and fee_asset == symbol[-len(fee_asset):]:
            net_total = total - fee
        else:
            # Tax com desconto usando outro MARKET, porem vou subtrair o valor equivalente dessa moeda no market atual
            # para facilitar visualizacao
            net_total = total * (1 - 0.05 / 100)  # Usando bnb, taxa = 0.05 por transacao

        summary = {
            'symbol': symbol,
            'order_id': order_id,
            'exec_amount': amount,
            'gross_total': total,
            'net_total': net_total,
            'fee_asset': str(fee_asset),
            'avg_price': avg_price,
            'fee': fee,
            'active': active,
            'ref_date': int(ref_date / 1000)
        }

        for cb in self.cbs:
            cb(summary)


class TickerStalker(object):
    def __init__(self, symbol, cb=None):
        self.symbol = symbol
        self.bm = BinanceSocketManager(None)
        self.conn_key = self.bm.start_symbol_ticker_socket(symbol, self.update_ticker)
        self.cbs = []
        if cb:
            self.cbs.append(cb)

        self.bm.start()

    def update_ticker(self, msg):
        for cb in self.cbs:
            cb(BinanceTicker.init_web_socket(msg))

    def stop(self):
        self.bm.stop_socket(self.conn_key)
        self.conn_key = None


class TradeStalker(object):
    def __init__(self, symbol, cb=None):
        self.symbol = symbol
        self.bm = BinanceSocketManager(None)
        self.conn_key = self.bm.start_trade_socket(self.symbol, self.update)
        self.cbs = []
        if cb:
            self.cbs.append(cb)

        self.bm.start()

    def update(self, msg):
        for cb in self.cbs:
            cb(BinanceTradeStream.init_web_socket(msg))

    def stop(self):
        self.bm.stop_socket(self.conn_key)
        self.conn_key = None
