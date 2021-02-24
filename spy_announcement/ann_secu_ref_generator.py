# 生成公告-证券关联表
import logging
import sys

sys.path.append('./../')

from spy_announcement.spider_configs import R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, \
    R_SPIDER_MYSQL_PASSWORD, R_SPIDER_MYSQL_DB, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, \
    SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB
from spy_announcement.sql_base import Connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AnnSecuRef(object):

    def __init__(self):
        self.read_spider_conn = Connection(
            host=R_SPIDER_MYSQL_HOST,
            port=R_SPIDER_MYSQL_PORT,
            user=R_SPIDER_MYSQL_USER,
            password=R_SPIDER_MYSQL_PASSWORD,
            database=R_SPIDER_MYSQL_DB,
        )

        self.spider_conn = Connection(
            host=SPIDER_MYSQL_HOST,
            port=SPIDER_MYSQL_PORT,
            user=SPIDER_MYSQL_USER,
            password=SPIDER_MYSQL_PASSWORD,
            database=SPIDER_MYSQL_DB,
        )

        self.juyuan_conn = Connection(
            host=JUY_HOST,
            port=JUY_PORT,
            user=JUY_USER,
            password=JUY_PASSWD,
            database=JUY_DB,
        )

        self.batch_count = 10000

    def fetch_bas_secumain(self) -> dict:
        # 将 bas_secumain 的全部数据加载到内存中
        bas_sql = '''select id, secu_code from bas_secumain; '''
        bas_datas = self.read_spider_conn.query(bas_sql)
        bas_map = {}
        for data in bas_datas:
            bas_map[data['secu_code']] = data['id']
        return bas_map

    def update_rename_codes(self, bas_map: dict) -> dict:
        # 扩充映射 新增改名的部分
        sql_fetch_raname_secucodes = '''
                   SELECT A.SecuCode 'old_code', B.SecuCode 'new_code',
                   A.*
                   FROM gildata.LC_CodeChange A 
                   JOIN gildata.SecuMain B ON A.InnerCode = B.InnerCode AND B.SecuMarket IN (83,90) AND B.SecuCategory = 1
                   WHERE A.CodeDefine = 1 
                   AND A.SecuCode <> B.SecuCode
                   ORDER BY A.StopDate; 
               '''
        rename_datas = self.juyuan_conn.query(sql_fetch_raname_secucodes)
        for rename_data in rename_datas:
            new_code = rename_data['new_code']
            secu_id = bas_map[new_code]
            old_code = rename_data['old_code']
            bas_map.update({old_code: secu_id})
        return bas_map

    def get_max_spyid(self):
        # 获取爬虫表中目前的最大 id
        sql_get_maxid = '''select max(id) from spy_announcement_data; '''
        max_id = self.read_spider_conn.get(sql_get_maxid).get("max(id)")
        return max_id

    def diff_ids(self):
        # 对比两张表的 id 只取差值部分
        sql = '''select id from spy_announcement_data ; '''
        ret = self.read_spider_conn.query(sql)
        spy_ids = set([r.get("id") for r in ret])

        sql = '''select ann_id from an_announcement_secu_ref; '''
        ret = self.spider_conn.query(sql)
        ref_ids = set([r.get("ann_id") for r in ret])

        diff_ids = spy_ids - ref_ids
        print(diff_ids)

        pass

    def process(self):
        bas_map = self.fetch_bas_secumain()

        bas_map = self.update_rename_codes(bas_map)

        # # test
        # for old_code in ('600018', '600849', '601313', '000022', '000043'):
        #     print(bas_map[old_code])

        max_id = self.get_max_spyid()
        logger.info(f'Now max(id) of spy_announcement_data is {max_id}')

        codes_notfound = set()
        items = []
        for i in range(int(max_id / self.batch_count) + 1):
            _start = i * self.batch_count
            _end = i * self.batch_count + self.batch_count
            sql = f'''select id, secu_codes from spy_announcement_data where id >= {_start} and id < {_end}; '''
            origin_ann_datas = self.read_spider_conn.query(sql)
            for origin_data in origin_ann_datas:
                item = dict()
                item['ann_id'] = origin_data['id']
                secu_codes = origin_data['secu_codes']    # 对于沪深公告来说 目前secu_codes只有一个
                secu_id = bas_map.get(secu_codes)
                if secu_id is None:
                    print(secu_codes)
                    codes_notfound.add(secu_codes)
                    continue
                item['secu_id'] = secu_id
                item['create_by'] = 0
                item['update_by'] = 0
                items.append(item)
                if len(items) > 10000:
                    count = self.spider_conn.batch_insert(items, 'an_announcement_secu_ref', ['secu_id', ])
                    logger.debug(count)
                    items = []
        self.spider_conn.batch_insert(items, 'an_announcement_secu_ref', ['secu_id', ])
        logger.warning(f'未匹配证券代码: {codes_notfound}')


if __name__ == '__main__':
    AnnSecuRef().process()

    # AnnSecuRef().diff_ids()
