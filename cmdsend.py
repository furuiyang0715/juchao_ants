import argparse
import datetime
import sys

from annversion2.juchao_finance_hotfixes_spider import JuchaoFinanceSpider
from annversion2.juchao_livenews_spider import JuchaoLiveNewsSpider

# v1
from annversion1.base1 import SourceAnnouncementBaseV1
from annversion1.his1 import JuchaoHistorySpiderV1

# v2
from annversion2.juchao_historyants_spider import JuchaoHistorySpider
from annversion2.source_announcement_base import SourceAnnouncementBase

# 新版
from spy_announcement.ann_secu_ref_generator import AnnSecuRef
from spy_announcement.juchao_historyant_spider import JuchaoHistorySpy


parser = argparse.ArgumentParser(description='脚本启动爬虫')

parser.add_argument('--type', type=str, help='要启动的爬虫文件 his:启动历史搜索爬虫 live:启动快讯爬虫'
                                             ' base:启动合并爬虫合并程序 fin:启动财务补充爬虫数据'
                                             ' his1: 版本1的历史爬虫  base1: 版本1的合并程序')
parser.add_argument('--start', type=str, help='重跑的开始时间 格式示例:2021-01-01')
parser.add_argument('--end', type=str, help='重跑的结束时间 格式示例:2021-01-01')

args = parser.parse_args()

spider_type = args.type
start_dt_string = args.start
end_dt_string = args.end


try:
    start_dt = datetime.datetime.strptime(start_dt_string, '%Y-%m-%d')
    end_dt = datetime.datetime.strptime(end_dt_string, '%Y-%m-%d')
except:
    print("请输入正确的时间格式, 举例: 2021-01-01")
    sys.exit(0)

print(f'选择的脚本类型是 {spider_type}\n开始时间是 {start_dt}\n结束时间是{end_dt}')

if spider_type == 'live':
    JuchaoLiveNewsSpider().start(start_dt, end_dt)
elif spider_type == 'fin':
    JuchaoFinanceSpider().start(start_dt, end_dt)

elif spider_type == 'his1':
    JuchaoHistorySpiderV1().start(start_dt, end_dt)
elif spider_type == 'base1':
    SourceAnnouncementBaseV1().daily_update(deadline=start_dt)

elif spider_type == 'his2':
    JuchaoHistorySpider().start(start_dt=start_dt, end_dt=end_dt)
elif spider_type == 'base2':
    SourceAnnouncementBase().daily_update(deadline=start_dt)

elif spider_type == 'his':
    JuchaoHistorySpy().start(start_dt=start_dt, end_dt=end_dt)
elif spider_type == 'ref':
    AnnSecuRef().daily_sync(start_dt=start_dt)


else:
    print('请在规定的范围内输入参数: his:启动历史搜索爬虫 live:启动快讯爬虫 base:启动合并爬虫合并程序'
          ' fin:启动财务补充爬虫数据 his1: 版本1的历史爬虫  base1: 版本1的合并程序')
