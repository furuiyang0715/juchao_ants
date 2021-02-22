import time

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
    print(t2 - t1)


if __name__ == "__main__":
    ann_derivation_task()
