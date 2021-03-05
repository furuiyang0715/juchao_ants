# 按天校验数据库中入库的数量与网页显示是否一致
import json
import os
import random
import sys
import time
import datetime

import requests
from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from announcement.spider_configs import (
    SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB,
    R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD,
    R_SPIDER_MYSQL_DB, )
from announcement.sql_base import Connection


_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min).strftime('%Y-%m-%d')
file_name = f'/Users/furuiyang/sntdataprocess/announcement/stock_single_{_dt}.json'

_map = {
    '601399': '601268',
    '601360': '601313',
    '600010': 'B06475',
    '600029': '136054',
    '601975': '600087',
    '600267': '122427',
    '600322': '122421',
    '600352': '136206',
    '600369': '122404',
    '600748': '122362',
    '600770': '122088',
    '600801': '122188',
    '601607': '600849',
    '600963': '122257',
    '001872': '000022',
    '001914': '000043',
    '601377': '122304',
    '601688': '122388',
    '601008': '136092',
    '601238': '113009',
    '601038': '122253',
    '600011': '122008',
    '600030': '122385',
    '600035': '122378',
    '600068': '136427',
    '600098': '122157',
    '600157': '122267',
    '600185': '110030',
    '600210': '122043',
    '600226': '122254',
    '600236': '122192',
    '600256': '122102',
    '600360': '122134',
    '600376': '122377',
    '600383': '122488',
    '600518': '122354',
    '600575': '122235',
    '600635': '122112',
    '600648': '136666',
    '600657': '136294',
    '600660': '136566',
    '600743': '122370',
    '600755': '110033',
    '600765': '122104',
    '600804': '122132',
    '600823': '136303',
    '600859': '122190',
    '600869': '136317',
    '601788': '143155',
}


class JuchaoCounter(object):
    def __init__(self):
        self.api = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
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

        self._r_spider_conn = Connection(
            host=R_SPIDER_MYSQL_HOST,
            port=R_SPIDER_MYSQL_PORT,
            user=R_SPIDER_MYSQL_USER,
            password=R_SPIDER_MYSQL_PASSWORD,
            database=R_SPIDER_MYSQL_DB,
        )

    @property
    def codes_map(self):
        codes_map = {}
        sql = '''select code, OrgId from juchao_codemap; '''
        res = self._spider_conn.query(sql)
        for r in res:
            codes_map[r.get('OrgId')] = r.get("code")
        return codes_map

    def launch(self, org_id: str):
        codes_map = self.codes_map
        org_id_lst = sorted(list(codes_map.keys()))
        position = org_id_lst.index(org_id)
        print("position", position)
        for org_id in org_id_lst[position:]:
            code = codes_map.get(org_id)
            stock_str = ','.join([code, org_id])
            print(stock_str)
            self.get_count(stock_str)

    @retry(stop_max_attempt_number=3)
    def get_count(self, stock_str: str):
        time.sleep(random.randint(1, 3)/10)
        post_data = {
            'pageNum': 1,
            'pageSize': 30,
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': '',
            'stock': stock_str,
            'searchkey': '',
            'secid': '',
            'category': '',
            'trade': '',
            'seDate': '',
            'sortName': '',
            'sortType': '',
            'isHLtitle': True,
        }
        resp = requests.post(self.api, headers=self.headers, data=post_data, timeout=3)
        if resp.status_code == 200:
            text = resp.text
            py_datas = json.loads(text)
            total_ann = py_datas.get("totalAnnouncement")
            total_rec = py_datas.get("totalRecordNum")
            record = {
                "SecuCode": stock_str.split(',')[0],
                "TotalAnn": total_ann,
                "TotalRec": total_rec,
            }
            # print(record)
            # 记录单个 code 的结束
            with open(file_name, "a") as f:
                f.write(json.dumps(record)+'\n')

    def check_count_bydate(self):
        """
        根据时间去计算每天的个数
        """
        sql = '''select SecuCode, count(*) from juchao_ant2 group by AntTime ; '''

    def check_count(self):
        sql = '''select SecuCode, count(*) from juchao_ant2 group by SecuCode ; '''
        ret = self._r_spider_conn.query(sql)
        exist_map = {}
        for r in ret:
            exist_map[r.get('SecuCode')] = r.get("count(*)")

        web_map = {}
        with open(file_name, "r") as f:
            lines = f.readlines()
            for line in lines:
                r = json.loads(line)
                web_map[r.get("SecuCode")] = r.get("TotalAnn")

        no_lst = []
        big_delta_lst = []
        small_delta_lst = []

        for code in web_map:
            _count = 0
            if code in _map:
                _code = _map.get(code)
                _count = exist_map.get(_code)

            exist_num = exist_map.get(code)
            exist_num += _count

            web_num = web_map.get(code)
            if not exist_num:
                no_lst.append(code)
            elif exist_num != web_num:
                delta = web_num - exist_num
                if delta > 0:
                    big_delta_lst.append((code, delta))
                    # big_delta_lst.append(code)
                else:
                    # small_delta_lst.append((code, delta))
                    small_delta_lst.append(code)

        print(no_lst)
        print(len(no_lst))

        print(big_delta_lst)
        print(len(big_delta_lst))

        print(small_delta_lst)
        print(len(small_delta_lst))


if __name__ == '__main__':
    org_id = os.environ.get("ORG", '9900000062')
    JuchaoCounter().launch(org_id)

    JuchaoCounter().check_count()


'''
select secucode, AntTime,  AntTitle  from juchao_ant2 where SecuCode = '603056' order by AntTime desc,  AntId  desc  limit 60, 30; 
select secucode, AntTime,  AntTitle  from juchao_ant2 where SecuCode = '600340' and categoryname = '中介报告' order by AntTime desc,  AntId  desc  limit 0, 30; 
'''
