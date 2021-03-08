import logging
import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from spy_announcement.ann_secu_ref_generator import AnnSecuRef
import utils
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


# ap_scheduler.start()


if __name__ == '__main__':
    # handle('ding')

    # handle('his')

    handle('ref')

    pass