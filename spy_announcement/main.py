import logging
import os
import sys
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from spy_announcement.ann_secu_ref_generator import AnnSecuRef
from spy_announcement import utils
from spy_announcement.juchao_historyant_spider import JuchaoHistorySpider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


executors = {
    'default': ThreadPoolExecutor(20)
}
ap_scheduler = BackgroundScheduler(executors=executors)


task_info = [
    {'task_id': 'his', 'task_name': 'his_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},
    {'task_id': 'ref', 'task_name': 'ann_secu_ref', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 1},
    # 概况播报
    {'task_id': 'ding', 'task_name': 'ding_msg', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 90},
]


def handle(event_name: str):
    if event_name == 'his':
        JuchaoHistorySpider().start()
    elif event_name == 'ref':
        AnnSecuRef().daily_sync()
    elif event_name == 'ding':
        utils.send_crawl_overview()


for data in task_info:
    ap_scheduler.add_job(
        func=handle,
        trigger=data['trigger'],
        minutes=data['time_interval'],
        args=(data['task_id'],),
        name=data['task_name'],
        max_instances=1,
    )


ap_scheduler.start()
handle('ding')


"""
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1

# 远程首次进行的关联表导入 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name ref --env LOCAL=0 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 \
python ann_secu_ref_generator.py


# 远程日常更新
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name spy_ann_ref --env LOCAL=0 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 \
python main.py

# 本地日常更新 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 \
-itd --name spy_ann_ref --env LOCAL=1 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spy_ann:v1 \
python main.py
"""


while True:    # 改为从命令行接收参数
    time.sleep(10)
