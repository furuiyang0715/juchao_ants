import json

import requests

api = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.cninfo.com.cn',
    'Origin': 'http://www.cninfo.com.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
}


def _query(stock_str: str = '',
           se_date: str = '',
           cat_code: str = '',
           page: int = 1,
           search_key: str = '',
           ):
    ants = []
    post_data = {
        'pageNum': page,
        'pageSize': 30,
        'column': 'szse',
        'tabName': 'fulltext',
        'plate': '',
        'stock': stock_str,
        'searchkey': search_key,
        'secid': '',
        'category': cat_code,
        'trade': '',
        'seDate': se_date,
        'sortName': '',
        'sortType': '',
        'isHLtitle': True,
    }
    resp = requests.post(api, headers=headers, data=post_data, timeout=3)
    if resp.status_code == 200:
        text = resp.text
        if text == '':
            ants = []
        else:
            py_datas = json.loads(text)
            ant_count = py_datas.get("totalAnnouncement")
            print(ant_count)
            if ant_count > 3000:
                # TODO
                pass
            ants = py_datas.get("announcements")
            if ants is None:
                ants = []
    return ants


'''
pageNum: 1
pageSize: 30
column: szse
tabName: fulltext
plate: 
stock: 603920,9900030580
searchkey: 
secid: 
category: 
trade: 
seDate: 2020-08-19~2021-02-20
sortName: 
sortType: 
isHLtitle: true
'''

# total = []
# for page in range(200):
#     ants = _query(stock_str='',
#                   se_date='2018-08-19~2021-02-20',
#                   cat_code='category_ndbg_szsh',
#                   page=page,     # 16346
#                   search_key='',
#                   )
#     print(page, len(ants))
#     total.extend(ants)
#
# print(len(total))


ants = _query(stock_str='',
              se_date='2018-08-19~2021-02-20',
              cat_code='category_ndbg_szsh',
              page=200,     # 16346
              search_key='',
              )
print(len(ants))
# print(ants[0])


ants = _query(stock_str='',
              se_date='2018-08-19~2021-02-20',
              cat_code='category_ndbg_szsh',
              page=201,     # 16346
              search_key='',
              )
print(len(ants))
# print(ants[0])

