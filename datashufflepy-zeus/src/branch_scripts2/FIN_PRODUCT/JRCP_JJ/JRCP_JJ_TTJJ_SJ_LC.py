# -*- coding: utf-8 -*-
"""天天基金网-理财型基金市价信息  """
from database._mongodb import MongoClient


def data_shuffle(data):
    data["add_field_list"] = ["CLOSE_"]
    return data


if __name__ == '__main__':
    main_mongo = MongoClient(entity_code="JRCP_JJ_TTJJ_SJ_LC", mongo_collection="CRMJRCP_JJ")
    data_list = main_mongo.main()
    for data in data_list:
        re_data = data_shuffle(data)
        print(re_data)
