import datetime
import logging
import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from ann_configs import R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD, \
    R_SPIDER_MYSQL_DB, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB
from sql_pool import PyMysqlPoolBase
import utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SourceAnnouncementBaseV1(object):
    """将两个爬虫表合并生成公告基础表"""
    def __init__(self):
        self.merge_table_name = 'announcement_base'
        self.his_table = 'juchao_ant'
        self.live_table = 'juchao_kuaixun'
        self.batch_number = 10000

        self._r_spider_conn = PyMysqlPoolBase(
            host=R_SPIDER_MYSQL_HOST,
            port=R_SPIDER_MYSQL_PORT,
            user=R_SPIDER_MYSQL_USER,
            password=R_SPIDER_MYSQL_PASSWORD,
            db=R_SPIDER_MYSQL_DB,
        )
        self._spider_conn = PyMysqlPoolBase(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            db=SPIDER_MYSQL_DB,
        )

    def daily_update(self, deadline: datetime.datetime = None):
        if deadline is None:
            deadline = datetime.datetime.now() - datetime.timedelta(days=1)

        load_sql = '''select id, SecuCode, SecuAbbr, AntTime as PubDatetime1, \
AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 from {} where \
UPDATETIMEJZ > '{}'; '''.format(self.his_table, deadline)
        logger.info(load_sql)

        items = []
        datas = self._r_spider_conn.select_all(load_sql)
        logger.info(len(datas))
        for data in datas:
            data = utils.process_secucode(data)
            if data:
                items.append(data)
        self._spider_conn._batch_save(items, self.merge_table_name,
        ['SecuCode', 'SecuAbbr', 'PubDatetime1', 'InsertDatetime1', 'Title1'])

        update_sql = '''
        select A.* from juchao_kuaixun A, juchao_ant B where B.UPDATETIMEJZ > '{}' and A.code = B.SecuCode \
and A.link = B.AntDoc and A.type = '公告';  '''.format(deadline)
        datas = self._r_spider_conn.select_all(update_sql)
        for data in datas:
            item = {
                'PubDatetime2': data.get("pub_date"),
                'InsertDatetime2': data.get("CREATETIMEJZ"),
                'Title2': data.get("title"),
            }
            self._spider_conn.table_update(self.merge_table_name, item, 'PDFLink', data.get("link"))
