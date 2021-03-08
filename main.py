import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from annversion1.base1 import SourceAnnouncementBaseV1
from annversion1.his1 import JuchaoHistorySpiderV1
from annversion2 import utils
from annversion2.juchao_finance_hotfixes_spider import JuchaoFinanceSpider
from annversion2.juchao_historyants_spider import JuchaoHistorySpider
from annversion2.juchao_livenews_spider import JuchaoLiveNewsSpider
from annversion2.source_announcement_base import SourceAnnouncementBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


executors = {
    'default': ThreadPoolExecutor(20)
}
ap_scheduler = BackgroundScheduler(executors=executors)


task_info = [
    {'task_id': 'his', 'task_name': 'his_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},
    {'task_id': 'live', 'task_name': 'live_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 10},
    {'task_id': 'fin', 'task_name': 'finance_update', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 10},
    {'task_id': 'base', 'task_name': 'merge_base', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},

    # v1
    # {'task_id': 'his1', 'task_name': 'his_spider1', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 3},    # TODO 从某个时间点开始的间隔 2min 一次 避免执行时线程比较集中
    # {'task_id': 'base1', 'task_name': 'merge_base1', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 3},

    # 概况播报
    {'task_id': 'ding', 'task_name': 'ding_msg', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 90},
]


def handle(event_name: str):
    if event_name == 'his':
        JuchaoHistorySpider().start()
    elif event_name == 'live':
        JuchaoLiveNewsSpider().start()
    elif event_name == 'fin':
        JuchaoFinanceSpider().start()
    elif event_name == 'base':
        SourceAnnouncementBase().daily_update()
    elif event_name == 'ding':
        utils.send_crawl_overview()

    # v1 版本
    elif event_name == 'his1':
        JuchaoHistorySpiderV1().start()
    elif event_name == 'base1':
        SourceAnnouncementBaseV1().daily_update()


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
#
#
# while True:    # TODO 改为从命令行接收参数
#     time.sleep(10)


if __name__ == '__main__':
    # handle('his')
    # handle('live')
    # handle('fin')
    # handle('base')
    # handle('ding')

    # handle('his1')
    handle('base1')


    pass
