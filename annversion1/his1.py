import datetime
import logging
import random
import pprint
import re
import time
from retrying import retry
from annversion2.juchao_historyant_base import JuchaoHisSpiderBase

logger = logging.getLogger(__name__)


class JuchaoHistorySpiderV1(JuchaoHisSpiderBase):
    """巨潮历史公告爬虫 """
    def __init__(self):
        super(JuchaoHistorySpiderV1, self).__init__()
        self.partten = re.compile('\<.*\>')
        self.history_table_name = 'juchao_ant'  # 巨潮历史公告表
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']

    def process_items(self, ants: list):
        items = []
        for ant in ants:
            item = dict()
            # item['CategoryCode'] = cat_code
            # item['CategoryName'] = cat_name
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
    def query(self,
              stock_str: str = '',
              start_date: datetime.datetime = None,
              end_date: datetime.datetime = None):
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
                items = self.process_items(ants)
                self._spider_conn._batch_save(items, self.history_table_name,
                    ['SecuCode', 'SecuAbbr', 'AntTime', 'AntTitle', 'AntDoc'])
                cat_num += len(items)
            count_map[cat_name] = cat_num
            counts += cat_num
        logger.info(f"本次股票: {stock_str}, 本次时间: {start_date}-->>{end_date}, 总数量: {counts}\n, "
              f"分类明细: {pprint.pformat(count_map)}")

    @retry(stop_max_attempt_number=3)
    def query_unconditional(self,
                            stock_str: str = '',
                            start_date: datetime.datetime = None,
                            end_date: datetime.datetime = None):
        counts = 0
        if not start_date and not end_date:
            se_date = ''
        else:
            se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        for page in range(1, 100):
            ants = self._query(stock_str=stock_str, se_date=se_date, cat_code='', page=page, search_key='')
            if len(ants) == 0:
                break
            items = self.process_items(ants)
            self._spider_conn._batch_save(items, self.history_table_name,
                                           ['SecuCode', 'AntTime', 'AntTitle', 'AntDoc'])
        logger.info(f"无分类查询: 本次股票{stock_str}, 本次时间{start_date}-->>{end_date}, 数量: {counts}")

    def start(self, start_dt: datetime.datetime = None, end_dt: datetime.datetime = None):
        _today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        if start_dt is None:
            start_dt = _today
        if end_dt is None:
            end_dt = _today
        self.query(start_date=start_dt, end_date=end_dt)
        self.query_unconditional(start_date=start_dt, end_date=end_dt)
