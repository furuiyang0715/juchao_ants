import datetime
import time

from spiders.juchao_finance_hotfixes_spider import JuchaoFinanceSpider
from spiders.juchao_historyants_spider import JuchaoHistorySpider
from spiders.juchao_livenews_spider import JuchaoLiveNewsSpider
from spiders.source_announcement_base import SourceAnnouncementBase

# jclive = JuchaoLiveNewsSpider()
# jclive.start()
#
# jc_his = JuchaoHistorySpider()
# jc_his.start()

jc_merge = SourceAnnouncementBase()
jc_merge.launch()


# # 最近 5 年的财务数据
# finance_his = JuchaoFinanceSpider()
# _now = datetime.datetime.now()
# for num in range(5):
#     print(num)
#     _start = datetime.datetime(_now.year - num - 1, _now.month, _now.day)
#     _end = datetime.datetime(_now.year - num, _now.month, _now.day)
#     print("年份: ", _start, _end)
#     finance_his.start(start_date=_start, end_date=_end)
#     time.sleep(10)
