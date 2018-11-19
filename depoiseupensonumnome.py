from binance.client import Client
from database.datamanager import DataManager
import common.helper as helper
from exchange.binance.models import BinanceChartData

config = helper.load_config('datasource.cfg')
DataManager.host = config['host']
DataManager.db = config['database']
DataManager.user = config['user']
DataManager.pw = config['password']
DataManager.prefix = config['table_prefix']
DataManager.init_connector(config['connector'])

symbol = 'ETCBTC'
period = '5m'
begin_date = '01 Oct, 2018'
end_date = '01 Nov, 2018'
client = Client(None, None)
klines = client.get_historical_klines(symbol, period, begin_date, end_date)
chart = BinanceChartData(klines)

create = """
CREATE TABLE IF NOT EXISTS chart_{}_{}(
  date timestamp,
  high decimal,
  low decimal,
  open decimal,
  close decimal,
  volume decimal,
  quote_volume decimal
);
""".format(symbol, period)
DataManager.execute_query(create)

delete = "delete from chart_{}_{} where date between '{}' and '{}';".format(symbol, period, begin_date, end_date)
DataManager.execute_query(delete)

for candle in chart:
    insert = "INSERT INTO chart_{}_{} VALUES ".format(symbol, period)
    insert += '(to_timestamp({}), {}, {}, {}, {}, {}, {});'.format(int(candle['date'] / 1000), candle['high'],
                                                                   candle['low'], candle['open'],
                                                                   candle['close'], candle['volume'],
                                                                   candle['quote_volume'])
    DataManager.execute_query(insert)
