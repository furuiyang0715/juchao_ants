import datetime
import os
import sys
import time

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from configs import (SPIDER_MYSQL_HOST2, SPIDER_MYSQL_PORT2, SPIDER_MYSQL_USER2, SPIDER_MYSQL_PASSWORD2,
                     SPIDER_MYSQL_DB2, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
                     SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB)
from sql_base import Connection
from spiders import utils


class SourceAnnouncementBase(object):
    """将两个爬虫表合并生成公告基础表"""
    def __init__(self):
        self.merge_table_name = 'announcement_base'
        self.batch_number = 1000

        self._r_spider_conn = Connection(
            host=SPIDER_MYSQL_HOST2,
            port=SPIDER_MYSQL_PORT2,
            user=SPIDER_MYSQL_USER2,
            password=SPIDER_MYSQL_PASSWORD2,
            database=SPIDER_MYSQL_DB2,
        )
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )

    def launch(self):
        deadline = datetime.datetime.now() - datetime.timedelta(hours=24)

        load_sql = '''select id, SecuCode, SecuAbbr, AntTime as PubDatetime1, AntTitle as Title1, \
AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 from juchao_ant where UPDATETIMEJZ > '{}'; '''.format(deadline)

        datas = self._r_spider_conn.query(load_sql)
        datas = [utils.process_secucode(data) for data in datas]
        datas = [data for data in datas if data is not None]
        for data in datas:
            self._spider_conn.table_insert(self.merge_table_name, data)

        update_sql = '''select A.* from juchao_kuaixun A, juchao_ant B where A.pub_date > '{}' \
and A.code = B.SecuCode and A.link = B.AntDoc and A.type = '公告';  '''.format(deadline)
        datas = self._r_spider_conn.query(update_sql)

        for data in datas:
            item = {
                'PubDatetime2': data.get("pub_date"),
                'InsertDatetime2': data.get("CREATETIMEJZ"),
                'Title2': data.get("title"),
            }
            print(item)
            self._spider_conn.table_update(self.merge_table_name, item, 'PDFLink', data.get("link"))


if __name__ == '__main__':
    while True:
        jc_merge = SourceAnnouncementBase()
        jc_merge.launch()
        time.sleep(600)
