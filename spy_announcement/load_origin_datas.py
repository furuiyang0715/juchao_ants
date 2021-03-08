import logging
from ann_configs import SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, \
    LOCAL, R_SPIDER_MYSQL_HOST, R_SPIDER_MYSQL_PORT, R_SPIDER_MYSQL_USER, R_SPIDER_MYSQL_PASSWORD, R_SPIDER_MYSQL_DB
from sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LoadOriginAnnData:
    spider_conn = PyMysqlPoolBase(
        host=SPIDER_MYSQL_HOST,
        port=SPIDER_MYSQL_PORT,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        db=SPIDER_MYSQL_DB,
    )
    if LOCAL:
        product_read_spider_conn = PyMysqlPoolBase(
            host=R_SPIDER_MYSQL_HOST,
            port=R_SPIDER_MYSQL_PORT,
            user=R_SPIDER_MYSQL_USER,
            password=R_SPIDER_MYSQL_PASSWORD,
            db=R_SPIDER_MYSQL_DB,
        )
    else:
        product_read_spider_conn = spider_conn

    category_name_code_map = {
        'category_bcgz_szsh': ('补充更正', 19),
        'category_bndbg_szsh': ('半年报', 2),
        'category_cqdq_szsh': ('澄清致歉', 12),
        'category_dshgg_szsh': ('董事会', 18),
        'category_fxts_szsh': ('风险提示', 21),
        'category_gddh_szsh': ('股东大会', 15),
        'category_gqbd_szsh': ('股权变动', 16),
        'category_gqjl_szsh': ('股权激励', 17),
        'category_gszl_szsh': ('公司治理', 24),
        'category_gszq_szsh': ('公司债', 25),
        'category_jj_szsh': ('解禁', 9),
        'category_jshgg_szsh': ('监事会', 14),
        'category_kzzq_szsh': ('可转债', 22),
        'category_ndbg_szsh': ('年报', 4),
        'category_pg_szsh': ('配股', 7),
        'category_qtrz_szsh': ('其他融资', 23),
        'category_qyfpxzcs_szsh': ('权益分派', 11),
        'category_rcjy_szsh': ('日常经营', 10),
        'category_sf_szsh': ('首发', 8),
        'category_sjdbg_szsh': ('三季报', 3),
        'category_tbclts_szsh': ('特别处理和退市', 13),
        'category_tszlq_szsh': ('退市整理期', 20),
        'category_yjdbg_szsh': ('一季报', 1),
        'category_yjygjxz_szsh': ('业绩预告', 5),
        'category_zf_szsh': ('增发', 6),
        'category_zj_szsh': ('中介报告', 26),
        'category_others': ('其他', 27),
    }
    batch_num = 10000
    fields = ['secu_codes', 'category_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime']

    def start(self):
        sql_create_table = '''
        CREATE TABLE IF NOT EXISTS `spy_announcement_data` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
          `cninfo_announcement_id` bigint(20) NOT NULL COMMENT '巨潮公告ID',
          `secu_codes` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '关联证券代码, 多个代码使用逗号(,)分隔',
          `category_codes` varchar(200) NOT NULL COMMENT '巨潮分类,多个分类代码使用(,)分隔',
          `ann_classify` tinyint(4) NOT NULL COMMENT '公告分类（1:沪深 2:港股 3:三板 4:基金 5:债券 6:监管 7:预披露）',
          `title` varchar(1000) COLLATE utf8_bin NOT NULL COMMENT '公告标题',
          `pdf_link` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '公告pdf地址',
          `pub_datetime` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
          `create_by` int(11) NOT NULL COMMENT '创建人',
          `update_by` int(11) NOT NULL COMMENT '更新人',
          `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`id`),
          UNIQUE KEY `cn_ann_id` (`cninfo_announcement_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告采集原始表' ;
        '''

        sql_create_table2 = '''
        CREATE TABLE IF NOT EXISTS `an_announcement_secu_ref` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
          `ann_id` int(20) NOT NULL COMMENT 'spy_announcement_data 表 id',
          `secu_id` int(20) NOT NULL COMMENT '公告关联证券',
          `create_by` int(11) NOT NULL COMMENT '创建人',
          `update_by` int(11) NOT NULL COMMENT '更新人',
          `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
          `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
          PRIMARY KEY (`id`), 
          UNIQUE KEY `annid_secuid` (`ann_id`, `secu_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='证券公告关联表' ;
        '''
        self.spider_conn._exec_sql(sql_create_table)
        self.spider_conn._exec_sql(sql_create_table2)

        sql_fetch_maxid = '''select max(id) from juchao_ant2 where AntTime <= '2021-02-18' ; '''
        max_id = self.product_read_spider_conn.select_one(sql_fetch_maxid).get("max(id)")
        print(max_id)

        sql_load = '''
        select id as id, 
            AntId as cninfo_announcement_id, 
            SecuCode as secu_codes, 
            CategoryCode, 
            AntTitle as title, 
            AntDoc as pdf_link, 
            AntTime as pub_datetime 
            from juchao_ant2
            where AntTime <= '2021-02-18'
            and id >= {} and id < {} ;  
        '''
        items = []
        for i in range(int(max_id / self.batch_num) + 1):
            sl = sql_load.format(i*self.batch_num, i*self.batch_num+self.batch_num)
            print(sl)
            juchao_ants_datas = self.product_read_spider_conn.select_all(sl)
            print(len(juchao_ants_datas))
            for data in juchao_ants_datas:
                if data.get('CategoryCode') == '':
                    cate_code = 27
                else:
                    try:
                        cate_code = self.category_name_code_map[data.pop('CategoryCode')][1]
                    except:
                        raise ValueError(f'{data}数据异常')
                data['category_codes'] = cate_code
                data['create_by'] = 0
                data['update_by'] = 0
                data['ann_classify'] = 1
                items.append(data)
                if len(items) > 100:
                    self.spider_conn._batch_save(items, 'spy_announcement_data', self.fields)
                    items = []

        self.spider_conn._batch_save(items, 'spy_announcement_data', self.fields)
