import datetime
import json
import os
import sys

import requests

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                     SPIDER_MYSQL_DB)
from sql_base import Connection


class JuchaoHistorySpider(object):
    """巨潮历史公告爬虫 """
    def __init__(self):
        self.api = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http://www.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        }
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )
        self.history_table_name = 'juchao_ant'  # 巨潮历史公告表

    def start(self, start_date=None):
        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=1)

        end_date = datetime.datetime.today()
        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        print(se_date)

        for page in range(1000):
            print("page >> {}".format(page))
            post_data = {
                'pageNum': page,
                'pageSize': 30,
                'column': 'szse',
                'tabName': 'fulltext',
                'plate': '',
                'stock': '',
                'searchkey': '',
                'secid': '',
                'category': '',
                'trade': '',
                'seDate': se_date,
                'sortName': '',
                'sortType': '',
                'isHLtitle': True,
            }
            resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
            if resp.status_code == 200:
                text = resp.text
                if text == '':
                    break

                py_datas = json.loads(text)
                ants = py_datas.get("announcements")
                if ants is None:
                    break

                for ant in ants:
                    item = dict()
                    item['SecuCode'] = ant.get('secCode')
                    item['SecuAbbr'] = ant.get('secName')
                    item['AntId'] = ant.get("announcementId")
                    item['AntTitle'] = ant.get("announcementTitle")
                    time_stamp = ant.get("announcementTime") / 1000
                    item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
                    item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
                    print(item)
                    self._spider_conn.table_insert(self.history_table_name, item)
            else:
                print(resp)
