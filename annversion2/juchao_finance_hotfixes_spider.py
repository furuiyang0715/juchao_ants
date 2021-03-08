import datetime
import logging
import pprint

from annversion2.juchao_historyant_base import JuchaoHisSpiderBase
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JuchaoFinanceSpider(JuchaoHisSpiderBase):
    """巨潮历史公告爬虫-仅财务数据 """
    def __init__(self):
        super(JuchaoFinanceSpider, self).__init__()
        self.fields = ['SecuCode', 'SecuAbbr', 'AntId', 'AntTime', 'AntTitle', 'AntDoc']
        self.history_table_name = 'juchao_ant_finance'

    def process(self, ant: dict, info: dict):
        item = dict()
        item['SecuCode'] = ant.get('secCode')
        item['SecuAbbr'] = ant.get('secName')
        item['AntId'] = ant.get("announcementId")
        item['AntTitle'] = ant.get("announcementTitle")
        item['Category'] = info.get("category")
        time_stamp = ant.get("announcementTime") / 1000
        item.update({'AntTime': datetime.datetime.fromtimestamp(time_stamp)})
        item.update({'AntDoc': 'http://static.cninfo.com.cn/' + ant.get("adjunctUrl")})
        return item

    def start(self, start_date=None, end_date=None):
        '''网站限制 一次最多只有一年的数据'''
        self.catup_mainids()

        if end_date is None:
            end_date = datetime.datetime.today()
        if start_date is None:
            start_date = datetime.datetime.today() - datetime.timedelta(days=1)
        se_date = "{}~{}".format(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        logger.info(se_date)

        crawl_map = {}

        items = []
        for category in ('category_ndbg_szsh',    # 年报
                         'category_bndbg_szsh',   # 半年报
                         'category_yjdbg_szsh',   # 一季报
                         'category_sjdbg_szsh',   # 三季报
                         'category_yjygjxz_szsh',  # 业绩预告
                         ):
            logger.info(f"category is {category}")
            cate_count = 0
            for page in range(100):
                logger.info("page >> {}".format(page))
                ants = self._query('', se_date, category, page, '')
                cate_count += len(ants)
                if len(ants) == 0:
                    break
                for ant in ants:
                    item = self.process(ant, {"category": category})
                    logger.info(item)
                    items.append(item)
                if len(items) > 100:
                    self._spider_conn._batch_save(items, self.history_table_name, self.fields)
                    items = []
            crawl_map[category] = cate_count

        logger.info("开始爬取快报")
        cate_count = 0
        # 'category_yjkb_szsh',    # 自定义的业绩快报类型
        for page in range(100):
            logger.info("page >> {}".format(page))
            ants = self._query('', se_date, '', page, '快报')
            cate_count += len(ants)
            if len(ants) == 0:
                break
            for ant in ants:
                item = self.process(ant, {"category": 'category_yjkb_szsh'})
                logger.info(item)
                items.append(item)
            if len(items) > 100:
                self._spider_conn._batch_save(items, self.history_table_name, self.fields)
                items = []
        crawl_map['category_yjkb_szsh'] = cate_count

        self._spider_conn._batch_save(items, self.history_table_name, self.fields)
        logger.info(f'本次爬取的情况是: \n{pprint.pformat(crawl_map)}')

    def catup_mainids(self):
        sql = 'update juchao_ant_finance A inner join juchao_ant2 B on A.AntId = B.AntId \
and (A.MainID is NULL or A.CategoryCode is NULL) \
set A.MainID = B.id, A.CategoryCode = B.CategoryCode;'
        update_count = self._spider_conn._exec_sql(sql)
        logger.info(update_count)
        return update_count
