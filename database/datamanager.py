from database.postgres.connector import PsqlConnector
from abstract.database import PersistableObject
from itertools import cycle
import common.helper as helper


class DataManager(object):
    config = helper.load_config('datasource.cfg')
    host = config['host']
    db = config['database']
    user = config['user']
    pw = config['password']
    prefix = config['table_prefix']
    connector = PsqlConnector(host, db, user, pw, prefix)
    pool_conn = cycle(
        [connector.connect(), connector.connect(), connector.connect(), connector.connect(), connector.connect()])

    @classmethod
    def persist(cls, obj):
        if not isinstance(obj, PersistableObject):
            raise (Exception, "Not a persistable object")
        return cls.connector.persist(next(cls.pool_conn), obj)


    @classmethod
    def execute_query(cls, query):
        return cls.connector.execute_query(next(cls.pool_conn), query)

    @classmethod
    def next_sequence(cls, sequence):
        return cls.connector.next_sequence(next(cls.pool_conn), sequence)
