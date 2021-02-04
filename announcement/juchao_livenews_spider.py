import datetime
import json
import logging
import os
import sys
import time
import traceback
import requests
import schedule
from retrying import retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from announcement.spider_configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
                                         SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, JUY_HOST, JUY_PORT,
                                         JUY_USER, JUY_PASSWD, JUY_DB)
from announcement.sql_base import Connection


class JuchaoLiveNewsSpider(object):
    """巨潮快讯爬虫"""
    def __init__(self):
        self.web_url = 'http://www.cninfo.com.cn/new/commonUrl/quickNews?url=/disclosure/quickNews&queryDate=2020-08-13'
        self.api_url = 'http://www.cninfo.com.cn/new/quickNews/queryQuickNews?queryDate={}&type='
        self.fields = ['code', 'name', 'link', 'title', 'type', 'pub_date']
        self.table_name = 'juchao_kuaixun'
        self.name = '巨潮快讯'
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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }

    def get_secu_abbr(self, code):
        """
        从聚源数据库获取证券代码对应的中文简称
        :param code: 无前缀的证券代码
        :return:
        """
        sql = f'''select SecuAbbr from secumain where secucode=%s;'''
        name = self._juyuan_conn.get(sql, code).get("SecuAbbr")
        return name

    def get_redit_link(self, link):
        """获取最终重定向后的网址"""
        resp = self.my_get(link)
        redit_list = resp.history
        try:
            redit_link = redit_list[len(redit_list) - 1].headers["location"]
        except IndexError:
            redit_link = link
        except:
            return None
        return redit_link

    @retry(stop_max_attempt_number=5)
    def my_get(self, link):
        # 请求 超时\被ban 时重试
        logger.debug(f'get in {link} .. ')
        resp = requests.get(link, headers=self.headers, timeout=5)
        return resp

    def parse(self, url: str, day_string: str):
        items = []
        resp = self.my_get(url)
        if resp and resp.status_code == 200:
            text = resp.text
            datas = json.loads(text)
            if not datas:
                print("{} 无公告数据".format(url))
            else:
                for data in datas:
                    item = {}
                    # 需要保存的字段: 快讯的发布详细时间、类型、标题、地址、股票代码、股票名称
                    announcementTime = time.localtime(int(data.get("announcementTime") / 1000))
                    announcementTime = time.strftime("%Y-%m-%d %H:%M:%S", announcementTime)
                    item['pub_date'] = announcementTime
                    item['type'] = data.get("type")
                    item['title'] = data.get("title")
                    page_path = data.get("pagePath")
                    if page_path is None:
                        link = '''http://www.cninfo.com.cn/new/disclosure/detail?stock=&announcementId={}&announcementTime={}'''.format(
                            data.get("textId"), day_string)
                    else:
                        try:
                            link = self.get_redit_link(page_path)
                        except:
                            link = None
                    if not link:
                        continue
                    item['link'] = link
                    code = data.get("code")
                    if code:
                        item['code'] = code  # 无前缀的证券代码
                        item['name'] = self.get_secu_abbr(code)
                        items.append(item)
        return items

    def start(self, start_dt: datetime.datetime = None, end_dt: datetime.datetime = None):
        """启动入口"""
        # 使用传入的结束时间否则置为今天
        if end_dt is not None:
            end_dt = datetime.datetime.combine(end_dt, datetime.time.min)
        else:
            end_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)

        # 使用传入的开始时间 否则置为结束时间之前 3 天
        if start_dt is not None:
            start_dt = datetime.datetime.combine(start_dt, datetime.time.min)
        else:
            start_dt = end_dt - datetime.timedelta(days=3)

        # 从结束时间向前 按天 遍历到开始时间 遍历列表包含起止时间
        this_day = end_dt
        while this_day >= start_dt:
            day_string = this_day.strftime("%Y-%m-%d")
            items = self.parse(self.api_url.format(day_string), day_string)
            logger.info(f"{day_string}, {len(items)}")
            self._spider_conn.batch_insert(items, self.table_name, self.fields)
            this_day -= datetime.timedelta(days=1)
            time.sleep(3)


if __name__ == '__main__':
    def task():
        try:
            JuchaoLiveNewsSpider().start()
        except:
            traceback.print_exc()

    task()

    schedule.every(10).minutes.do(task)
    while True:
        schedule.run_pending()
        time.sleep(20)
