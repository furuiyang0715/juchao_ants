import sys

from announcement.spider_configs import SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, \
    SPIDER_MYSQL_DB, R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD, \
    R_SPIDER_MYSQL_DB
from announcement.sql_base import Connection


class SpyAnnBase(object):
    spider_conn = Connection(
        host=SPIDER_MYSQL_HOST,
        port=SPIDER_MYSQL_PORT,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        database=SPIDER_MYSQL_DB,
    )

    r_spider_conn = Connection(
        host=R_SPIDER_MYSQL_HOST,
        port=R_SPIDER_MYSQL_PORT,
        user=R_SPIDER_MYSQL_USER,
        password=R_SPIDER_MYSQL_PASSWORD,
        database=R_SPIDER_MYSQL_DB,
    )

    def start(self):
        sql = '''
        CREATE TABLE `announcement_base2` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票代码',
          `InnerCode` int(11) NOT NULL DEFAULT '0',
          `SecuAbbr` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票简称',
          `CategoryCode` tinyint(4) NOT NULL COMMENT '巨潮网站分类',
          `PDFLink` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '公告pdf地址',
          `PubDatetime1` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
          `InsertDatetime1` datetime NOT NULL COMMENT '爬虫入库时间(巨潮公告速递栏目)',
          `Title1` varchar(1000) COLLATE utf8_bin NOT NULL COMMENT '巨潮公告速递栏目中的标题',
          `PubDatetime2` datetime DEFAULT NULL COMMENT '公告发布时间(巨潮快讯栏目中的时间)',
          `InsertDatetime2` datetime DEFAULT NULL COMMENT '爬虫入库时间(巨潮快递栏目)',
          `Title2` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '巨潮快讯栏目中的标题（没有则留空）',
          `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`id`),
          UNIQUE KEY `un1` (`PDFLink`),
          KEY `k1` (`SecuCode`,`CategoryCode`,`PubDatetime1`,`PubDatetime2`,`UpdateTime`),
          KEY `innercode` (`InnerCode`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告基础表' ; 
        '''

        secu_id_map = {}
        '''
        id: 19
        secu_code: 000010
        secu_abbr: 美丽生态
        jy_inner_code: 31
        secu_type: 1
        industry_code: IX880032
        secu_market: 90 
        '''
        sql = '''select id, secu_code from bas_secumain ; '''
        ret = self.spider_conn.query(sql)
        for r in ret:
            secu_id_map[r['secu_code']] = r['id']
        print(secu_id_map)

        sql = '''
        CREATE TABLE IF NOT EXISTS `spy_announcement_data` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
          `secu_id` int(20) NOT NULL COMMENT '证券ID',
          `category_code` tinyint(4) NOT NULL COMMENT '巨潮网站分类', 
          `pdf_link` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '公告pdf地址', 
          `title` varchar(1000) COLLATE utf8_bin NOT NULL COMMENT '公告标题', 
          `pub_date` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
          `create_by` int(11) NOT NULL DEFAULT 0 COMMENT '创建人',
          `update_by` int(11) NOT NULL DEFAULT 0 COMMENT '更新人',
          `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`id`), 
          UNIQUE KEY `ix_spy_announcement_data` (`pdf_link`), 
          KEY `pub_date` (`pub_date`), 
          KEY `update_time` (`update_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告采集原始表' ; 
        '''
        self.spider_conn.execute(sql)

        base_sql = '''
        select id,  
        SecuCode, 
        CategoryCode as category_code, 
        PDFLink as pdf_link, 
        Title1 as title, 
        PubDatetime1 as pub_date
        from announcement_base2 
        where id >=  {} and id < {} ;   
        '''

        maxid_sql = '''select max(id) from announcement_base2; '''
        max_id = self.r_spider_conn.get(maxid_sql).get("max(id)")
        print(max_id)    # 123787519
        fields = ['secu_id', 'category_code', 'title', 'pub_date']
        for i in range(int(max_id / 10000) + 1):
            start = i * 10000
            end = i * 10000 + 10000
            sql = base_sql.format(start, end)
            print(sql)
            datas = self.r_spider_conn.query(sql)
            for data in datas:
                data['secu_id'] = secu_id_map[data['SecuCode'][2:]]
                data.pop('SecuCode')
            save_count = self.spider_conn.batch_insert(datas, 'spy_announcement_data', fields)
            print(len(datas), ">>>", save_count)
            # sys.exit(0)


if __name__ == '__main__':
    SpyAnnBase().start()
