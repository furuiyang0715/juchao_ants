# 生成公告-证券关联表
from spy_announcement.spider_configs import R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, \
    R_SPIDER_MYSQL_PASSWORD, R_SPIDER_MYSQL_DB, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, \
    SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB
from spy_announcement.sql_base import Connection


class AnnSecuRef(object):

    read_spider_conn = Connection(
        host=R_SPIDER_MYSQL_HOST,
        port=R_SPIDER_MYSQL_PORT,
        user=R_SPIDER_MYSQL_USER,
        password=R_SPIDER_MYSQL_PASSWORD,
        database=R_SPIDER_MYSQL_DB,
    )

    spider_conn = Connection(
        host=SPIDER_MYSQL_HOST,
        port=SPIDER_MYSQL_PORT,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        database=SPIDER_MYSQL_DB,
    )

    def start(self):
        # 将 bas_secumain 的全部数据加载到内存中
        bas_sql = '''select id, secu_code from bas_secumain; '''
        bas_datas = self.read_spider_conn.query(bas_sql)
        bas_map = {}
        for data in bas_datas:
            bas_map[data['secu_code']] = data['id']

        sql_get_maxid = '''select max(id) from spy_announcement_data; '''
        max_id = self.read_spider_conn.get(sql_get_maxid).get("max(id)")
        print(max_id)

        codes_notfound = set()
        items = []
        for i in range(int(max_id / 10000) + 1):
            _start = i * 10000
            _end = i * 10000 + 10000
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
                    # raise ValueError
                item['secu_id'] = secu_id
                item['create_by'] = 0
                item['update_by'] = 0
                items.append(item)
                if len(items) > 10000:
                    count = self.spider_conn.batch_insert(items, 'an_announcement_secu_ref', ['secu_id', ])
                    print(count)
                    items = []
        self.spider_conn.batch_insert(items, 'an_announcement_secu_ref', ['secu_id', ])
        print(codes_notfound)


if __name__ == '__main__':
    AnnSecuRef().start()
