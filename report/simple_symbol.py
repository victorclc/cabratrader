import report.query as querys
from database.datamanager import DataManager


def format_list(list_):
    txt = ''
    for element in list_:
        txt += '{},'.format(element)
    else:
        txt = txt[:-1]
    return txt


symbol = 'ETHBTC'
run_id = DataManager.execute_query(querys.LAST_RUN)[0]['run_id']

res = DataManager.execute_query(querys.CYCLES_SYMBOL_RUNID.format(symbol, run_id))

successes = [d['profit'] for d in res if d['profit'] > 0.0]
losses = [d['profit'] for d in res if d['profit'] < 0.0]

print('TOTAL CYCLES: {}'.format(len(res)))
print('SUCC CYCLES: {} | PROFIT: {} | BIGGEST PROFIT: {}'.format(len(successes), sum(successes), max(successes)))
print('FAIL CYCLES: {} | LOSS: {} | BIGGEST LOSS: {}'.format(len(losses), sum(losses), min(losses)))

