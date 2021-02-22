# bas_secumain 证券主表
import configparser
import datetime
import logging
import os
import pprint

import MySQLdb

from ann_derivation.sql_base import Connection

cfg = os.path.join(os.path.dirname(__file__), 'ann_derivation.ini')
xgrgcfg = os.path.join(os.path.dirname(__file__), 'XGRQ.cfg')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SecuMainSQL(object):
    """
    secuMainSQLDic 字典类型，存储从聚源获取数据的sql语句：
    1： A股（包含科创板）、B股、债券
    2： 港股
    3： 基金
    """
    secuMainSQLDic = {
        "1": """
                SELECT
                    A.InnerCode,# 证券内部编码
                    A.CompanyCode,# 公司代码
                    A.SecuCode,# 证券代码
                    A.SecuAbbr,# 证券简称
                    A.ChiSpelling,# 拼音证券简称
                    A.ChiName,# 中文名称
                    A.ChiNameAbbr,# 中文名称缩写
                    A.EngName,# 英文名称
                    A.EngNameAbbr,# 英文名称缩写
                    A.SecuMarket,# 证券市场
                    A.SecuCategory,# 证券类别
                    A.ListedDate,# 上市日期
                    A.ListedSector,# 上市板块
                    A.ListedState,# 上市状态
                    B.ChangeDate DelistingDate, # 退市日期
                    A.XGRQ,# 修改时间
                    B.XGRQ XGRQ_B # 修改时间
                FROM
                    gildata.SecuMain A
                    LEFT JOIN gildata.LC_ListStatus B ON A.InnerCode = B.InnerCode 
                    AND B.ChangeType = 4 
                WHERE
                    A.SecuMarket IN ( 83, 90 ) 
                    AND A.SecuCategory IN (1,2,6,7,9,11,28,29,41)
                    AND (A.XGRQ >= '{}' or B.XGRQ >= '{}');
            """,
        "2": """
                SELECT
                    InnerCode,# 证券内部编码
                    CompanyCode,# 公司代码
                    SecuCode,# 证券代码
                    SecuAbbr,# 证券简称
                    ChiSpelling,# 拼音证券简称
                    ChiName,# 中文名称
                    ChiNameAbbr,# 中文名称缩写
                    EngName,# 英文名称
                    EngNameAbbr,# 英文名称缩写
                    SecuMarket,# 证券市场
                    SecuCategory,# 证券类别
                    ListedDate,# 上市日期
                    ListedSector,# 上市板块
                    ListedState,# 上市状态
                    DelistingDate,# 退市日期
                    XGRQ # 修改时间
                FROM
                    gildata.HK_SecuMain 
                WHERE
                    SecuMarket = 72 
                    AND SecuCategory IN ( 3, 51, 52, 53, 71 )
                    AND XGRQ >= '{}';
        """,
        "3": """
            SELECT
                A.InnerCode,# 证券内部编码
                A.CompanyCode,# 公司代码
                A.SecuCode,# 证券代码
                A.SecuAbbr,# 证券简称
                A.ChiSpelling,# 拼音证券简称
                A.ChiName,# 中文名称
                A.ChiNameAbbr,# 中文名称缩写
                A.EngName,# 英文名称
                A.EngNameAbbr,# 英文名称缩写
                A.SecuMarket,# 证券市场
                A.SecuCategory,# 证券类别
                A.ListedDate,# 上市日期
                A.ListedSector,# 上市板块
                A.ListedState,# 上市状态
                B.ChangeDate DelistingDate,# 退市日期
                A.XGRQ,# 修改时间
                B.XGRQ XGRQ_B 
            FROM
                gildata.SecuMain A
                LEFT JOIN gildata.LC_ListStatus B ON A.InnerCode = B.InnerCode 
                AND B.ChangeType = 4 
            WHERE
                A.SecuCategory IN ( 8, 13 ) 
                AND (A.XGRQ >= '{}' OR B.XGRQ >= '{}')
        """
    }


class BasSecumainMgr(object):
    """
    此类主要对bas_secumain 证券主表的处理
    字段名              对应表名+对应字段                           字段类型    是否为空   键        字段名称
    id			      （自增）                                   bigint(20)	  否	主键
    secu_code	        聚源SecuMain	SecuCode	               varchar(30)			          证券代码
    cn_name	            聚源SecuMain	ChiName	                    varchar(30)			          证券中文名称
    cn_name_abbr	    聚源SecuMain	ChiNameAbbr	                varchar(30)			          证券中文名称缩写
    secu_abbr	        聚源SecuMain	SecuAbbr	                varchar(100)		          证券简称
    secu_market	        聚源SecuMain	SecuMarket	                int(11)			              证券市场（83 上交所；90 深交所； 72 港交所）
    secu_category	    聚源SecuMain	SecuCategory	            int(11)			              证券代码分类（1-A股，2-B股，4-大盘，5-国债回购，6-国债现货，7-金融债券，8-开放式基金，9-可转换债券，10-其他，11-企业债券，12-企业债券回购，13-投资基金，14-央行票据，15-深市代理沪市股票，16-沪市代理深市股票，17-资产支持证券，18-资产证券化产品，19-买断式回购，20-衍生权证，21-股本权证，23-商业银行定期存款，24-其他股票，26-收益增长线，27-新质押式回购，28-地方政府债，29-可交换公司债，30-拆借，31-信用风险缓释工具，32-浮息债计息基准利率，33-定期存款凭证，35-大额存款凭证，36-债券借贷，37-存款类机构质押式回购，38-存款类机构信用拆借，39-现货，40-货币对，41-中国存托凭证，42-协议回购，43-三方回购，44-利率互换品种，45-标准利率互换合约，46-报价回购，55-优先股。）
    cn_spelling	        聚源SecuMain	ChiSpelling	                varchar(50)			          拼音证券简称
    eng_name	        聚源SecuMain	EngName	                    varchar(200)		          英文名称
    eng_name_abbr	    聚源SecuMain	EngNameAbbr	                varchar(50)			          英文名称缩写
    listed_date	        聚源SecuMain	ListedDate	                datetime			          上市日期
    listed_sector	    聚源SecuMain	ListedSector	            int(11)			              上市板块（1-主板，2-中小企业板，3-三板，4-其他，5-大宗交易系统，6-创业板，7-科创板，101-纳斯达克全球精选市场（NASDAQ-GS），102-纳斯达克全球市场（NASDAQ-GM），103-纳斯达克资本市场（NASDAQ-CM），201-伦交所主板，202-伦交所主板-高级市场，203-伦交所主板-标准市场，204-伦交所主板-高增长市场，205-伦交所主板-高科技市场，210-伦交所另类投资市场，220-伦交所专家证券市场，230-伦交所专家基金市场，240-伦交所环球板(GES)。）
    listed_state	    聚源SecuMain	ListedState	                int(11)			              上市状态（1-上市，3-暂停，5-终止，9-其他。）
    delisting_date	    聚源ListState/HK_SecuMain DelistingDate	datetime			退市时间
    juyuan_inner_code	聚源SecuMain	InnerCode	                int(11)	      否	          聚源内部编码
    juyuan_company_code	聚源SecuMain	CompanyCode	                int(11)	      否	          聚源公司代码
    create_time		   （自增）                                   datetime	  否	          创建时间
    update_time		   （自增）                                   datetime	  否	          更新时间
    create_by		   （自增）                                   int(11)	  否	          创建人
    update_by		   （自增）                                   int(11)	  否	          更新人
    """
    def __init__(self):
        # 日志句柄
        self.__handel = None
        # 读取配置文件
        self.anncfg = configparser.ConfigParser()
        self.anncfg.read(cfg)
        # 聚源db配置信息
        self.jydbip = self.anncfg["juyuan"]["ip"]  # 数据库ip
        self.jydbport = self.anncfg["juyuan"]["port"]  # 数据库端口
        self.jydbuser = self.anncfg["juyuan"]["user"]  # 数据库用户
        self.jydbpwd = self.anncfg["juyuan"]["pwd"]  # 数据库密码
        self.jydbdefault = self.anncfg["juyuan"]["default"]  # 数据库名称
        # 获取记录的更新时间（每次更新以上次记录的更新时间往后查询）初始时间为 LAST_DATETIME = 2005-01-01 00:00:00 在XGRG.cfg中配置
        self.datecfg = configparser.ConfigParser()
        self.datecfg.read(xgrgcfg)
        # 爬虫db配置信息
        self.spiderdbip = self.anncfg["spider"]["ip"]  # 数据库ip
        self.spiderdbport = self.anncfg["spider"]["port"]  # 数据库端口
        self.spiderdbuser = self.anncfg["spider"]["user"]  # 数据库用户
        self.spiderdbpwd = self.anncfg["spider"]["pwd"]  # 数据库密码
        self.spiderdbdefault = self.anncfg["spider"]["default"]  # 数据库名称

    @property
    def handle(self):
        self.__handel = "Bas_SecuMian:"
        return self.__handel

    # 创建 mysql链接，返回一个链接对象，设置超时为5分钟
    def __get_conn(self, db_cfg):
        conn = MySQLdb.connect(
            host=db_cfg["ip"], port=int(db_cfg["port"]), user=db_cfg["user"], password=db_cfg["pwd"], db=db_cfg["default"],
            charset='utf8', compress=True, read_timeout=300)
        return conn

    # 查询mysql
    def __select_data(self, conn, sql):
        trs = ()
        c = True
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            trs = cursor.fetchall()
        except Exception as e:
            print(f"{self.handle}拉取数据失败：{e},其中sql语句为：{sql}, 第{e.__traceback__.tb_lineno}行发生错误")
            c = False
        return trs, c

    # # 组合插入sql的语句
    # def __create_sql(self, item, table, cl):
    #     columns = ""
    #     values = ""
    #     values2 = ""
    #     for key in item.keys():
    #         if key in cl:
    #             columns += "%s, " % key
    #             if not item[key] != 'null' and isinstance(item[key], str):
    #                 values += '{}, '.format(item[key])
    #                 v2 = "{}={},".format(key, item[key])
    #             else:
    #                 values += '"%s", ' % (str(item[key]).replace('"', "'"))
    #                 v2 = '%s="%s",' % (key, str(item[key]).replace('"', "'"))
    #             values2 += v2
    #     sql = "INSERT INTO " + table + ' ({})'.format(columns[:-2]) + "values " + \
    #           '({})'.format(values[:-2]) + "on duplicate key update " + '{};'.format(values2[:-1])
    #     return sql

    # # 存储mysql
    # def __save_item(self, sql, db_cfg):
    #     conn = self.__get_conn(db_cfg)
    #     cur = conn.cursor()
    #     c = False
    #     cur.execute(sql)
    #     try:
    #         conn.commit()
    #         c = True
    #     except Exception as e:
    #         conn.rollback()
    #         print(f"{self.handle}入库失败,原因是{e},发生回滚")
    #     cur.close()
    #     conn.close()
    #     return c

    # 从聚源的SECUMAIN中获取对应字段
    def gain_basic_data(self, category, last_datetime):
        # 1、链接聚源数据库
        db_cfg = {
            "ip": self.jydbip,
            "port": self.jydbport,
            "user": self.jydbuser,
            "pwd": self.jydbpwd,
            "default": self.jydbdefault
        }
        conn = self.__get_conn(db_cfg)
        # 2、根据sql语句获取数据(1,2,3）类型
        jy_sql = SecuMainSQL.secuMainSQLDic[category].format(last_datetime, last_datetime)
        logger.info(jy_sql)
        data_s, c = self.__select_data(conn, jy_sql)
        return data_s, c

    # # 对特殊字段做处理
    # def deal_special_field(self, data_s):
    #     item_lis = list()
    #     for data in data_s:
    #         item = dict()
    #         item["juyuan_inner_code"] = data[0]
    #         item["juyuan_company_code"] = data[1] if data[1] is not None else "null"
    #         item["secu_code"] = data[2] if data[2] is not None else "null"
    #         item["secu_abbr"] = data[3] if data[3] is not None else "null"
    #         item["cn_spelling"] = data[4] if data[4] is not None else "null"
    #         item["cn_name"] = data[5] if data[5] is not None else "null"
    #         item["cn_name_abbr"] = data[6] if data[6] is not None else "null"
    #         item["eng_name"] = data[7] if data[7] is not None else "null"
    #         item["eng_name_abbr"] = data[8] if data[8] is not None else "null"
    #         item["secu_market"] = data[9] if data[9] is not None else 0
    #         item["secu_category"] = data[10] if data[10] is not None else "null"
    #         item["listed_date"] = data[11] if data[11] is not None else "null"
    #         item["listed_sector"] = data[12] if data[12] is not None else "null"
    #         item["listed_state"] = data[13] if data[13] is not None else "null"
    #         item["delisting_date"] = data[14] if data[14] is not None else "null"
    #         item_lis.append(item)
    #     return item_lis

    # # 存储到爬虫数据库中
    # def save_bas_secumain(self, item_lis):
    #     table = "bas_secumain"
    #     headclounms = ["juyuan_inner_code", "juyuan_company_code", "secu_code", "secu_abbr", "cn_spelling", "cn_name",
    #                    "cn_name_abbr", "eng_name", "eng_name_abbr", "secu_market", "secu_category", "listed_date",
    #                    "listed_sector", "listed_state", "delisting_date"]
    #     db_cfg = {
    #         "ip": self.spiderdbip,
    #         "port": self.spiderdbport,
    #         "user": self.spiderdbuser,
    #         "pwd": self.spiderdbpwd,
    #         "default": self.spiderdbdefault
    #     }
    #     i = True
    #     for item in item_lis:
    #         # 完成插入sql语句
    #         sql = self.__create_sql(item, table, headclounms)
    #         c = self.__save_item(sql, db_cfg)
    #         if not c:
    #             i = False
    #     return i

    def save_bas_secumain(self, item_lis):
        headclounms = ["juyuan_inner_code", "juyuan_company_code", "secu_code", "secu_abbr", "cn_spelling", "cn_name",
                       "cn_name_abbr", "eng_name", "eng_name_abbr", "secu_market", "secu_category", "listed_date",
                       "listed_sector", "listed_state", "delisting_date"]

        items = [dict(zip(headclounms, item)) for item in item_lis]

        for item in items:
            if item['secu_market'] is None:
                item['secu_market'] = 0

        spider_conn = Connection(
            host=self.spiderdbip,
            database=self.spiderdbdefault,
            user=self.spiderdbuser,
            password=self.spiderdbpwd,
            port=int(self.spiderdbport),
        )

        ret = spider_conn.batch_insert(items, "bas_secumain", headclounms)
        return ret

    # 数据处理
    def deal_data(self):
        i = False
        # 获取上次的更新时间LAST_DATETIME
        last_datetime = self.datecfg["mgr_time"]["LAST_DATETIME"]
        logger.info(f'上次的更新时间LAST_DATETIME{last_datetime}')
        # 1、从聚源的SECUMAIN中获取对应字段(1,2,3)类型
        for category in SecuMainSQL.secuMainSQLDic.keys():
            data_s, c = self.gain_basic_data(category, last_datetime)
            if c:
                if len(data_s) > 0:
                    # 2、对特殊字段做处理
                    # item_lis = self.deal_special_field(data_s)
                    item_lis = data_s
                    print(len(item_lis))

                    # FIXME 较为耗时
                    # 3、存储到爬虫数据库bas_secumain中
                    i = self.save_bas_secumain(item_lis)
                else:
                    print(f"{self.handle}查询聚源数据为空集")
        # 4、存储成功后，更新LAST_DATETIME时间
        if i:
            endtime = datetime.datetime.now().strftime("%Y-%m-%d")
            self.datecfg.set("mgr_time", "LAST_DATETIME", endtime)
            self.datecfg.write(open(xgrgcfg, "w"))

    # 程序入口
    def start(self):
        # 数据处理
        logger.info("bas_secumain_mgr开始执行")
        self.deal_data()


if __name__ == "__main__":
    BSM = BasSecumainMgr()
    BSM.start()
