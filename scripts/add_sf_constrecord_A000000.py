from announcement.spider_configs import (TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_MYSQL_USER,
                                         TEST_MYSQL_PASSWORD, TEST_MYSQL_DB)
from announcement.sql_base import Connection

sql1 = '''
CREATE TABLE `sf_const_announcement` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `EventMainTypeCode` varchar(20) COLLATE utf8_bin NOT NULL COMMENT '事件所属的大类代码',
  `EventMainTypeName` varchar(50) COLLATE utf8_bin NOT NULL COMMENT '事件所属的大类名称',
  `EventCode` varchar(50) COLLATE utf8_bin NOT NULL COMMENT '事件代码',
  `EventName` varchar(100) COLLATE utf8_bin NOT NULL COMMENT '事件名称',
  `EventOneWordLabel` varchar(50) COLLATE utf8_bin DEFAULT NULL COMMENT '事件类型一字标签',
  `Sentiment` tinyint(4) NOT NULL COMMENT '情感倾向(1-正面，-1-负面，0-中性)',
  `Level` int(4) NOT NULL COMMENT '舆情级别：0为中性，负数越小，影响越利空；正数越大，影响越利多',
  `EventDayChgPerc` decimal(10,4) NOT NULL COMMENT '公告发布当日的涨跌幅',
  `EventDayWinRatio` decimal(10,4) NOT NULL COMMENT '公告发布当日的胜率',
  `NextDayWinRatio` decimal(10,4) NOT NULL COMMENT '次日胜率',
  `NextDayChgPerc` decimal(10,4) NOT NULL COMMENT '次日涨幅',
  `ThreeDayChgPerc` decimal(10,4) NOT NULL COMMENT '3日涨幅',
  `FiveDayChgPerc` decimal(10,4) NOT NULL COMMENT '5日涨幅',
  `Desc` varchar(1000) COLLATE utf8_bin DEFAULT NULL COMMENT '事件描述',
  `IfShow` tinyint(4) NOT NULL DEFAULT '1' COMMENT '软件是否展示：0-不展示，1-展示',
  `FirstLevelShowRank` int(10) DEFAULT NULL COMMENT '公告智选前端展示排序-一级事件（对应EventMainTypeCode）（一个一级事件下面对应的多个二级事件每条数据需要保证这个字段一致）',
  `SecondLevelShowRank` int(10) DEFAULT NULL COMMENT '公告智选前端展示排序-二级事件（对应EventCode）',
  `CreateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `UpdateTime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `u1` (`EventName`) USING BTREE,
  UNIQUE KEY `u2` (`EventCode`) USING BTREE,
  UNIQUE KEY `u3` (`EventMainTypeCode`,`EventCode`,`SecondLevelShowRank`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='常量表-公告事件'; 
'''

sql2 = '''
INSERT INTO sf_const_announcement (EventMainTypeCode, EventMainTypeName, EventCode, EventName, \
EventOneWordLabel, Sentiment, Level, EventDayChgPerc, EventDayWinRatio, NextDayWinRatio, NextDayChgPerc, \
ThreeDayChgPerc,FiveDayChgPerc, IfShow, FirstLevelShowRank, SecondLevelShowRank) VALUES \
('A000', '其他', 'A000000', '其他类别', '其', 0,0,  0,0,0,0,0,0, 1, 7,1);
'''

conn = Connection(
    host=TEST_MYSQL_HOST,
    port=TEST_MYSQL_PORT,
    user=TEST_MYSQL_USER,
    password=TEST_MYSQL_PASSWORD,
    database=TEST_MYSQL_DB,
)

conn.insert(sql1)
conn.insert(sql2)
