import base64
import hashlib
import hmac
import json
import logging
import time
import urllib.parse

import requests

from spy_announcement import sql_base
from spy_announcement.spider_configs import (SECRET, TOKEN, USER_PHONE, SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT,
    SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB)
from spy_announcement.sql_base import Connection


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        # 'juchao_ant2': 'AntTime',
        # 'juchao_ant_finance': 'AntTime',
        # 'juchao_kuaixun': 'pub_date',
        # 'announcement_base2': 'PubDatetime1',
        #
        # TODO v1 版本的讯息
        # 'juchao_ant': 'AntTime',
        # 'announcement_base': 'PubDatetime1',

        'spy_announcement_data': 'pub_datetime',


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

    send_crawl_overview()

    pass
