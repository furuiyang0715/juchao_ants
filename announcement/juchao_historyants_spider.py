import datetime
import logging
import os
import random
import re
import sys
import time
import pprint
import traceback
import schedule
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
        self.history_table_name = 'juchao_ant2'  # 巨潮历史公告表
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']

    @property
    def codes_map(self):
        codes_map = {}
        sql = '''select code, OrgId from juchao_codemap; '''
        res = self._spider_conn.query(sql)
        for r in res:
            codes_map[r.get('OrgId')] = r.get("code")
        return codes_map

    def process_items(self, ants: list, info: dict):
        items = []
        for ant in ants:
            item = dict()
            item['CategoryCode'] = info.get("cat_code")
            item['CategoryName'] = info.get("cat_name")
            item['SecuCode'] = ant.get('secCode')  # 无前缀
            item['SecuAbbr'] = self.partten.sub('', ant.get('secName'))
            item['AntId'] = ant.get("announcementId")
            item['AntTitle'] = ant.get("announcementTitle")
            time_stamp = ant.get("announcementTime") / 1000
            item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
            item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
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
            self._spider_conn.batch_insert(items, self.history_table_name,
                    ['SecuCode', 'AntTime', 'AntTitle', 'AntDoc'])
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
                self._spider_conn.batch_insert(items, self.history_table_name,
                                               ['SecuCode', 'AntTime', 'AntTitle', 'AntDoc'])
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

    schedule.every(2).minutes.do(task)
    while True:
        schedule.run_pending()

        time.sleep(20)
