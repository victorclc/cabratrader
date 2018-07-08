from database.datamanager import DataManager
from abstract.database import PersistableObject


class Run(PersistableObject):
    run_id = DataManager.execute_query("SELECT run_id from c_run order by run_id desc limit 1")[0]['run_id']

    def __init__(self, mode=None):
        self.mode = mode
        DataManager.persist(self)
        res = DataManager.execute_query("SELECT run_id from c_run order by run_id desc limit 1")[0]
        self.run_id = res['run_id']

    def persistables(self):
        pers = {
            'mode': self.mode
        }
        return pers

