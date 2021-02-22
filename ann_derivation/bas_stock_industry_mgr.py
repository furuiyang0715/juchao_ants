# bas_stock_industry 个股行业表
import configparser
import datetime
import os
import MySQLdb

cfg = os.path.join(os.path.dirname(__file__), 'ann_derivation.ini')
xgrgcfg = os.path.join(os.path.dirname(__file__), 'XGRQ.cfg')


class BasStockIndustrySQL(object):
    BasStockIndustryDic = {
        "1": """SELECT
                    id,
                    secu_code,
                    secu_market 
                FROM
                    bas_secumain 
                WHERE
                    secu_category = 1
                    """,  # 根据证券代码分类（1为A股）【目前只需要用到A股】来获取所有所需要匹配的数据
        "2": """
                select A.code as IndustryCode,
                    A.name as IndustryName,
                    B.code as SecuCode,
                    B.name as SecuAbbr
                from block A, block_code B
                where A.type = 1
                and A.id = B.bid ;
        """,
        "3": """
                SELECT
                    * 
                FROM
                    bas_stock_industry 
                WHERE
                    secu_id = {}
                    AND industry_code = "{}";
        """
    }


class BasStockIndustry(object):
    """
    id			                              bigint(20)	否	    主键
    secu_id	        bas_secumain的id	 id	  int(20)	    否		证券ID
    industry_code	主题猎手block	    code  varchar(20)	否		板块代码
    industry_name	主题猎手block	    name  varchar(200)			板块名称
    create_time		                          datetime	    否		创建时间
    update_time		                          datetime	    否		更新时间
    create_by		                          int(11)	    否		创建人
    update_by		                          int(11)	    否		更新人
    """
    def __init__(self):
        # 日志句柄
        self.__handel = None
        # 主题猎手查询数据的内存字典
        self.ls_dict = dict()
        # 读取配置文件
        self.anncfg = configparser.ConfigParser()
        self.anncfg.read(cfg)
        # 聚源db配置信息
        self.lsdbip = self.anncfg["lieshou"]["ip"]  # 数据库ip
        self.lsdbport = self.anncfg["lieshou"]["port"]  # 数据库端口
        self.lsdbuser = self.anncfg["lieshou"]["user"]  # 数据库用户
        self.lsdbpwd = self.anncfg["lieshou"]["pwd"]  # 数据库密码
        self.lsdbdefault = self.anncfg["lieshou"]["default"]  # 数据库名称
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
        self.__handel = "Bas_SI:"
        return self.__handel

    # 创建 mysql链接，返回一个链接对象，设置超时为5分钟
    def __get_conn(self, db_cfg):
        conn = MySQLdb.connect(
            host=db_cfg["ip"], port=int(db_cfg["port"]), user=db_cfg["user"], password=db_cfg["pwd"],
            db=db_cfg["default"],
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

    # 组合插入sql的语句
    def __create_sql(self, item, table, cl):
        columns = ""
        values = ""
        values2 = ""
        for key in item.keys():
            if key in cl:
                columns += "%s, " % key
                if not item[key] != 'null' and isinstance(item[key], str):
                    values += '{}, '.format(item[key])
                    v2 = "{}={},".format(key, item[key])
                else:
                    values += '"%s", ' % (str(item[key]).replace('"', "'"))
                    v2 = '%s="%s",' % (key, str(item[key]).replace('"', "'"))
                values2 += v2
        sql = "INSERT INTO " + table + ' ({})'.format(columns[:-2]) + "values " + \
              '({})'.format(values[:-2]) + "on duplicate key update " + '{};'.format(values2[:-1])
        return sql

    # 存储mysql
    def __save_item(self, sql, db_cfg):
        conn = self.__get_conn(db_cfg)
        cur = conn.cursor()
        c = False
        cur.execute(sql)
        try:
            conn.commit()
            c = True
        except Exception as e:
            conn.rollback()
            print(f"{self.handle}入库失败,原因是{e},发生回滚")
        cur.close()
        conn.close()
        return c

    # 获取主题猎手的全部a股类型的
    def get_zt_stocks(self):
        db_cfg = {
            "ip": self.lsdbip,
            "port": self.lsdbport,
            "user": self.lsdbuser,
            "pwd": self.lsdbpwd,
            "default": self.lsdbdefault
        }
        conn = self.__get_conn(db_cfg)
        sql = BasStockIndustrySQL.BasStockIndustryDic["2"]
        data_s, c = self.__select_data(conn, sql)
        if c:
            for data in data_s:
                # IndustryCode,IndustryName,SecuCode, SecuAbbr
                # ('IX880001', '农林牧渔', 'SH600097', '开创国际')
                self.ls_dict[f"{data[2]}"] = [data[0], data[1], data[3]]

    # 根据证券代码分类（1为A股）【目前只需要用到A股】来获取所有所需要匹配的数据
    def get_update_stocks(self):
        """从bas_secumain表中根据update_time更新时间获取到最新的数据，
        数据包括字段有id, secu_category为1, secu_code, secu_market根据交易所补全code前缀例如：SH600751"""
        db_cfg = {
            "ip": self.spiderdbip,
            "port": self.spiderdbport,
            "user": self.spiderdbuser,
            "pwd": self.spiderdbpwd,
            "default": self.spiderdbdefault
        }
        conn = self.__get_conn(db_cfg)
        # 获取上次的更新时间LAST_DATETIME
        # last_datetime = self.datecfg["mgr_time"]["LAST_DATETIME"]
        sql = BasStockIndustrySQL.BasStockIndustryDic["1"]
        data_s, c = self.__select_data(conn, sql)
        return data_s, c

    # 处理code代码的前缀问题
    def deal_data_s(self, data_s):
        """
        secu_id	        bas_secumain的id	 id	  int(20)	    否		证券ID
        industry_code	主题猎手block	    code  varchar(20)	否		板块代码
        industry_name	主题猎手block	    name  varchar(200)			板块名称
        """
        s_lis = list()
        for da in data_s[0]:
            s_ = dict()
            code = None
            s_["industry_code"] = None
            s_["industry_name"] = None
            s_["secu_id"] = da[0]
            # 如果市场为90则是深交SZ， 83是上交SH
            if da[2] == 90:
                code = "SZ" + str(da[1])
            elif da[2] == 83:
                code = "SH" + str(da[1])
            else:
                print(f"{self.handle}该股票代码{da[1]}属于上交深交之外的市场，暂不处理")
            if code:
                try:
                    s_["industry_code"] = self.ls_dict[f"{code}"][0]
                    s_["industry_name"] = self.ls_dict[f"{code}"][1]
                    s_lis.append(s_)
                except:
                    print(f"{self.handle}该股票代码{da[1]}没有匹配到相对应的板块")
        return s_lis

    def check_bas_stock_industry(self, s_lis):
        db_cfg = {
            "ip": self.spiderdbip,
            "port": self.spiderdbport,
            "user": self.spiderdbuser,
            "pwd": self.spiderdbpwd,
            "default": self.spiderdbdefault
        }
        conn = self.__get_conn(db_cfg)
        c_lis = list()
        for s in s_lis:
            sql = BasStockIndustrySQL.BasStockIndustryDic["3"].format(s["secu_id"], s["industry_code"])
            data_s, c = self.__select_data(conn, sql)
            if c:
                if len(data_s)  == 0:
                    c_lis.append(s)
        return c_lis

    # 存储到爬虫数据库中
    def save_bas_stock_industry(self, item_lis):
        if len(item_lis) > 0:
            table = "bas_stock_industry"
            headclounms = ["secu_id", "industry_code", "industry_name"]
            db_cfg = {
                "ip": self.spiderdbip,
                "port": self.spiderdbport,
                "user": self.spiderdbuser,
                "pwd": self.spiderdbpwd,
                "default": self.spiderdbdefault
            }
            i = True
            for item in item_lis:
                # 完成插入sql语句
                sql = self.__create_sql(item, table, headclounms)
                c = self.__save_item(sql, db_cfg)
                if not c:
                    i = False
            # return i
        print(f"{self.handle}成功存储{len(item_lis)}条数据")

    def deal_data(self):
        self.get_zt_stocks()
        data_s = self.get_update_stocks()
        s_lis = self.deal_data_s(data_s)
        c_lis = self.check_bas_stock_industry(s_lis)
        self.save_bas_stock_industry(c_lis)

    # 程序入口
    def start(self):
        # 数据处理
        print("bas_stock_industry开始执行")
        self.deal_data()


# if __name__ == "__main__":
#     bs = BasStockIndustry()
#     bs.start()