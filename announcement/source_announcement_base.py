import datetime
import logging
import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from announcement import utils
from ann_configs import R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD, \
    R_SPIDER_MYSQL_DB, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, \
    JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB
from sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SourceAnnouncementBase(object):
    """将两个爬虫表合并生成公告基础表"""
    def __init__(self):
        self.merge_table_name = 'announcement_base2'
        self.his_table = 'juchao_ant2'
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
        self._juyuan_conn = PyMysqlPoolBase(
            host=JUY_HOST,
            port=JUY_PORT,
            user=JUY_USER,
            password=JUY_PASSWD,
            db=JUY_DB,
        )

    def category_code_map(self):
        return {
         'category_bcgz_szsh': ('补充更正', 19),
         'category_bndbg_szsh': ('半年报', 2),
         'category_cqdq_szsh': ('澄清致歉', 12),
         'category_dshgg_szsh': ('董事会', 18),
         'category_fxts_szsh': ('风险提示', 21),
         'category_gddh_szsh': ('股东大会', 15),
         'category_gqbd_szsh': ('股权变动', 16),
         'category_gqjl_szsh': ('股权激励', 17),
         'category_gszl_szsh': ('公司治理', 24),
         'category_gszq_szsh': ('公司债', 25),
         'category_jj_szsh': ('解禁', 9),
         'category_jshgg_szsh': ('监事会', 14),
         'category_kzzq_szsh': ('可转债', 22),
         'category_ndbg_szsh': ('年报', 4),
         'category_pg_szsh': ('配股', 7),
         'category_qtrz_szsh': ('其他融资', 23),
         'category_qyfpxzcs_szsh': ('权益分派', 11),
         'category_rcjy_szsh': ('日常经营', 10),
         'category_sf_szsh': ('首发', 8),
         'category_sjdbg_szsh': ('三季报', 3),
         'category_tbclts_szsh': ('特别处理和退市', 13),
         'category_tszlq_szsh': ('退市整理期', 20),
         'category_yjdbg_szsh': ('一季报', 1),
         'category_yjygjxz_szsh': ('业绩预告', 5),
         'category_zf_szsh': ('增发', 6),
         'category_zj_szsh': ('中介报告', 26),
         'category_others': ('其他', 27),
         }

    def load_innercode_map(self):
        sql = '''select secucode, innercode from secumain; '''
        _map = dict()
        ret = self._juyuan_conn.select_all(sql)
        for r in ret:
            _map[r.get("secucode")] = r.get("innercode")
        return _map

    def get_old_inner_code(self, secucode: str):
        sql = '''select InnerCode from LC_CodeChange where secucode = '{}';'''.format(secucode)
        r = self._juyuan_conn.select_one(sql)
        if r:
            inner_code = r.get("InnerCode")
            return inner_code

    def daily_update(self, deadline: datetime.datetime = None):
        inner_map = self.load_innercode_map()
        category_code_map = self.category_code_map()

        if deadline is None:
            deadline = datetime.datetime.now() - datetime.timedelta(days=1)

        load_sql = '''select id, SecuCode, CategoryCode, SecuAbbr, AntTime as PubDatetime1, \
AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 from {} where \
UPDATETIMEJZ > '{}'; '''.format(self.his_table, deadline)
        logger.info(f"his load sql is {load_sql}")
        datas = self._r_spider_conn.select_all(load_sql)
        logger.info(f"load count is {len(datas)} from his table.")
        items = []
        for data in datas:
            data['CategoryCode'] = category_code_map.get(data.get("CategoryCode"))[1]
            inner_code = inner_map.get(data.get("SecuCode"))
            if inner_code:
                data['InnerCode'] = inner_code    # 爬虫库中的 secucode 无前缀
            else:
                inner_code = self.get_old_inner_code(data.get("SecuCode"))
                if inner_code:
                    inner_map.update({data.get("SecuCode"): inner_code})
                    data['InnerCode'] = inner_code
                else:
                    continue
            data = utils.process_secucode(data)  # 暂时只要 0 3 6
            if data:
                items.append(data)

        self._spider_conn._batch_save(items, self.merge_table_name,
        ['SecuCode', 'SecuAbbr', 'CategoryCode', 'PubDatetime1', 'InsertDatetime1', 'Title1', 'InnerCode'])

        update_sql = '''select A.* from juchao_kuaixun A, juchao_ant B where B.UPDATETIMEJZ > '{}' \
and A.code = B.SecuCode and A.link = B.AntDoc and A.type = '公告';  '''.format(deadline)
        logger.info(f"live sql is {update_sql}")
        datas = self._r_spider_conn.select_all(update_sql)
        logger.info(f'load count {len(datas)} from live table.')
        for data in datas:
            item = {
                'PubDatetime2': data.get("pub_date"),
                'InsertDatetime2': data.get("CREATETIMEJZ"),
                'Title2': data.get("title"),
            }
            self._spider_conn.table_update(self.merge_table_name, item, 'PDFLink', data.get("link"))
