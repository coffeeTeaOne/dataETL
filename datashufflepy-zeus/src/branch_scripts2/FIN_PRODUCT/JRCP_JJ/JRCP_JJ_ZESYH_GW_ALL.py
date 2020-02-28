# -*- coding: utf-8 -*-
"""浙商银行-官网基金信息  代销基金  CHA_BRANCH_FUND_AGENT"""
from database._mongodb import MongoClient


def data_shuffle(data):
    """爬取的数据不止含有基金，只清洗PRO_TYPE_='基金'的数据"""
    return None if data.get("PRO_TYPE_") and data["PRO_TYPE_"] != "基金" else data


if __name__ == '__main__':
    main_mongo = MongoClient(entity_code="JRCP_JJ_ZESYH_GW_ALL", mongo_collection="CRMJRCP_JJ")
    data_list = main_mongo.main()
    for data in data_list:
        re_data = data_shuffle(data)
        print(re_data)
