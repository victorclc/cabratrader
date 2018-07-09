from database.postgres.connector import PsqlConnector
from abstract.database import PersistableObject
import common.helper as helper


class DataManager(object):
    logger = helper.load_logger('DataManager')
    config = helper.load_config('datasource.cfg')
    host = config['host']
    db = config['database']
    user = config['user']
    pw = config['password']
    prefix = config['table_prefix']
    connector = PsqlConnector(host, db, user, pw, prefix)

    @classmethod
    def persist(cls, obj):
        if not isinstance(obj, PersistableObject):
            raise (Exception, "Not a persistable object")

        conn = None
        ret = None
        try:
            conn = cls.connector.connect()
            ret = cls.connector.persist(conn, obj)
        except Exception as ex:
            cls.logger.error(ex)
        finally:
            if conn:
                conn.close()
        return ret

    @classmethod
    def execute_query(cls, query):
        conn = None
        ret = None
        try:
            conn = cls.connector.connect()
            ret = cls.connector.execute_query(conn, query)
        except Exception as ex:
            cls.logger.error(ex)
        finally:
            if conn:
                conn.close()
        return ret

    @classmethod
    def next_sequence(cls, sequence):
        conn = None
        ret = None
        try:
            conn = cls.connector.connect()
            ret = cls.connector.next_sequence(conn, sequence)
        except Exception as ex:
            cls.logger.error(ex)
        finally:
            if conn:
                conn.close()
        return ret
