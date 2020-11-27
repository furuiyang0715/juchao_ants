"""
财报事件计算程序
"""

# from jznlpmodel.nlputils import  sqltool,connect
# mysql_obj_juyuan = sqltool.MysqlConnection(connect.jy_condict, name='annfinancial')


def eventcode_recognize(secucode,year,oritype):
    """
    :param secucode:股票代码（例如600000,688001），不区分是否科创板
    :param year: 财报年份（列如2020）
    :param oritype: 聚源原始公告分类 （例如1）  【对应巨潮公告类型：1-一季报，2-半年报，3-三季报，4-年报】
    :return: 精确公告类别代码，和sf_const_announcement中的EventCode相对应（如A001001）
    """
    assert oritype in (1, 2, 3, 4), 'oritype字段只能是1,2,3,4其中之一'
    assert len(secucode) == 6, 'secucode字段是长度为6的字符串'

    enddate_d = {1: '03-31',
                 2: '06-30',
                 3: '09-30',
                 4: '12-31',
                }

    # 本期财报的截止日期
    EndDate = '%s-%s' % (year, enddate_d.get(oritype))
    # 去年同期财报的截止日期
    PreEndDate = '%s-%s' % (year-1, enddate_d.get(oritype))

    if secucode[:3] == '688':
        SQL = """
            SELECT A.SecuCode,B.EndDate,B.InfoPublDate,B.IfAdjusted,B.NPParentCompanyOwners from LC_STIBIncomeState B,secumain A
        WHERE A.SecuCode='%s' AND A.SecuCategory=1  AND A.SecuMarket IN(83,90) AND A.ListedSector IN(1,2,6,7) AND
         A.CompanyCode=B.CompanyCode AND B.IfMerged=1 AND B.IfAdjusted IN(1,2) AND (EndDate='%s' OR EndDate ='%s')
          ORDER BY B.EndDate DESC,InfoPublDate DESC,IfAdjusted ASC;
        """ % (secucode, EndDate, PreEndDate)
    else:
        SQL = """
        SELECT A.SecuCode,B.EndDate,B.InfoPublDate,B.IfAdjusted,B.NPParentCompanyOwners from LC_IncomeStatementAll B,secumain A
        WHERE A.SecuCode='%s' AND A.SecuCategory=1  AND A.SecuMarket IN(83,90) AND A.ListedSector IN(1,2,6,7) AND
         A.CompanyCode=B.CompanyCode AND B.IfMerged=1 AND B.IfAdjusted IN(1,2) AND (EndDate='%s' OR EndDate ='%s')
          ORDER BY B.EndDate DESC,InfoPublDate DESC,IfAdjusted ASC;
        """ % (secucode, EndDate, PreEndDate)

    data = mysql_obj_juyuan.read_sql(SQL)
    data = data.drop_duplicates(subset=['EndDate'], keep='first').dropna(subset=['NPParentCompanyOwners'])
    EventCode = None  # 事件类型-和sf_const_announcement中的EventCode相对应（如A001001）
    evtype = None
    if len(data) == 2:
        NPParentCompanyOwners_list = data.NPParentCompanyOwners.to_list()
        this_yeard = NPParentCompanyOwners_list[0]
        pre_yeard = NPParentCompanyOwners_list[1]
        print(f'this_yeard:{this_yeard},pre_yeard:{pre_yeard}')
        if pre_yeard > 0 and this_yeard > pre_yeard:
            # *报上升
            evtype = 1
        elif this_yeard < pre_yeard and this_yeard > 0:
            # *报下降
            evtype = 2
        elif this_yeard < 0 and pre_yeard > 0:
            # *报首亏
            evtype = 3
        elif this_yeard > 0 and pre_yeard < 0:
            # *报扭亏
            evtype = 4

    # 判断事件类型
    if oritype in (1, 3):
        if evtype == 1:
            EventCode = 'A001001'
            # 季报上升
        elif evtype == 2:
            EventCode = 'A001002'
            # 季报下降
        elif evtype == 3:
            EventCode = 'A001012'
            # 季报首亏
        elif evtype == 4:
            EventCode ='A001011'
            # 季报扭亏

    elif oritype == 2:
        if evtype == 1:
            EventCode = 'A001005'
            # 中报上升
        elif evtype == 2:
            EventCode ='A001006'
            # 中报下降
        elif evtype == 3:
            # 中报首亏
            EventCode = 'A001016'
        elif evtype == 4:
            # 中报扭亏
            EventCode = 'A001015'

    elif oritype == 4:
        if evtype == 1:
            # 年报上升
            EventCode = 'A001003'
        elif evtype == 2:
            # 年报下降
            EventCode = 'A001004'
        elif evtype == 3:
            # 年报首亏
            EventCode = 'A001014'
        elif evtype == 4:
            # 年报扭亏
            EventCode = 'A001013'

    return EventCode

# 示例
rs = eventcode_recognize('688003', 2020, 1)
print(rs)
