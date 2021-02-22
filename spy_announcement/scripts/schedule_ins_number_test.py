"""
Demonstrates how to use the blocking scheduler to schedule a job that executes on 3 second
intervals.
"""
import time
from datetime import datetime
import os

from apscheduler.schedulers.blocking import BlockingScheduler


def tick():
    print('Tick! The time is: %s' % datetime.now())
    time.sleep(60)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'interval', seconds=3)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    # 达到最大的运行实例数
    # （1） 增加可同时运行的实例个数 （2） 控制单个实例运行的时间
    # Execution of job "tick (trigger: interval[0:00:03], next run at: 2021-02-22 15:23:54 CST)" skipped: maximum number of running instances reached (1)

