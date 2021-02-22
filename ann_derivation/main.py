from ann_derivation.bas_secumain_mgr import BasSecumainMgr
from ann_derivation.bas_stock_industry_mgr import BasStockIndustry

if __name__ == "__main__":
    BSM = BasSecumainMgr()
    BSM.start()
    bs = BasStockIndustry()
    bs.start()
