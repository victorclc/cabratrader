from binance.client import Client
from database.datamanager import DataManager
import common.helper as helper
from exchange.binance.models import BinanceChartData

DataManager.host = 'cabra'
DataManager.db = 'cabratrader'
DataManager.user = 'cabra'
DataManager.pw = 'cabra'
DataManager.prefix = 'c'
DataManager.init_connector('postgres')

logger = helper.load_logger('lixo')

results = DataManager.execute_query(
    "select cycle_id from c_cycle where status = 'COMPLETED' and run_id >= 23 order by cycle_id")

cycles_to_analyze = [x['cycle_id'] for x in results]

for cycle in cycles_to_analyze:
    results = DataManager.execute_query(
        'select * from c_order where cycle_id = {} and exec_amount > 0.0 order by ref_date'.format(cycle))
    start = results[0]['ref_date']
    end = results[-1]['ref_date']
    profit = DataManager.execute_query("select * from c_cycle where cycle_id = {}".format(cycle))[0]['profit_perc']
    logger.info("{}; {}; {}; {}; {}".format(cycle, start, end, end - start, profit))
