### 巨潮快讯 
#### 建表 
```shell script
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
#### 位置 
annversion2/juchao_livenews_spider.py


### 巨潮财务 
##### 建表
```shell script
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
#### 位置
annversion2/juchao_finance_hotfixes_spider.py


### 巨潮历史数据原始表2 
#### 建表 
```shell script
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
#### 位置
annversion2/juchao_historyants_spider.py


### 巨潮合并表2 
#### 建表
```shell script
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告基础表'; 
```
#### 位置
annversion2/juchao_historyant_base.py 


### 巨潮历史数据原始表1 
#### 建表 
```shell script
CREATE TABLE `juchao_ant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `SecuCode` varchar(8) NOT NULL COMMENT '证券代码',
  `SecuAbbr` varchar(16) NOT NULL COMMENT '证券代码',
  `AntId` int(20) NOT NULL COMMENT '巨潮自带公告 ID',
  `AntTime` datetime NOT NULL COMMENT '发布时间',
  `AntTitle` varchar(512) DEFAULT NULL,
  `AntDoc` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '公告详情页链接',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ant_id` (`AntId`),
  KEY `ant_time` (`AntTime`),
  KEY `secucode` (`SecuCode`),
  KEY `update_time` (`UPDATETIMEJZ`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巨潮个股公告关联'; 
```
#### 位置
annversion1/his1.py 


### 巨潮合并数据表1 
#### 建表 
```shell script
CREATE TABLE `announcement_base` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `SecuCode` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票代码',
  `SecuAbbr` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '股票简称',
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
  KEY `k1` (`SecuCode`,`PubDatetime1`,`PubDatetime2`,`UpdateTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告基础表'; 
```
#### 位置
annversion1/base1.py


### 新版网站原始表
#### 建表 
```shell script
CREATE TABLE `spy_announcement_data` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `cninfo_announcement_id` bigint(20) NOT NULL COMMENT '巨潮公告ID',
  `secu_codes` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '关联证券代码, 多个代码使用逗号(,)分隔',
  `category_codes` varchar(200) COLLATE utf8_bin NOT NULL COMMENT '巨潮分类,多个分类代码使用(,)分隔',
  `ann_classify` tinyint(4) NOT NULL COMMENT '公告分类（1:沪深 2:港股 3:三板 4:基金 5:债券 6:监管 7:预披露）',
  `title` varchar(1000) COLLATE utf8_bin NOT NULL COMMENT '公告标题',
  `pdf_link` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '公告pdf地址',
  `pub_datetime` datetime NOT NULL COMMENT '公告发布时间(巨潮公告速递栏目中的时间)',
  `create_by` int(11) NOT NULL COMMENT '创建人',
  `update_by` int(11) NOT NULL COMMENT '更新人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `cn_ann_id` (`cninfo_announcement_id`),
  KEY `update_time` (`update_time`),
  KEY `pub_datetime` (`pub_datetime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='公告采集原始表'; 
```
#### 位置
spy_announcement/juchao_historyant_spider.py 


### 新版关联表
#### 建表
```shell script
CREATE TABLE `an_announcement_secu_ref` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `ann_id` int(20) NOT NULL COMMENT 'spy_announcement_data 表 id',
  `secu_id` int(20) NOT NULL COMMENT '公告关联证券',
  `create_by` int(11) NOT NULL COMMENT '创建人',
  `update_by` int(11) NOT NULL COMMENT '更新人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `annid_secuid` (`ann_id`,`secu_id`)
) ENGINE=InnoDB AUTO_INCREMENT=51831696 DEFAULT CHARSET=utf8 COLLATE=utf8_bin ROW_FORMAT=DYNAMIC COMMENT='证券公告关联表'; 
```
#### 位置 
spy_announcement/ann_secu_ref_generator.py 
