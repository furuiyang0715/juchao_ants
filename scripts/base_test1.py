import logging
import os
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from announcement import utils
from announcement.sql_base import Connection
from announcement.spider_configs import (
    R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD, R_SPIDER_MYSQL_DB,
    SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB,
    JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SourceAnnouncementBase(object):
    """将两个爬虫表合并生成公告基础表"""
    def __init__(self):
        self.merge_table_name = 'announcement_base2'
        self.his_table = 'juchao_ant2'
        self.live_table = 'juchao_kuaixun'
        self.batch_number = 10000

        self._r_spider_conn = Connection(
            host=R_SPIDER_MYSQL_HOST,
            port=R_SPIDER_MYSQL_PORT,
            user=R_SPIDER_MYSQL_USER,
            password=R_SPIDER_MYSQL_PASSWORD,
            database=R_SPIDER_MYSQL_DB,
        )
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

    def spider_max_id(self, table_name: str):
        sql = f'''select max(id) as max_id from {table_name}; '''
        max_id = self._r_spider_conn.get(sql).get("max_id")
        return max_id

    def check_ids(self):
        _delta = []
        max_id = self.spider_max_id(self.his_table)
        for i in range(int(max_id / self.batch_number) + 1):
            begin_id = i * self.batch_number
            end_id = i * self.batch_number + self.batch_number
            print()
            print(begin_id, end_id)
            sql1 = '''select count(id) from {} where id between {} and {}; '''.format(self.his_table, begin_id, end_id)
            sql2 = '''select count(id) from {} where id between {} and {}; '''.format(self.merge_table_name, begin_id, end_id)
            count1 = self._r_spider_conn.get(sql1).get("count(id)")
            count2 = self._r_spider_conn.get(sql2).get("count(id)")
            print(count1, count2)
            if count1 != count2:
                sl1 = '''select id from {} where id between {} and {};'''.format(self.his_table, begin_id, end_id)
                sl2 = '''select id from {} where id between {} and {};'''.format(self.merge_table_name, begin_id, end_id)
                rs1 = self._r_spider_conn.query(sl1)
                ids1 = set([r.get("id") for r in rs1])
                rs2 = self._r_spider_conn.query(sl2)
                ids2 = set([r.get("id") for r in rs2])
                print(list(ids1 - ids2))
                _delta.extend(list(ids1 - ids2))

        print(_delta)
        return _delta

    def process_diff_ids(self, diff_lst):
        diff_lst = tuple(diff_lst)
        category_code_map = self.category_code_map()
        _sql = '''select id, SecuCode, CategoryCode, SecuAbbr, AntTime as PubDatetime1, \
AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 from  {} where id in {}; '''.format(self.his_table, diff_lst)
        datas = self._r_spider_conn.query(_sql)
        print(len(datas))
        for data in datas:
            data['CategoryCode'] = category_code_map.get(data.get("CategoryCode"))[1]
            data = utils.process_secucode(data)  # 暂时只要 0 3 6
            if data:
                print(data)
                ret = self._spider_conn.table_insert(
                    self.merge_table_name, data,
                    ['SecuCode', 'SecuAbbr', 'CategoryCode', 'PubDatetime1', 'InsertDatetime1', 'Title1'])
                print(ret)

    def first_load(self):
        inner_map = self.load_innercode_map()
        category_code_map = self.category_code_map()

        load_sql = '''select id, SecuCode, CategoryCode, SecuAbbr, AntTime as PubDatetime1, \
AntTitle as Title1, AntDoc as PDFLink, CREATETIMEJZ as InsertDatetime1 from  {} where \
id >= {} and id < {}; '''
        max_id = self.spider_max_id(self.his_table)
        for i in range(int(max_id / self.batch_number) + 1):
            begin_id = i * self.batch_number
            end_id = i * self.batch_number + self.batch_number
            print(begin_id, end_id)
            _sql = load_sql.format(self.his_table, begin_id, end_id)
            print(_sql)
            datas = self._r_spider_conn.query(_sql)
            for data in datas:
                inner_code = inner_map.get(data.get("SecuCode"))
                if inner_code:
                    data['InnerCode'] = inner_code  # 爬虫库中的 secucode 无前缀
                else:
                    inner_code = self.get_old_inner_code(data.get("SecuCode"))
                    if inner_code:
                        data['InnerCode'] = inner_code
                        inner_map.update({data.get("SecuCode"): inner_code})
                    else:
                        continue

                data['CategoryCode'] = category_code_map.get(data.get("CategoryCode"))[1]
                data = utils.process_secucode(data)   # 暂时只要 0 3 6
                if data:
                    self._spider_conn.table_insert(self.merge_table_name, data,
                ['SecuCode', 'SecuAbbr', 'CategoryCode', 'PubDatetime1', 'InsertDatetime1', 'Title1', 'InnerCode'])

        # 将巨潮快讯的数据补充进去
        update_sql = '''select A.* from {} A, {} B \
where A.code = B.SecuCode and A.link = B.AntDoc and A.type = '公告' \
and A.id between {} and  {}; '''
        max_id = self.spider_max_id(self.live_table)
        for j in range(int(max_id / self.batch_number) + 1):
            begin_id = j * self.batch_number
            end_id = j * self.batch_number + self.batch_number
            print(begin_id, end_id)
            _sql = update_sql.format(self.live_table, self.his_table, begin_id, end_id)
            print(_sql)
            datas = self._r_spider_conn.query(_sql)
            for data in datas:
                item = {
                    'PubDatetime2': data.get("pub_date"),
                    'InsertDatetime2': data.get("CREATETIMEJZ"),
                    'Title2': data.get("title"),
                }
                self._spider_conn.table_update(self.merge_table_name, item, 'PDFLink', data.get("link"))

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


if __name__ == '__main__':
    SourceAnnouncementBase().first_load()
    delta_ids = SourceAnnouncementBase().check_ids()
    SourceAnnouncementBase().process_diff_ids(delta_ids)
