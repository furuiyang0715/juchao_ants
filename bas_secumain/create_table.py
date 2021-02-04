# 这一块交出去了 所以不做了 啊哈哈哈哈


### 创建证券主表
'''
CREATE TABLE IF NOT EXISTS `bas_secumain` (
  `id` bigint(20) NOT NULL COMMENT '主键',
  `jy_inner_code` int(11) NOT NULL COMMENT '聚源内部编码',
  `company_code` int(11) DEFAULT NULL COMMENT '公司代码',
  `secu_code` varchar(100) NOT NULL COMMENT '股票代码',
  `chi_name` varchar(200) DEFAULT NULL COMMENT '中文名称',
  `chi_name_abbr` varchar(100) DEFAULT NULL COMMENT '中文名称缩写',
  `eng_name` varchar(200) DEFAULT NULL COMMENT '英文名称',
  `eng_name_abbr` varchar(50) DEFAULT NULL COMMENT '英文名称缩写',
  `secu_abbr` varchar(100) NOT NULL COMMENT '股票简称',
  `chi_spelling` varchar(50) DEFAULT NULL COMMENT '拼音证券简称',
  `secu_market` int(11) DEFAULT NULL COMMENT '证券市场',
  `secu_category` int(11) DEFAULT NULL COMMENT '证券类别',
  `listed_date` datetime DEFAULT NULL COMMENT '上市日期',
  `listed_sector` int(11) DEFAULT NULL COMMENT '上市板块',
  `listed_state` int(11) DEFAULT NULL COMMENT '上市状态',
  `jy_update_time` datetime NOT NULL COMMENT '聚源修改日期',
  `jy_jsid` bigint(20) NOT NULL COMMENT '聚源 JSID',
  `jy_isin` varchar(20) DEFAULT NULL COMMENT '聚源 ISIN代码',
  `industry_code` varchar(20) DEFAULT NULL COMMENT '经传行业版块代码(仅限个股)',
   UNIQUE KEY `pk_bas_secumain` (`ID`),
   UNIQUE KEY `ix_bas_secumain_jy_jsid` (`JSID`),
   UNIQUE KEY `ix_bas_secumain` (`jy_inner_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='证券主表';
'''

fields = ['secu_code', 'secu_abbr', 'jy_inner_code', 'industry_code', 'secu_type']
#### 聚源证券主表
'''
CREATE TABLE `secumain` (
  `ID` bigint(20) NOT NULL COMMENT 'ID',
  `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
  `CompanyCode` int(11) DEFAULT NULL COMMENT '公司代码',
  `SecuCode` varchar(30) DEFAULT NULL,
  `ChiName` varchar(200) DEFAULT NULL COMMENT '中文名称',
  `ChiNameAbbr` varchar(100) DEFAULT NULL COMMENT '中文名称缩写',
  `EngName` varchar(200) DEFAULT NULL COMMENT '英文名称',
  `EngNameAbbr` varchar(50) DEFAULT NULL COMMENT '英文名称缩写',
  `SecuAbbr` varchar(100) DEFAULT NULL COMMENT '证券简称',
  `ChiSpelling` varchar(50) DEFAULT NULL COMMENT '拼音证券简称',
  `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
  `SecuCategory` int(11) DEFAULT NULL COMMENT '证券类别',     # 1-A股，2-B股，3-H股，4-大盘，5-国债回购，6-国债现货，7-金融债券，8-开放式基金，9-可转换债券，10-其他，11-企业债券，12-企业债券回购，13-投资基金 
  `ListedDate` datetime DEFAULT NULL COMMENT '上市日期',
  `ListedSector` int(11) DEFAULT NULL COMMENT '上市板块',
  `ListedState` int(11) DEFAULT NULL COMMENT '上市状态',
  `XGRQ` datetime NOT NULL COMMENT '修改日期',
  `JSID` bigint(20) NOT NULL COMMENT 'JSID',
  `ISIN` varchar(20) DEFAULT NULL COMMENT 'ISIN代码',
  UNIQUE KEY `IX_SecuMain` (`InnerCode`),
  UNIQUE KEY `IX_SecuMain_JSID` (`JSID`),
  UNIQUE KEY `PK_SecuMain` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=gbk; 
'''

'''
select InnerCode as jy_inner_code, 
CompanyCode as company_code, 
SecuCode as secu_code, 
ChiName as chi_name, 
ChiNameAbbr as chi_name_abbr, 
EngName as eng_name, 
EngNameAbbr as eng_name_abbr, 
SecuAbbr as secu_abbr, 
ChiSpelling as chi_spelling, 
SecuMarket as secu_market, 
SecuCategory as secu_category, 
ListedDate as listed_date, 
ListedSector as listed_sector, 
XGRQ as jy_update_time, 
JSID as jy_jsid, 
ISIN as jy_isin 
from secumain limit 1 \G

'''


'''
# 从聚源表中获取 A 股、B 股以及基金的基础信息
select ID as id, 
InnerCode as jy_inner_code, 
SecuCode as secu_code, 
SecuAbbr as secu_abbr, 
SecuCategory as secu_type, 
SecuMarket as secu_market
from secumain
where SecuCategory in (1, 2, 13); 


'''

import sys
sys.path.append('./../')
from announcement.spider_configs import SPIDER_MYSQL_DB, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, \
    SPIDER_MYSQL_PASSWORD, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB, THE_HOST, THE_PORT, THE_USER, THE_PASSWD, \
    THE_DB
from announcement.sql_base import Connection


class BasSecuMain(object):
    spider_conn = Connection(
        host=SPIDER_MYSQL_HOST,
        port=SPIDER_MYSQL_PORT,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        database=SPIDER_MYSQL_DB,
    )

    juyuan_conn = Connection(
        host=JUY_HOST,
        port=JUY_PORT,
        user=JUY_USER,
        password=JUY_PASSWD,
        database=JUY_DB,
    )

    theme_conn = Connection(
        host=THE_HOST,
        port=THE_PORT,
        user=THE_USER,
        password=THE_PASSWD,
        database=THE_DB,
    )

    fields = ['secu_code', 'secu_abbr', 'jy_inner_code', 'industry_code', 'secu_type']
    table_name = 'bas_secumain'

    def start(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `bas_secumain` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键',
          `secu_code` varchar(100) NOT NULL COMMENT '股票代码',
          `secu_abbr` varchar(100) NOT NULL COMMENT '股票简称',
          `jy_inner_code` int(11) NOT NULL COMMENT '聚源内部编码',
          `secu_type` int(11) NOT NULL COMMENT '证券代码分类(1:A股 2:B股 3:基金)',
          `industry_code` varchar(20) DEFAULT NULL COMMENT '经传行业版块代码(仅限个股)',
          `secu_market` int(11) DEFAULT NULL COMMENT '证券市场',
          `is_delete` tinyint(1) DEFAULT 0 COMMENT '逻辑删除标志',
           UNIQUE KEY `pk_bas_secumain` (`ID`), 
           UNIQUE KEY `ix_bas_secumain` (`jy_inner_code`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='证券主表';
        '''
        self.spider_conn.execute(sql)

        industry_map = {}
        sql = '''
        select A.code as IndustryCode, 
        A.name as IndustryName, 
        B.code as SecuCode, 
        B.name as SecuAbbr 
        from block A, block_code B 
        where A.type = 1 
        and A.id = B.bid ;
        '''
        ret = self.theme_conn.query(sql)
        for r in ret:
            industry_map[r['SecuCode']] = r['IndustryCode']
        print(industry_map)

        # 全表同步
        # secumain 字段:

        # sql = '''
        # select ID as id,
        # InnerCode as jy_inner_code,
        # SecuCode as secu_code,
        # SecuAbbr as secu_abbr,
        # SecuCategory as secu_type,
        # SecuMarket as secu_market
        # from secumain
        # where SecuCategory in (1, 2, 8, 13);
        # '''
        # datas = self.juyuan_conn.query(sql)
        # for data in datas:
        #     if data['secu_type'] in (8, 13) :
        #         data['secu_type'] = 3     # 更改基金的证券分类
        #     if data['secu_market'] == 83 and data['secu_type'] in (1, 2):
        #         # 获取经传行业代码
        #         industry_code = industry_map.get("SH"+data['secu_code'])
        #     elif data['secu_market'] == 90 and data['secu_type'] in (1, 2):
        #         industry_code = industry_map.get("SZ" + data['secu_code'])
        #     else:
        #         industry_code = None
        #     data['industry_code'] = industry_code
        #     data.pop("secu_market")
        #     print(data)
        # self.spider_conn.batch_insert(datas, self.table_name, self.fields)

        # # 获取全量的 A 股
        # sql = """
        #     (
        #     select A.id, A.SecuCode, A.SecuMarket, A.InnerCode, A.SecuAbbr, A.ListedDate, B.ChangeDate '退市日期'
        #     from gildata.SecuMain A
        #     left join
        #     gildata.LC_ListStatus B
        #     on A.InnerCode = B.InnerCode
        #     and B.ChangeType = 4
        #     where
        #     A.SecuMarket in (83, 90)
        #     and A.SecuCategory in (1, 41)
        #     and A.ListedSector in (1, 2, 6, 7)
        #     and A.ListedDate <= CURDATE()
        #     )
        #     UNION
        #     (
        #     SELECT
        #     B.id, A.SecuCode, B.SecuMarket, A.InnerCode, B.SecuAbbr, A.BeginDate '启用日期', A.StopDate '停用日期'
        #     FROM gildata.LC_CodeChange A
        #     JOIN gildata.SecuMain B
        #     ON A.InnerCode = B.InnerCode
        #     AND B.SecuMarket IN (83,90)
        #     AND B.SecuCategory in (1, 41)
        #     WHERE
        #     A.CodeDefine = 1
        #     AND A.SecuCode <> B.SecuCode
        #     );
        #     """
        # datas = self.juyuan_conn.query(sql)
        # items = []
        # for data in datas:
        #     # print(data)
        #     item = {}
        #     if data['SecuMarket'] == 83:
        #         secu_code = 'SH' + data['SecuCode']
        #     elif data['SecuMarket'] == 90:
        #         secu_code = 'SZ' + data['SecuCode']
        #     else:
        #         raise
        #     industry_code = industry_map.get(secu_code)
        #     item['industry_code'] = industry_code
        #     # item['secu_code'] = data['SecuCode']
        #     item['secu_code'] = secu_code
        #     item['secu_abbr'] = data['SecuAbbr']
        #     item['jy_inner_code'] = data['InnerCode']
        #     item['secu_type'] = 1
        #     item['secu_market'] = data['SecuMarket']
        #     print(item)
        #     items.append(item)
        #
        # self.spider_conn.batch_insert(items, self.table_name, self.fields)


if __name__ == '__main__':
    BasSecuMain().start()
