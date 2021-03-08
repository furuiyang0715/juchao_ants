import configparser
import os

env = os.environ

cf = configparser.ConfigParser()
thisdir = os.path.dirname(__file__)
cf.read(os.path.join(thisdir, 'ann.ini'))


# deploy
LOCAL = bool(int(env.get("LOCAL", cf.get('deploy', 'LOCAL'))))
SECRET = env.get("SECRET", cf.get('deploy', 'SECRET'))
TOKEN = env.get("TOKEN", cf.get('deploy', 'TOKEN'))
USER_PHONE = env.get('USER_PHONE', cf.get('deploy', 'USER_PHONE'))
PROXY_URL = env.get("PROXY_URL", cf.get("deploy", "PROXY_URL"))
LOCAL_PROXY_URL = env.get("LOCAL_PROXY_URL", cf.get("deploy", "LOCAL_PROXY_URL"))


# datacenter
DC_HOST = env.get("DC_HOST", cf.get('dc', 'DC_HOST'))
DC_PORT = int(env.get("DC_PORT", cf.get('dc', 'DC_PORT')))
DC_USER = env.get("DC_USER", cf.get('dc', 'DC_USER'))
DC_PASSWD = env.get("DC_PASSWD", cf.get('dc', 'DC_PASSWD'))
DC_DB = env.get("DC_DB", cf.get('dc', 'DC_DB'))


# test
TEST_MYSQL_HOST = env.get("TEST_MYSQL_HOST", cf.get('test', 'TEST_MYSQL_HOST'))
TEST_MYSQL_PORT = int(env.get("TEST_MYSQL_PORT", cf.get('test', 'TEST_MYSQL_PORT')))
TEST_MYSQL_USER = env.get("TEST_MYSQL_USER", cf.get('test', 'TEST_MYSQL_USER'))
TEST_MYSQL_PASSWORD = env.get("TEST_MYSQL_PASSWORD", cf.get('test', 'TEST_MYSQL_PASSWORD'))
TEST_MYSQL_DB = env.get("TEST_MYSQL_DB", cf.get('test', 'TEST_MYSQL_DB'))


# 聚源
JUY_HOST = env.get("JUY_HOST", cf.get('juyuan', 'JUY_HOST'))
JUY_PORT = int(env.get("JUY_PORT", cf.get('juyuan', 'JUY_PORT')))
JUY_USER = env.get("JUY_USER", cf.get('juyuan', 'JUY_USER'))
JUY_PASSWD = env.get("JUY_PASSWD", cf.get('juyuan', 'JUY_PASSWD'))
JUY_DB = env.get("JUY_DB", cf.get('juyuan', 'JUY_DB'))

# 主题猎手数据库
THE_HOST = env.get("THE_HOST", cf.get('theme', 'THE_HOST'))
THE_PORT = int(env.get("THE_PORT", cf.get('theme', 'THE_PORT')))
THE_USER = env.get("THE_USER", cf.get('theme', 'THE_USER'))
THE_PASSWD = env.get("THE_PASSWD", cf.get('theme', 'THE_PASSWD'))
THE_DB = env.get("THE_DB", cf.get('theme', 'THE_DB'))


# spider 读
R_SPIDER_MYSQL_HOST = env.get("R_SPIDER_MYSQL_HOST", cf.get('r_spider', 'R_SPIDER_MYSQL_HOST'))
R_SPIDER_MYSQL_PORT = int(env.get("R_SPIDER_MYSQL_PORT", cf.get('r_spider', 'R_SPIDER_MYSQL_PORT')))
R_SPIDER_MYSQL_USER = env.get("R_SPIDER_MYSQL_USER", cf.get('r_spider', 'R_SPIDER_MYSQL_USER'))
R_SPIDER_MYSQL_PASSWORD = env.get("R_SPIDER_MYSQL_PASSWORD", cf.get('r_spider', 'R_SPIDER_MYSQL_PASSWORD'))
R_SPIDER_MYSQL_DB = env.get("R_SPIDER_MYSQL_DB", cf.get('r_spider', 'R_SPIDER_MYSQL_DB'))

# spider 写
if LOCAL:
    SPIDER_MYSQL_HOST = env.get("SPIDER_MYSQL_HOST", cf.get('local_w_spider', 'W_SPIDER_MYSQL_HOST'))
    SPIDER_MYSQL_PORT = int(env.get("SPIDER_MYSQL_PORT", cf.get('local_w_spider', 'W_SPIDER_MYSQL_PORT')))
    SPIDER_MYSQL_USER = env.get("SPIDER_MYSQL_USER", cf.get('local_w_spider', 'W_SPIDER_MYSQL_USER'))
    SPIDER_MYSQL_PASSWORD = env.get("SPIDER_MYSQL_PASSWORD", cf.get('local_w_spider', 'W_SPIDER_MYSQL_PASSWORD'))
    SPIDER_MYSQL_DB = env.get("SPIDER_MYSQL_DB", cf.get('local_w_spider', 'W_SPIDER_MYSQL_DB'))
else:
    SPIDER_MYSQL_HOST = env.get("SPIDER_MYSQL_HOST", cf.get('w_spider', 'W_SPIDER_MYSQL_HOST'))
    SPIDER_MYSQL_PORT = int(env.get("SPIDER_MYSQL_PORT", cf.get('w_spider', 'W_SPIDER_MYSQL_PORT')))
    SPIDER_MYSQL_USER = env.get("SPIDER_MYSQL_USER", cf.get('w_spider', 'W_SPIDER_MYSQL_USER'))
    SPIDER_MYSQL_PASSWORD = env.get("SPIDER_MYSQL_PASSWORD", cf.get('w_spider', 'W_SPIDER_MYSQL_PASSWORD'))
    SPIDER_MYSQL_DB = env.get("SPIDER_MYSQL_DB", cf.get('w_spider', 'W_SPIDER_MYSQL_DB'))
