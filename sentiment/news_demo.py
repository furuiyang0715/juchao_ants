# 对新闻事件表进行建表
sql_old = '''
CREATE TABLE `dc_ann_event_source_news_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `NewsID` bigint(20) NOT NULL COMMENT '新闻主表ID',
  `MedName` varchar(100) COLLATE utf8_bin DEFAULT NULL COMMENT '媒体名称',
  `PubTime` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `Title` varchar(500) COLLATE utf8_bin DEFAULT NULL COMMENT '标题',
  `Website` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '网址',
  `SecuCode` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',
  `EventCode` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '事件代码',
  `EventName` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '事件名称',
  `Position` tinyint(4) NOT NULL COMMENT '提及位置：1-标题,2-内容',
  `IsValid` tinyint(4) NOT NULL DEFAULT '1' COMMENT '是否有效',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`NewsID`,`SecuCode`,`EventCode`),
  KEY `k1` (`NewsID`),
  KEY `k2` (`PubTime`),
  KEY `k3` (`SecuCode`),
  KEY `k4` (`EventCode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-新闻源'; 
'''


sql_new = '''
CREATE TABLE `dc_ann_event_source_news_detail` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `news_id` bigint(20) NOT NULL COMMENT '新闻主表ID',
  `med_name` varchar(100) COLLATE utf8_bin DEFAULT NULL COMMENT '媒体名称',
  `pub_time` datetime NOT NULL COMMENT '发布时间（精确到秒）',
  `title` varchar(500) COLLATE utf8_bin DEFAULT NULL COMMENT '标题',
  `web_site` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '网址',
  `secu_code` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',    # 改为 secu_id 
  `event_code` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '事件代码',
  `event_name` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '事件名称',
  `position` tinyint(4) NOT NULL COMMENT '提及位置：1-标题,2-内容',
  `is_valid` tinyint(4) NOT NULL DEFAULT '1' COMMENT '是否有效',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `un1` (`news_id`,`secu_code`,`event_code`), 
  KEY `k1` (`news_id`),
  KEY `k2` (`pub_time`),
  KEY `k3` (`secu_code`),
  KEY `k4` (`event_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='公告舆情事件明细-新闻源'; 
'''


sl_old = '''




'''


sl_new = '''





'''
