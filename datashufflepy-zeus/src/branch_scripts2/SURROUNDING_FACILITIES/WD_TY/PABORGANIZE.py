# -*- coding: utf-8 -*-
"""平安银行网点 PABORGANIZE  有经纬度"""
from branch_scripts import GenericScript
from database._mongodb import MongoClient
from tools.web_api_of_baidu import get_lat_lng, get_area


def data_shuffle(data, province_list, city_list, area_list):
    re_data = dict()
    prov_n = None
    prov_c = None
    city_n = None
    city_c = None
    area_n = None
    area_c = None
    addr_ = None

    # 市级信息清洗
    for city in city_list:
        if city["NAME_"] == data["CITY_NAME_"]:
            city_n = city["NAME_"]
            city_c = city["CODE_"]
            prov_c = city["CODE_"][:2] + "00"
            break
    if not city_n:
        for city in city_list:
            if city["NAME_"][:-1] == data["CITY_NAME_"]:
                city_n = city["NAME_"]
                city_c = city["CODE_"]
                prov_c = city["CODE_"][:2] + "00"
    if not city_n:
        for area in area_list:
            if area["NAME_"][:-1] == data["CITY_NAME_"]:
                area_n = area["NAME_"]
                area_c = area["CODE_"]
                city_c = area["CODE_"][:-2] + "00"
                prov_c = area["CODE_"][:2] + "00"
                break
        for city in city_list:
            if city["CODE_"] == city_c:
                city_n = city["NAME_"]
    # 省级信息清洗
    for prov in province_list:
        if prov["NAME_"][:2] == data["CITY_NAME_"]:
            prov_n = prov["NAME_"]
            prov_c = prov["CODE_"]
            city_n = prov["NAME_"]
            city_c = prov["CODE_"]
            break
        elif prov["CODE_"] == prov_c:
            prov_n = prov["NAME_"]
            break

    # 区县级信息清洗
    if not area_n:
        for area in area_list:
            if city_n:
                if city_n == prov_n:
                    if area["CODE_"][:2] == city_c[:2]:
                        if area["NAME_"] in data["ADDR_"]:
                            area_n = area["NAME_"]
                            area_c = area["CODE_"]
                elif area["CODE_"][:4] == city_c[:4]:
                    if area["NAME_"] in data["ADDR_"]:
                        area_n = area["NAME_"]
                        area_c = area["CODE_"]
    if not area_n:
        for area in area_list:
            if len(area["NAME_"]) < 3:
                continue
            elif area["CODE_"][:4] == city_c[:4]:
                if (area["NAME_"][:-1] in data["ADDR_"]) and (area["NAME_"][:-1] != city_n[:-1]):
                    check_index = data["ADDR_"].find(area["NAME_"][:-1])
                    if ("道" not in data["ADDR_"][check_index:check_index+len(area["NAME_"][:-1])+2]) \
                            and ("路" not in data["ADDR_"][check_index:check_index+len(area["NAME_"][:-1])+2]) \
                            and ("街" not in data["ADDR_"][check_index:check_index+len(area["NAME_"][:-1])+2]):
                        area_n = area["NAME_"]
                        area_c = area["CODE_"]
    # 特殊情况
    if "个旧市" in data["ADDR_"]:
        area_n = "个旧市"
        area_c = "532501"
        city_n = "红河哈尼族彝族自治州"
        city_c = "532500"
        prov_n = "云南省"
        prov_c = "5300"
    elif "辛集市" in data["ADDR_"]:
        area_n = "辛集市"
        area_c = "139002"
        city_n = "石家庄市"
        city_c = "130100"
        prov_n = "河北省"
        prov_c = "1300"
    # 地址清洗
    if prov_n in data["ADDR_"]:
        addr_ = data["ADDR_"]
    elif prov_n[:-1] in data["ADDR_"][:len(prov_n)]:
        addr_ = data["ADDR_"][:len(prov_n)].replace(prov_n[:-1], prov_n) + data["ADDR_"][len(prov_n):]
    elif prov_n[:4] in data["ADDR_"][:len(prov_n)]:
        addr_ = data["ADDR_"][:len(prov_n)].replace(prov_n[:4], prov_n) + data["ADDR_"][len(prov_n):]
    elif prov_n[:3] in data["ADDR_"][:len(prov_n)]:
        addr_ = data["ADDR_"][:len(prov_n)].replace(prov_n[:3], prov_n) + data["ADDR_"][len(prov_n):]
    elif prov_n[:2] in data["ADDR_"][:len(prov_n)]:
        addr_ = data["ADDR_"][:len(prov_n)].replace(prov_n[:2], prov_n) + data["ADDR_"][len(prov_n):]
    else:
        addr_ = prov_n + data["ADDR_"]

    if city_n in addr_[:len(prov_n) + len(city_n)]:
        addr_ = addr_
    elif city_n[:-1] in addr_[:len(prov_n) + len(city_n)]:
        addr_ = addr_[:len(prov_n) + len(city_n)].replace(
            city_n[:-1], city_n) + addr_[len(prov_n) + len(city_n):]
    elif city_n[:4] in addr_[:len(prov_n) + len(city_n)]:
        addr_ = addr_[:len(prov_n) + len(city_n)].replace(
            city_n[:4], city_n) + addr_[len(prov_n) + len(city_n):]
    elif city_n[:3] in addr_[:len(prov_n) + len(city_n)]:
        addr_ = addr_[:len(prov_n) + len(city_n)].replace(
            city_n[:3], city_n) + addr_[len(prov_n) + len(city_n):]
    elif city_n[:2] in addr_[:len(prov_n) + len(city_n)]:
        addr_ = addr_[:len(prov_n) + len(city_n)].replace(
            city_n[:2], city_n) + addr_[len(prov_n) + len(city_n):]
    else:
        addr_ = addr_[:len(prov_n)] + city_n + addr_[len(prov_n):]

    # # 添加分行编码
    # branch_code = None
    # for i in range(1, 10000):
    #     branch_code = "PAB" + "_" + city_c + "_" + "00000"
    #     branch_code = branch_code[:len(branch_code) - len(str(i))] + "{}".format(i)
    #     if branch_code in branch_code_list:
    #         continue
    #     else:
    #         branch_code_list.append(branch_code)
    #         break

    # "C"
    re_data["BANK_CODE_"] = "PAB"
    re_data["BANK_NAME_"] = data["ENTITY_NAME_"][:-3]
    re_data["SPIDER_TIME_"] = data["DATETIME_"]
    # re_data["AREA_CODE_"] = area_c
    # re_data["AREA_NAME_"] = area_n
    # re_data["UNIT_CODE_"] = "PAB" + "_" + city_c

    # "F"
    re_data["ADDR_"] = addr_
    # re_data["CITY_CODE_"] = city_c
    # re_data["CITY_NAME_"] = city_n
    # re_data["LAT_"] = data["LAT_"]
    # re_data["LNG_"] = data["LNG_"]
    re_data["NAME_"] = data["NAME_"]
    # re_data["PROVINCE_CODE_"] = prov_c
    # re_data["PROVINCE_NAME_"] = prov_n

    result = get_lat_lng(address=re_data["ADDR_"])
    try:
        re_data["LAT_"] = str(result["result"]["location"]["lat"])
        re_data["LNG_"] = str(result["result"]["location"]["lng"])
    except KeyError:
        re_data["LAT_"] = ""
        re_data["LNG_"] = ""
    else:
        dis_result = get_area(",".join([re_data["LAT_"], re_data["LNG_"]]))
        try:
            re_data["AREA_NAME_"] = dis_result["result"]["addressComponent"]["district"]
        except KeyError:
            re_data["AREA_NAME_"] = ""
        try:
            re_data["AREA_CODE_"] = dis_result["result"]["addressComponent"]["adcode"]
        except KeyError:
            re_data["AREA_CODE_"] = ""
        else:
            re_data["CITY_CODE_"] = re_data["AREA_CODE_"][:4] + "00"
            re_data["PROVINCE_CODE_"] = re_data["AREA_CODE_"][:2] + "00"
            for city in city_list:
                if city["CODE_"] == re_data["CITY_CODE_"]:
                    re_data["CITY_NAME_"] = city["NAME_"]
                    break
            for prov in province_list:
                if prov["CODE_"] == re_data["PROVINCE_CODE_"]:
                    re_data["PROVINCE_NAME_"] = prov["NAME_"]
                    break
    re_data["UNIT_CODE_"] = "PAB" + "_" + re_data.get("CITY_CODE_", "")

    re_data["ENTITY_CODE_"] = data["ENTITY_CODE_"]
    re_data["ENTITY_NAME_"] = data["ENTITY_NAME_"]
    re_data["URL_"] = data["URL_"]
    if "TEL_" in data:
        re_data["TEL_"] = data["TEL_"]
    if "BUSINESS_HOURS_" in data:
        re_data["BUSINESS_HOURS_"] = data["BUSINESS_HOURS_"]
    if "SOURCE_TYPE_NAME_" in data:
        re_data["SOURCE_TYPE_NAME_"] = data["SOURCE_TYPE_NAME_"]
    re_data["TYPE_NAME_"] = "支行"
    re_data["TYPE_"] = "ZH"

    return re_data


if __name__ == '__main__':
    main_mongo = MongoClient(entity_code="PABORGANIZE", mongo_collection="WD_TY")
    sc = GenericScript
    # Mysql connection
    sc.mysql_client, sc.mysql_connection = sc.mysql_connect()
    province_list, city_list, area_list, dir_area_list, bank_list = sc.data_from_mysql()
    data_list = main_mongo.main()
    for data in data_list:
        re_data = data_shuffle(data, province_list, city_list, area_list)
        # print(re_data)
