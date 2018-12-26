from abc import ABC, abstractmethod

from core.runconstants import RunConstants
from database.datamanager import DataManager
from database.abstract.persistable import PersistableObject
import common.helper as helper
from strategy.impatient import Impatient
from strategy.technicalonly import TechnicalOnly


class Run(PersistableObject):
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


class Mode(ABC):
    def __init__(self):
        # DataManager Initialization / Configuration
        config = helper.load_config('datasource.cfg')
        DataManager.host = config['host']
        DataManager.db = config['database']
        DataManager.user = config['user']
        DataManager.pw = config['password']
        DataManager.prefix = config['table_prefix']
        DataManager.init_connector(config['connector'])

        # RunConstants - used to persist things in the database (to differentiate different runs)
        run = Run(type(self).__name__)
        RunConstants.run_id = run.run_id
        RunConstants.mode = type(self).__name__

    @abstractmethod
    def start(self):
        pass

    def spawn_strategy_instance(self, strategy, info):
        if strategy == 'techinicalonly':
            return TechnicalOnly(**info)
        elif strategy == 'impatient':
            return Impatient(**info)

    @classmethod
    def init_run(cls):
        Run(cls.__name__)
