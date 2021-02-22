import os
import sys
import time

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)


from ann_derivation.bas_secumain_mgr import BasSecumainMgr
from ann_derivation.bas_stock_industry_mgr import BasStockIndustry


def ann_derivation_task():
    t1 = time.time()
    print("开始更新 bas_secumain 表 ")
    BSM = BasSecumainMgr()
    BSM.start()

    print("开始更新 bas_stock_industry 表")
    bs = BasStockIndustry()
    bs.start()
    t2 = time.time()
    print(f"运行时间: {t2 - t1}s")


if __name__ == "__main__":
    ann_derivation_task()
