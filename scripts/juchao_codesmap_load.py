# 生成一份巨潮的证券主表
import json
import time
import requests

from announcement.spider_configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
                                         SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB)
from announcement.sql_base import Connection


class JuChaoCodeMap(object):
    def __init__(self):
        self.fields = ['code', 'orgId', 'category', 'pinyin', 'zwjc']
        self.tool_table_name = 'juchao_codemap'
        self._spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )

    def create_tools_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `juchao_codemap` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `code` varchar(8) NOT NULL COMMENT '证券代码',
            `orgId` varchar(16) NOT NULL COMMENT '证券编码',
            `category` varchar(8) NOT NULL COMMENT '证券分类',
            `pinyin` varchar(10) NOT NULL COMMENT '证券中文名拼音',
            `zwjc` varchar(20) NOT NULL COMMENT '证券中文名',
            `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
            `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `orgId_code` (`orgId`, `code`),
            KEY `update_time` (`UPDATETIMEJZ`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮证券编码';
        '''
        self._spider_conn.execute(sql)

    def get_stock_json(self):
        api = 'http://www.cninfo.com.cn/new/data/szse_a_stock.json?_={}'.format(int(time.time() * 1000))
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.cninfo.com.cn',
            'Origin': 'http://uc.cninfo.com.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://uc.cninfo.com.cn/user/optionalConfig?groupId=88937',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
        }
        resp = requests.get(api, headers=headers)
        if resp and resp.status_code == 200:
            text = resp.text
            try:
                py_data = json.loads(text).get("stockList")
            except:
                print(text)
                raise Exception("resp parse error.")
            self._spider_conn.batch_insert(py_data, self.tool_table_name, self.fields)

    def start(self):
        self.create_tools_table()
        self.get_stock_json()


if __name__ == '__main__':
    JuChaoCodeMap().start()
