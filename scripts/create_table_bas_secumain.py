from spy_announcement.spider_configs import SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, \
    SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB
from spy_announcement.sql_base import Connection

sql = '''
CREATE TABLE `bas_secumain` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `secu_code` varchar(30) DEFAULT NULL COMMENT '证券代码',
  `cn_name` varchar(200) DEFAULT NULL COMMENT '证券中文名称',
  `cn_name_abbr` varchar(100) DEFAULT NULL COMMENT '证券中文名称缩写',
  `secu_abbr` varchar(100) DEFAULT NULL COMMENT '证券简称',
  `secu_market` int(11) NOT NULL DEFAULT '0' COMMENT '证券市场（83 上交所； 90 深交所；72 港交所）',
  `secu_category` int(11) DEFAULT NULL COMMENT '证券代码分类（1 A股； 2 B股； 3 基金）',
  `cn_spelling` varchar(50) DEFAULT NULL COMMENT '拼音证券简称',
  `eng_name` varchar(200) DEFAULT NULL COMMENT '英文名称',
  `eng_name_abbr` varchar(50) DEFAULT NULL COMMENT '英文名称缩写',
  `listed_date` datetime DEFAULT NULL COMMENT '上市日期',
  `listed_sector` int(11) DEFAULT NULL COMMENT '上市板块',
  `listed_state` int(11) DEFAULT NULL COMMENT '上市状态（1-上市，3-暂停，5-终止，9-其他。）',
  `delisting_date` datetime DEFAULT NULL COMMENT '退市时间',
  `juyuan_inner_code` int(11) NOT NULL COMMENT '聚源内部编码',
  `juyuan_company_code` int(11) DEFAULT NULL COMMENT '聚源公司代码',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_user` int(11) NOT NULL DEFAULT '0' COMMENT '创建用户',
  `update_user` int(11) NOT NULL DEFAULT '0' COMMENT '更新用户',
  PRIMARY KEY (`id`),
  UNIQUE KEY `s_key` (`secu_code`,`secu_market`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='证券主表'; 

'''


sql_conn = Connection(
    host=SPIDER_MYSQL_HOST,
    port=SPIDER_MYSQL_PORT,
    user=SPIDER_MYSQL_USER,
    password=SPIDER_MYSQL_PASSWORD,
    database=SPIDER_MYSQL_DB,
)


sql_conn.execute(sql)
