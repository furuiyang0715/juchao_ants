import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

import utils
from annversion1.base1 import SourceAnnouncementBaseV1
from annversion1.his1 import JuchaoHistorySpiderV1

from annversion2.juchao_livenews_spider import JuchaoLiveNewsSpider
from annversion2.juchao_finance_hotfixes_spider import JuchaoFinanceSpider

from annversion2.juchao_historyants_spider import JuchaoHistorySpider
from annversion2.source_announcement_base import SourceAnnouncementBase

from spy_announcement.ann_secu_ref_generator import AnnSecuRef
from spy_announcement.juchao_historyant_spider import JuchaoHistorySpy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


executors = {
    'default': ThreadPoolExecutor(20)
}
ap_scheduler = BackgroundScheduler(executors=executors)


task_info = [
    # v1 v2 公用
    {'task_id': 'live', 'task_name': 'live_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 10},
    {'task_id': 'fin', 'task_name': 'finance_update', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 10},

    # v1
    {'task_id': 'his1', 'task_name': 'his_spider1', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 3},
    {'task_id': 'base1', 'task_name': 'merge_base1', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 3},

    # v2
    {'task_id': 'his2', 'task_name': 'his_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},
    {'task_id': 'base2', 'task_name': 'merge_base', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},

    # 最新
    {'task_id': 'his', 'task_name': 'his_spider', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 2},
    {'task_id': 'ref', 'task_name': 'ann_secu_ref', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 1},

    # 概况播报
    {'task_id': 'ding', 'task_name': 'ding_msg', "trigger": 'interval', 'time_unit': 'minutes', 'time_interval': 90},
]


def handle(event_name: str):
    # v1 版本
    if event_name == 'his1':    # juchao_ant
        JuchaoHistorySpiderV1().start()
    elif event_name == 'base1':    # announcement_base
        SourceAnnouncementBaseV1().daily_update()

    # v2 版本
    elif event_name == 'his2':   # juchao_ant2
        JuchaoHistorySpider().start()
    elif event_name == 'base2':    # announcement_base2
        SourceAnnouncementBase().daily_update()

    # v1 v2 公用
    elif event_name == 'live':    # juchao_kuaixun
        JuchaoLiveNewsSpider().start()
    elif event_name == 'fin':    # juchao_ant_finance
        JuchaoFinanceSpider().start()

    # 新版
    elif event_name == 'his':   # spy_announcement_data
        JuchaoHistorySpy().start()
    elif event_name == 'ref':    # an_announcement_secu_ref
        AnnSecuRef().daily_sync()

    # 播报模块
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


while True:
    time.sleep(10)
