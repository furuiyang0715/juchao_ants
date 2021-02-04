import pprint

web_category_codename_map = {}
web_category_info = [
    {"key": "category_ndbg_szsh", "value": "年报"},
    {"key": "category_bndbg_szsh", "value": "半年报"},
    {"key": "category_yjdbg_szsh", "value": "一季报"},
    {"key": "category_sjdbg_szsh", "value": "三季报"},
    {"key": "category_yjygjxz_szsh", "value": "业绩预告"},
    {"key": "category_qyfpxzcs_szsh", "value": "权益分派"},
    {"key": "category_dshgg_szsh", "value": "董事会"},
    {"key": "category_jshgg_szsh", "value": "监事会"},
    {"key": "category_gddh_szsh", "value": "股东大会"},
    {"key": "category_rcjy_szsh", "value": "日常经营"},
    {"key": "category_gszl_szsh", "value": "公司治理"},
    {"key": "category_zj_szsh", "value": "中介报告"},
    {"key": "category_sf_szsh", "value": "首发"},
    {"key": "category_zf_szsh", "value": "增发"},
    {"key": "category_gqjl_szsh", "value": "股权激励"},
    {"key": "category_pg_szsh", "value": "配股"},
    {"key": "category_jj_szsh", "value": "解禁"},
    {"key": "category_gszq_szsh", "value": "公司债"},
    {"key": "category_kzzq_szsh", "value": "可转债"},
    {"key": "category_qtrz_szsh", "value": "其他融资"},
    {"key": "category_gqbd_szsh", "value": "股权变动"},
    {"key": "category_bcgz_szsh", "value": "补充更正"},
    {"key": "category_cqdq_szsh", "value": "澄清致歉"},
    {"key": "category_fxts_szsh", "value": "风险提示"},
    {"key": "category_tbclts_szsh", "value": "特别处理和退市"},
    {"key": "category_tszlq_szsh", "value": "退市整理期"}
]
for one in web_category_info:
    web_category_codename_map[one.get("key")] = one.get("value")

print(pprint.pformat(web_category_codename_map))
