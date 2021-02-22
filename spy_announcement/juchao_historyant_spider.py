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
from spy_announcement.juchao_historyant_base import JuchaoHisSpiderBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JuchaoHistorySpider(JuchaoHisSpiderBase):
    """巨潮历史公告爬虫 """
    def __init__(self):
        super(JuchaoHistorySpider, self).__init__()
        self.partten = re.compile('\<.*\>')
        self.history_table_name = 'spy_announcement_data'  # 巨潮历史公告表
        self.fields = ['cninfo_announcement_id', 'secu_codes', 'category_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime']
        # self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']

    def process_items(self, ants: list, info: dict):
        items = []
        for ant in ants:
            item = dict()
            item['ann_classify'] = 1
            item['create_by'] = 0
            item['update_by'] = 0

            # item['CategoryCode'] = info.get("cat_code")
            # item['CategoryName'] = info.get("cat_name")
            item['category_codes'] = info.get("cat_code")

            # item['SecuCode'] = ant.get('secCode')  # 无前缀
            item['secu_codes'] = ant.get('secCode')  # 无前缀  目前沪深都是 1对1

            # item['SecuAbbr'] = self.partten.sub('', ant.get('secName'))
            # item['AntId'] = ant.get("announcementId")
            item['cninfo_announcement_id'] = ant.get("announcementId")

            # item['AntTitle'] = ant.get("announcementTitle")
            item['title'] = ant.get("announcementTitle")

            time_stamp = ant.get("announcementTime") / 1000
            # item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
            item.update({'pub_datetime': datetime.datetime.fromtimestamp(time_stamp)})

            # item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
            item.update({'pdf_link': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})

            # print(item)
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
            # items = self.process_items(ants, {'cat_code': 'category_others', 'cat_name': '其他'})
            items = self.process_items(ants, {'cat_code': '27', 'cat_name': '其他'})
            counts += len(items)
            self._spider_conn.batch_insert(items, self.history_table_name,
           ['secu_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime'])

        logger.info(f"无分类查询: 本次股票{stock_str}, 本次时间{start_date}-->>{end_date}, 数量: {counts}")

    @retry(stop_max_attempt_number=3)
    def query(self,
              stock_str: str = '',
              start_date: datetime.datetime = None,
              end_date: datetime.datetime = None,
              ):
        counts = 0
        count_map = {}
        detail_map = {}
        # 按照网站给出的分类查询进行查询
        for cat_code, cat_name in self.ant_types.items():
            cat_num = 0
            cat_total = []
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
                cat_num += len(items)
                cat_total.extend(items)

            count_map[cat_name] = cat_num
            detail_map[cat_code] = cat_total
            counts += cat_num

        logger.info(f"本次股票: {stock_str}, 本次时间: {start_date}-->>{end_date}, 总数量: {counts}\n, "
              f"分类明细: {pprint.pformat(count_map)}")

        # 处理 detail map 进行插入
        data_base = {}
        cate_base = {}
        for cate_code, items in detail_map.items():
            print(cate_code, len(items))
            cate_code = str(self.cat_map.get(cate_code)[1])

            for item in items:
                ann_id = item['cninfo_announcement_id']

                data_base[ann_id] = item

                exist_cate = cate_base.get(ann_id)
                current_cate = cate_code

                if exist_cate is not None:
                    ant_cate = ','.join([exist_cate, current_cate])
                    cate_base.update({ann_id: ant_cate})
                else:
                    cate_base[ann_id] = cate_code

        print(pprint.pformat(cate_base))

        # 拼接待插入数据
        iitems = []
        for ann_id, cate_info in cate_base.items():
            iitem = data_base.get(ann_id)
            iitem.update({'category_codes': cate_info})
            iitems.append(iitem)
            if len(iitems) >= 100:
                self._spider_conn.batch_insert(iitems, self.history_table_name,
                ['secu_codes', 'category_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime'])
                iitems = []

        self._spider_conn.batch_insert(iitems, self.history_table_name,
        ['secu_codes', 'category_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime'])

    def start(self, start_dt: datetime.datetime = None, end_dt: datetime.datetime = None):
        _today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)

        if not start_dt:
            start_dt = _today
        if not end_dt:
            end_dt = _today

        self.query(start_date=start_dt, end_date=end_dt)

        self.query_unconditional(start_date=start_dt, end_date=end_dt)


if __name__ == '__main__':
    # def task():
    #     try:
    #         JuchaoHistorySpider().start()
    #     except:
    #         traceback.print_exc()
    # task()
    #
    # schedule.every(2).minutes.do(task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(20)

    def run_fortest():
        JuchaoHistorySpider().start(datetime.datetime(2021, 2, 19), datetime.datetime(2021, 2, 19))

    run_fortest()
    # # test sql example: select distinct category_codes from spy_announcement_data where date(pub_datetime) = '2021-02-19' ;


'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1

sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name spy_ann --env LOCAL=0 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 \
python juchao_historyant_spider.py


sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name spy_ann --env LOCAL=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 \
python juchao_historyant_spider.py
'''
