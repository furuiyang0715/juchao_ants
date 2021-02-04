from announcement.spider_configs import JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB
from announcement.sql_base import Connection


# 4274
sql1 = """(
SELECT InnerCode, SecuCode
FROM  secumain 
WHERE 
   SecuCategory=1 AND 
   SecuMarket IN(83,90) AND 
   ListedSector IN(1,2,6,7) and 
   ListedState=1
)
UNION 
(
SELECT A.InnerCode, A.SecuCode  
FROM  secumain A, LC_ListStatus B 
WHERE 
   A.SecuCategory=1 AND 
   A.SecuMarket IN(83,90) AND 
   A.ListedSector IN(1,2,6,7) AND 
   B.ChangeType IN(4) AND 
   A.InnerCode=B.InnerCode);
"""


# 4315
sql2 = '''(
SELECT InnerCode,SecuCode 
from secumain 
WHERE SecuCategory IN(1,41) and 
SecuMarket IN(83,90) and 
ListedSector IN(1,2,6,7) and 
ListedDate<=CURDATE())
UNION
(SELECT InnerCode,SecuCode 
from LC_CodeChange 
WHERE 
CodeDefine=1 and SecuMarket IN(83,90)); 
'''


# 4289
sql3 = '''
select A.InnerCode, A.SecuCode
from SecuMain A
left join 
LC_ListStatus B 
on A.InnerCode = B.InnerCode 
and B.ChangeType = 4 
where 
A.SecuMarket in (83, 90) 
and A.SecuCategory in (1, 41) 
and A.ListedSector in (1, 2, 6, 7) 
and A.ListedDate <= CURDATE(); 
'''


# 4294 最终结果
# 获取全量的 A 股 SecuCode 和 InnerCode 的映射包含改名的以及退市的
sql4 = '''
(
select A.SecuCode, A.InnerCode, A.SecuAbbr, A.ListedDate, B.ChangeDate '退市日期'
from gildata.SecuMain A
left join 
gildata.LC_ListStatus B 
on A.InnerCode = B.InnerCode 
and B.ChangeType = 4 
where 
A.SecuMarket in (83, 90) 
and A.SecuCategory in (1, 41) 
and A.ListedSector in (1, 2, 6, 7) 
and A.ListedDate <= CURDATE()
)
UNION
(
SELECT
A.SecuCode, A.InnerCode, B.SecuAbbr, A.BeginDate '启用日期', A.StopDate '停用日期'
FROM gildata.LC_CodeChange A
JOIN gildata.SecuMain B
ON A.InnerCode = B.InnerCode
AND B.SecuMarket IN (83,90)
AND B.SecuCategory in (1, 41) 
WHERE
A.CodeDefine = 1
AND A.SecuCode <> B.SecuCode
); 

'''


juyuan_conn = Connection(
    host=JUY_HOST,
    port=JUY_PORT,
    user=JUY_USER,
    password=JUY_PASSWD,
    database=JUY_DB,
)


# res1 = juyuan_conn.query(sql1)
# map1 = {}
# for one in res1:
#     map1[one['SecuCode']] = one['InnerCode']
#
# res2 = juyuan_conn.query(sql2)
# map2 = {}
# for one in res2:
#     map2[one['SecuCode']] = one['InnerCode']
#
#
# res3 = juyuan_conn.query(sql3)
# map3 = {}
# for one in res3:
#     map3[one['SecuCode']] = one['InnerCode']
#
# delta12 = set(map1.keys()) - set(map2.keys())
# # print(delta12)
#
# delta21 = set(map2.keys() - map1.keys())
# # print(delta21)
#
# delta23 = set(map2.keys() - map3.keys())
# print(delta23)
#
# delta32 = set(map3.keys() - map2.keys())
# print(delta32)


res4 = juyuan_conn.query(sql4)
map4 = {}


for one in res4:
    map4[one['SecuCode']] = one['InnerCode']
    if not one['SecuCode'][0] in ['0', '3', '6']:
        print(one)
