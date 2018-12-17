# encoding: utf-8
import json
import logging
from datetime import date, datetime

from pymongo import MongoClient
from pymongo import errors

logger = logging.getLogger('Shark Logger')


class Mongodb():
    def __init__(self, db_config, db_name=None):
        self.db_config = db_config
        if db_name is not None:
            self.db_config['database'] = db_name
        try:
            # self.conn = MongoClient(self.db_config['host'], self.db_config['port'])
            self.conn = MongoClient(self.db_config['URI'])
            self.db = self.conn.get_database(self.db_config['database'])
        except errors.ServerSelectionTimeoutError as e:
            logger.error('Connect timeout：%s' % e)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __default(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            raise TypeError('%r is not JSON serializable' % obj)

    def close_conn(self):
        self.conn.close()

    def find_one(self, table_name, condition=None):
        return self.db.get_collection(table_name).find_one(condition)

    def find_all(self, table_name, condition=None):
        return self.db.get_collection(table_name).find(condition)

    def count(self, table_name, condition=None):
        return self.db.get_collection(table_name).count(condition)

    def distinct(self, table_name, field_name):
        return self.db.get_collection(table_name).distinct(field_name)

    def insert(self, table_name, data):
        try:
            ids = self.db.get_collection(table_name).insert(data)
            return ids
        except Exception as e:
            logger.error('Insert failed：%s' % e)
            return None

    def update(self, table_name, condition, update_data, update_type='set'):
        if update_type not in ['inc', 'set', 'unset', 'push', 'pushAll', 'addToSet', 'pop', 'pull', 'pullAll',
                               'rename']:
            logger.error('Update Failed，Type Error：%s' % update_type)
            return None
        try:
            result = self.db.get_collection(table_name).update_many(condition, {'$%s' % update_type: update_data})
            logger.info(
                'Update successful，Matched count：%s；Updated count：%s' % (result.matched_count, result.modified_count))
            return result.modified_count
        except Exception as e:
            logger.error('Update failed：%s' % e)
            return None

    def remove(self, table_name, condition=None):
        result = self.db.get_collection(table_name).remove(condition)
        if result.get('err') is None:
            logger.info('Deletion successful，Deleted entries %s' % result.get('n', 0))
            return result.get('n', 0)
        else:
            logger.error('Deletion failed：%s' % result.get('err'))
            return None

    def output_row(self, table_name, condition=None, style=0):
        row = self.find_one(table_name, condition)
        if style == 0:
            max_len_key = max([len(each_key) for each_key in row.keys()])
            str_format = '{0: >%s}' % max_len_key
            keys = [str_format.format(each_key) for each_key in row.keys()]
            result = dict(zip(keys, row.values()))
            print('**********  Table Name[%s]  **********' % table_name)
            for key, item in result.items():
                print(key, ':', item)
        else:
            print(json.dumps(row, indent=4, ensure_ascii=False, default=self.__default))

    def output_rows(self, table_name, condition=None, style=0):
        rows = self.find_all(table_name, condition)
        total = self.count(table_name, condition)
        if style == 0:
            count = 0
            for row in rows:
                max_len_key = max([len(each_key) for each_key in row.keys()])
                str_format = '{0: >%s}' % max_len_key
                keys = [str_format.format(each_key) for each_key in row.keys()]
                result = dict(zip(keys, row.values()))
                count += 1
                print('**********  Table Name[%s]  [%d/%d]  **********' % (table_name, count, total))
                for key, item in result.items():
                    print(key, ':', item)
        else:
            for row in rows:
                print(json.dumps(row, indent=4, ensure_ascii=False, default=self.__default))


def save_to_mongo_db(shark_db, collection, dict):
    try:
        old_document = shark_db.find_one(collection, {'key': dict['key']})

        if old_document is None:
            _ids = shark_db.insert(collection, dict)
            print('Insertion successful')
            return _ids
        else:
            _id = old_document['_id']
            shark_db.update(collection, {'_id': _id}, dict)

            new_document = shark_db.find_one(collection, {'_id': _id});
            print('Existing document has been replaced %s', new_document['_id'])
    except Exception as db_exception:
        print(str(db_exception))
