import json

import requests

from announcement.spider_configs import SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, \
    SPIDER_MYSQL_DB
from announcement.sql_base import Connection


class JuchaoHisSpiderBase(object):
    """巨潮历史公告爬虫基类"""
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

    @property
    def ant_types(self):
        return {
            'category_bcgz_szsh': '补充更正',
            'category_bndbg_szsh': '半年报',
            'category_cqdq_szsh': '澄清致歉',
            'category_dshgg_szsh': '董事会',
            'category_fxts_szsh': '风险提示',
            'category_gddh_szsh': '股东大会',
            'category_gqbd_szsh': '股权变动',
            'category_gqjl_szsh': '股权激励',
            'category_gszl_szsh': '公司治理',
            'category_gszq_szsh': '公司债',
            'category_jj_szsh': '解禁',
            'category_jshgg_szsh': '监事会',
            'category_kzzq_szsh': '可转债',
            'category_ndbg_szsh': '年报',
            'category_pg_szsh': '配股',
            'category_qtrz_szsh': '其他融资',
            'category_qyfpxzcs_szsh': '权益分派',
            'category_rcjy_szsh': '日常经营',
            'category_sf_szsh': '首发',
            'category_sjdbg_szsh': '三季报',
            'category_tbclts_szsh': '特别处理和退市',
            'category_tszlq_szsh': '退市整理期',
            'category_yjdbg_szsh': '一季报',
            'category_yjygjxz_szsh': '业绩预告',
            'category_zf_szsh': '增发',
            'category_zj_szsh': '中介报告',
        }

    def _query(self, stock_str: str = '',
               se_date: str = '',
               cat_code: str = '',
               page: int = 1,
               search_key: str = '',
               ):
        ants = []
        post_data = {
            'pageNum': page,
            'pageSize': 30,
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': '',
            'stock': stock_str,
            'searchkey': search_key,
            'secid': '',
            'category': cat_code,
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
                ants = []
            else:
                py_datas = json.loads(text)
                ants = py_datas.get("announcements")
                if ants is None:
                    ants = []
        return ants
