# 创建公告采集原始表
from spy_announcement.spider_configs import SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, \
    SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB
from spy_announcement.sql_base import Connection

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

fields = ['secu_codes', 'category_codes', 'ann_classify', 'title', 'pdf_link', 'pub_datetime']

spider_conn = Connection(
    host=SPIDER_MYSQL_HOST,
    port=SPIDER_MYSQL_PORT,
    user=SPIDER_MYSQL_USER,
    password=SPIDER_MYSQL_PASSWORD,
    database=SPIDER_MYSQL_DB,
)

spider_conn.execute(sql_create_table)


# 创建证券公告关联表 an_announcement_secu_ref
# 目前是 1 对 1 的关系
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

spider_conn.execute(sql_create_table2)


'''
mysql> select * from juchao_ant2 limit 1 \G 
*************************** 1. row ***************************
          id: 1
CategoryCode: category_bndbg_szsh
CategoryName: 半年报
    SecuCode: 002054
    SecuAbbr: 德美化工
       AntId: 18056499
     AntTime: 2006-08-19 06:15:30
    AntTitle: 德美化工2006年度中期报告摘要
      AntDoc: http://static.cninfo.com.cn/finalpage/2006-08-19/18056499.PDF
CREATETIMEJZ: 2020-12-06 06:43:12
UPDATETIMEJZ: 2020-12-06 06:43:12
1 row in set (0.03 sec)
'''

'''
id 为自增的公告 ID, 暂时采用 juchao_ant2 的 ID

cninfo_announcement_id 为巨潮公告 ID, 使用 AntId 字段 

secu_codes 关联证券代码, 即导入部分暂时是从 SecuCode 中获取 

category_codes 巨潮分类.导入部分是暂时从 CategoryCode 中获取 

ann_classify 公告分类 目前只有 1 沪深 

title 公告标题 使用 AntTitle 字段 

pdf_link 公告链接 使用 AntDoc 字段

pub_datetime 公告发布时间 使用 AntTime 字段 

.... 其余默认字段 
'''


'''
{
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
mysql> select * from juchao_ant2 limit 1 \G
*************************** 1. row ***************************
          id: 1
CategoryCode: category_bndbg_szsh
CategoryName: 半年报
    SecuCode: 002054
    SecuAbbr: 德美化工
       AntId: 18056499
     AntTime: 2006-08-19 06:15:30
    AntTitle: 德美化工2006年度中期报告摘要
      AntDoc: http://static.cninfo.com.cn/finalpage/2006-08-19/18056499.PDF
CREATETIMEJZ: 2020-12-06 06:43:12
UPDATETIMEJZ: 2020-12-06 06:43:12


select id ad id, 
AntId as cninfo_announcement_id, 
SecuCode as secu_codes, 
CategoryCode, 
AntTitle as title, 
AntDoc as pdf_link, 
AntTime as pub_datetime 
from juchao_ant2; 


{
id: 1, 
cninfo_announcement_id: 18056499, 
secu_codes: 002054, 
category_codes: 2, 
ann_classify: 1,
title: 德美化工2006年度中期报告摘要, 
pdf_link: http://static.cninfo.com.cn/finalpage/2006-08-19/18056499.PDF, 
pub_datetime: 2006-08-19 06:15:30, 
create_by: 0, 
update_by: 0, 

}
'''
