## 项目说明 
爬取巨潮网站的各类公告数据并进行数据整和


## 股票公告 
### 数据源 
#### 巨潮快讯 
- 网站数据源：http://www.cninfo.com.cn/new/commonUrl/quickNews?url=/disclosure/quickNews&queryDate=2021-01-12
- 爬取逻辑文件：announcement/juchao_livenews_spider.py
- 入库表名以及结构:
```sql
CREATE TABLE IF NOT EXISTS `juchao_kuaixun` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `code` varchar(8) DEFAULT NULL COMMENT '证券代码',
    `name` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '证券简称', 
    `pub_date` datetime NOT NULL COMMENT '发布时间',
    `title` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
    `type` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯类别',
    `link` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
    `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
    `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `date_title` (`pub_date`, `title`),
    KEY `pub_date` (`pub_date`),
    KEY `update_time` (`UPDATETIMEJZ`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮快讯'; 
```
其中快讯的全部类型有: 公告、通知、调研、互动、其他。后续只取公告的部分。
发布时间为快讯的发布时间, 精确到秒。
爬虫定时频率: 10min/次

#### 巨潮历史数据查询 
- 网站数据源: http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index
- 爬取逻辑文件: announcement/juchao_historyants_spider.py
- 入库表名以及结构:
```sql
CREATE TABLE IF NOT EXISTS `juchao_ant2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CategoryCode` varchar(32) NOT NULL COMMENT '分类代码',
  `CategoryName` varchar(32) NOT NULL COMMENT '分类名称',
  `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
  `SecuAbbr` varchar(16) NOT NULL COMMENT '证券简称',
  `AntId` int(20) NOT NULL COMMENT '巨潮自带公告 ID',
  `AntTime` datetime NOT NULL COMMENT '发布时间',
  `AntTitle` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
  `AntDoc` varchar(1000) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ant_id` (`AntId`),
  KEY `ant_time` (`AntTime`),
  KEY `secucode` (`SecuCode`),
  KEY `update_time` (`UPDATETIMEJZ`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮历史公告' ; 
```

#### 巨潮历史公告财务部分查询 
- 网站数据源：http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index 
- 爬取逻辑文件: announcement/juchao_finance_hotfixes_spider.py 
- 入库表名以及结构: 
```sql
 CREATE TABLE `juchao_ant_finance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
  `SecuAbbr` varchar(16) NOT NULL COMMENT '证券代码',
  `Category` varchar(32) NOT NULL COMMENT '财报类型',
  `AntId` int(20) NOT NULL COMMENT '巨潮自带公告 ID',
  `AntTime` datetime NOT NULL COMMENT '发布时间',
  `AntTitle` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '资讯标题',
  `AntDoc` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `MainID` bigint(20) unsigned DEFAULT NULL,
  `CategoryCode` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ant_id` (`AntId`),
  KEY `ant_time` (`AntTime`),
  KEY `secucode` (`SecuCode`),
  KEY `update_time` (`UPDATETIMEJZ`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股财务类公告' ; 
```

其中 MainID、CategoryCode 是与主表 juchao_ant2 的关联字段。 表示该条记录在主表中的 id 和分类。 

### base 基础表 
```sql
CREATE TABLE IF NOT EXISTS `juchao_ant2` (
    `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
    `SecuCode` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票代码',
    `SecuAbbr` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票简称',
    `CategoryCode` TINYINT NOT NULL COMMENT '巨潮网站分类',
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
    KEY `k1` (`SecuCode`, `CategoryCode`, `PubDatetime1`,`PubDatetime2`,`UpdateTime`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告基础表'; 
```



### 改版后爬虫表数据库[最新]
