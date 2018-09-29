from core.mode import Mode
from datetime import time
import common.helper as helper
from exchange.binance.broker import Broker


class CabrictorMode(Mode):
    def __init__(self):
        super().__init__()
        self.config = self.ConfigWrapper(helper.load_config('cabrictor.cfg'))
        ex_config = helper.load_config('binance.cfg')
        self.broker = Broker(ex_config['key'], ex_config['secret'])
        self.instances = []
        self.amount_per_coin = float('%.8f' % (self.config.working_amount / self.config.num_coins))

    def get_coins(self):
        raw_ticker = self.broker.binance.get_ticker()
        symbols = []

        for ticker in raw_ticker:
            if ticker['symbol'][-len(self.config.market):] == self.config.market and float(
                    ticker['quoteVolume']) >= self.config.min_volume:
                if ticker['symbol'] not in self.config.black_list:
                    symbols.append({'symbol': ticker['symbol'], 'volume': float(ticker['quoteVolume'])})

        symbols = sorted(symbols, key=lambda obj: obj['volume'])

        return [x['symbol'][:-len(self.config.market)] for x in symbols[-self.config.num_coins:]]

    def start(self):
        coins = self.get_coins()

        for coin in coins:
            symbol = coin + self.config.market
            info = {
                'broker': self.broker,
                'symbol': symbol,
                'amount': self.amount_per_coin,
                'setup': self.config.setup,
                'simulation': self.config.simulation,
                'work_start': self.config.work_start,
                'work_end': self.config.work_end
            }
            self.instances.append(self.spawn_strategy_instance(self.config.strategy, info))

    class ConfigWrapper(object):
        def __init__(self, data):
            self.market = data['market']
            self.working_amount = data['working_amount']
            self.num_coins = data['num_coins']
            self.min_volume = data['min_volume']
            self.daily_target = data['daily_target']
            self.daily_loss = data['daily_loss']
            self.work_start = time(*[int(x) for x in data['work_start'].split(':')]) if data['work_start'] else None
            self.work_end = time(*[int(x) for x in data['work_end'].split(':')]) if data['work_end'] else None
            self.simulation = data['simulation']
            self.setup = data['setup']
            self.black_list = [x + self.market for x in data['black_list']]
            self.strategy = data['strategy']
