import base64
import hashlib
import hmac
import json
import logging
import time
import urllib.parse

import requests

from announcement import sql_base
from announcement.spider_configs import (SECRET, TOKEN, USER_PHONE, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT,
    SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD,
    JUY_DB, )
from announcement.sql_base import Connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_secucode(data: dict):
    _map = {
        # select * from juchao_codemap where orgid in ('9900010450', '9900021962', 'gssh0600087', 'gssh0600849', 'gssz0000022', 'gssz0000043');
        # '601399': '601268',
        # '601360': '601313',
        # '601975': '600087',
        # '601607': '600849',
        # '001872': '000022',
        # '001914': '000043',

        '600010': 'B06475',
        '600029': '136054',
        '600267': '122427',
        '600322': '122421',
        '600352': '136206',
        '600369': '122404',
        '600748': '122362',
        '600770': '122088',
        '600801': '122188',
        '600963': '122257',
        '601377': '122304',
        '601688': '122388',
        '601008': '136092',
        '601238': '113009',
        '601038': '122253',
        '600011': '122008',
        '600030': '122385',
        '600035': '122378',
        '600068': '136427',
        '600098': '122157',
        '600157': '122267',
        '600185': '110030',
        '600210': '122043',
        '600226': '122254',
        '600236': '122192',
        '600256': '122102',
        '600360': '122134',
        '600376': '122377',
        '600383': '122488',
        '600518': '122354',
        '600575': '122235',
        '600635': '122112',
        '600648': '136666',
        '600657': '136294',
        '600660': '136566',
        '600743': '122370',
        '600755': '110033',
        '600765': '122104',
        '600804': '122132',
        '600823': '136303',
        '600859': '122190',
        '600869': '136317',
        '601788': '143155',
    }

    _rmap = {}
    for k, v in _map.items():
        _rmap[v] = k

    secu_code = data.get("SecuCode")

    secu_code = _rmap.get(secu_code, secu_code)

    if secu_code.startswith("6"):
        data['SecuCode'] = "SH" + secu_code
    elif secu_code.startswith("3") or secu_code.startswith("0"):
        data['SecuCode'] = "SZ" + secu_code
    else:
        return None
    return data


def fetch_A_secucode_innercode_map(juyuan_conn: sql_base.Connection):
    '''
    给出任意一个 SecuCode, 不管是上市还是退市, 不管是变更前还是变更后, 均在这此找到唯一的InnerCode
    '''

    sql = """
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
    """

    exec_res = juyuan_conn.query(sql)
    map1 = {}
    for one in exec_res:
        map1[one['SecuCode']] = one['InnerCode']

    sql = f'''select InnerCode, SecuMarket from secumain where InnerCode in {tuple(map1.values())};'''
    res = juyuan_conn.query(sql)
    map2 = {}
    for r in res:
        map2[r['InnerCode']] = r['SecuMarket']
    info = {}

    for k, v in map1.items():
        if map2[v] == 83:
            k = "SH" + k
            info[k] = v
        elif map2[v] == 90:
            k = "SZ" + k
            info[k] = v
        else:
            raise

    return info


def get_inc_num(conn: sql_base.Connection, table_name: str, field: str):
    query_sql = '''
    select count(id) as inc_count from {} where {} >= date_sub(CURDATE(), interval 1 day);
    '''
    query_sql = query_sql.format(table_name, field)
    inc_count = conn.get(query_sql).get("inc_count")
    return inc_count


def ding_msg(msg: str):
    """发送钉钉预警消息"""
    def get_url():
        timestamp = str(round(time.time() * 1000))
        secret_enc = SECRET.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, SECRET)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(
            TOKEN, timestamp, sign)
        return url

    url = get_url()
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = {
        "msgtype": "text",
        "text": {
            "content": f"{msg}@{USER_PHONE}"
        },
        "at": {
            "atMobiles": [
                USER_PHONE,
            ],
            "isAtAll": False
        }
    }
    message_json = json.dumps(message)
    resp = requests.post(url=url, data=message_json, headers=header)
    if resp.status_code == 200:
        logger.info("钉钉发送消息成功: {}".format(msg))
    else:
        logger.warning("钉钉消息发送失败")


def send_crawl_overview():
    conn = Connection(
        host=SPIDER_MYSQL_HOST,
        port=SPIDER_MYSQL_PORT,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        database=SPIDER_MYSQL_DB
    )
    spiders_info = {
        'juchao_ant2': 'AntTime',
        'juchao_ant_finance': 'AntTime',
        'juchao_kuaixun': 'pub_date',
        'announcement_base2': 'PubDatetime1',

        # TODO v1 版本的讯息
        'juchao_ant': 'AntTime',
        'announcement_base': 'PubDatetime1',
    }

    msg = ''
    for table_name, field in spiders_info.items():
        count = get_inc_num(conn, table_name, field)
        msg += f'{table_name} 相比昨日新增的个数是 {count}\n'

    print(msg)
    ding_msg(msg)
    return msg


if __name__ == '__main__':
    # ding_msg('just test')

    # send_crawl_overview()

    juyuanconn = Connection(
        host=JUY_HOST,
        port=JUY_PORT,
        user=JUY_USER,
        password=JUY_PASSWD,
        database=JUY_DB,
    )

    ret = fetch_A_secucode_innercode_map(juyuanconn)

    print(ret)
