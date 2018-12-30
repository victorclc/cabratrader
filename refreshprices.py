"""
    Refreshes c_ticker table with the latest symbol/prices information,
    this table is used to 'rank' the coins (big, medium, small) for statistics sake
"""
import common.helper as helper
from database.datamanager import DataManager
from binance.client import Client
from datetime import datetime

config = helper.load_config('datasource.cfg')
DataManager.host = config['host']
DataManager.db = config['database']
DataManager.user = config['user']
DataManager.pw = config['password']
DataManager.prefix = config['table_prefix']
DataManager.init_connector(config['connector'])

binance = Client(None, None)
tickers = binance.get_all_tickers()
now = int(datetime.utcnow().timestamp())

if tickers:
    DataManager.execute_query('DELETE FROM c_ticker')

for ticker in tickers:
    DataManager.execute_query(
        "INSERT INTO c_ticker VALUES ('{}', {}, to_timestamp({}))".format(ticker['symbol'], ticker['price'], now))
