import datetime
import functools
import logging
import os
import random
import re
import sys
import time
import pprint
import traceback

from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)
from announcement.juchao_historyant_base import JuchaoHisSpiderBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JuchaoHistorySpider(JuchaoHisSpiderBase):
    """巨潮历史公告爬虫 """
    def __init__(self):
        super(JuchaoHistorySpider, self).__init__()
        self.partten = re.compile('\<.*\>')
        self.table_name = 'spy_announcement_data'
        self.fields = ['secu_id', 'category_code', 'title', 'pub_date']

    @functools.cached_property
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

    @functools.cached_property
    def secu_id_map(self):
        print("* " * 1000)
        sql = '''select * from  bas_secumain where secu_type = 1 ; '''
        secu_id_map = {}
        ret = self._spider_conn.query(sql)
        for r in ret:
            secu_id_map[r['secu_code'][2:]] = r['id']
        return secu_id_map

    def process_items(self, ants: list, info: dict):
        items = []
        for ant in ants:
            item = dict()
            try:
                category_code = self.category_code_map.get(info.get("cat_code"))[1]
            except:
                raise ValueError(f"出现未知分类{info.get('cat_code')}")
            item['category_code'] = category_code
            secu_code = ant.get('secCode')
            secu_id = self.secu_id_map.get(secu_code)
            if secu_id is None:
                logger.warning(f'{secu_code} 不是 A 股 ')
                continue
            item['secu_id'] = secu_id
            item['title'] = ant.get("announcementTitle")
            item.update({'pdf_link': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
            time_stamp = ant.get("announcementTime") / 1000
            item.update({'pub_date': datetime.datetime.fromtimestamp(time_stamp)})
            print(item)
            items.append(item)
        return items

    @retry(stop_max_attempt_number=3)
    def query_unconditional(self,
                            stock_str: str = '',
                            start_date: datetime.datetime = None,
                            end_date: datetime.datetime = None,
                            ):
        counts = 0
        if not start_date and not end_date:
            se_date = ''
        else:
            se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        for page in range(1, 100):
            ants = self._query(stock_str=stock_str, se_date=se_date, cat_code='', page=page, search_key='')
            if len(ants) == 0:
                break
            items = self.process_items(ants, {'cat_code': 'category_others', 'cat_name': '其他'})
            counts += len(items)
            self._spider_conn.batch_insert(items, self.table_name, ['secu_id', 'title', 'pub_date'])
        logger.info(f"无分类查询: 本次股票{stock_str}, 本次时间{start_date}-->>{end_date}, 数量: {counts}")

    @retry(stop_max_attempt_number=3)
    def query(self,
              stock_str: str = '',
              start_date: datetime.datetime = None,
              end_date: datetime.datetime = None,
              ):
        counts = 0
        count_map = {}
        for cat_code, cat_name in self.ant_types.items():
            cat_num = 0
            time.sleep(random.randint(1, 3)/10)
            if not start_date and not end_date:
                se_date = ''
            else:
                se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            for page in range(1, 100):
                ants = self._query(stock_str=stock_str, se_date=se_date, cat_code=cat_code, page=page, search_key='')
                if len(ants) == 0:
                    break
                items = self.process_items(ants, {'cat_code': cat_code, 'cat_name': cat_name})
                self._spider_conn.batch_insert(items, self.table_name, self.fields)    # ['secu_id', 'category_code', 'title', 'pub_date']
                cat_num += len(items)

            count_map[cat_name] = cat_num
            counts += cat_num
        logger.info(f"本次股票: {stock_str}, 本次时间: {start_date}-->>{end_date}, 总数量: {counts}\n, "
              f"分类明细: {pprint.pformat(count_map)}")

    def start(self, start_dt: datetime.datetime = None, end_dt: datetime.datetime = None):
        _today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)

        if not start_dt:
            start_dt = _today
        if not end_dt:
            end_dt = _today

        self.query(start_date=start_dt, end_date=end_dt)
        self.query_unconditional(start_date=start_dt, end_date=end_dt)


if __name__ == '__main__':
    def task():
        try:
            JuchaoHistorySpider().start()
        except:
            traceback.print_exc()
    task()
