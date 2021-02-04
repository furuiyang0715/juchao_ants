import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from announcement.spider_configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
    SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB)
from announcement.sql_base import Connection


class UpdateInnerCode(object):
    def __init__(self):
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )
        self._juyuan_conn = Connection(
            host=JUY_HOST,
            port=JUY_PORT,
            user=JUY_USER,
            password=JUY_PASSWD,
            database=JUY_DB,
        )
        self.batch_num = 10000

    def max_id(self):
        sql = '''select max(id) as max_id from announcement_base2; '''
        return self._spider_conn.get(sql).get("max_id")

    def load_innercode_map(self):
        sql = '''select secucode, innercode from secumain; '''
        _map = dict()
        ret = self._juyuan_conn.query(sql)
        for r in ret:
            _map[r.get("secucode")] = r.get("innercode")
        return _map

    def get_old_inner_code(self, secucode: str):
        sql = '''select InnerCode from LC_CodeChange where secucode = '{}';'''.format(secucode)
        r = self._juyuan_conn.get(sql)
        if r:
            inner_code = r.get("InnerCode")
            return inner_code

    def start(self, begin: int, end: int):
        inner_map = self.load_innercode_map()    # secucode 无前缀
        # max_id = self.max_id()
        # print(max_id)

        base_sql = '''select id, secucode from announcement_base2 where id between {} and {} and InnerCode = 0; '''

        for i in range(begin, end):
            sql = base_sql.format(i * self.batch_num, i * self.batch_num + self.batch_num)
            print(sql)
            datas = self._spider_conn.query(sql)
            print(len(datas))
            for data in datas:
                inner_code = inner_map.get(data.get('secucode')[2:])
                if inner_code is None:
                    inner_code = self.get_old_inner_code(data.get('secucode')[2:])
                    if inner_code is not None:
                        inner_map.update({data.get('secucode')[2:]: inner_code})
                        self._spider_conn.table_update('announcement_base2', {'InnerCode': inner_code},
                                                       "id", data.get("id"))
                else:
                    self._spider_conn.table_update('announcement_base2', {'InnerCode': inner_code},
                                                   "id", data.get("id"))


if __name__ == '__main__':
    _start = int(os.environ.get("START", 0))
    _end = int(os.environ.get("END", 4042))
    UpdateInnerCode().start(_start, _end)
