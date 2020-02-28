# -*- coding: utf-8 -*-

# 中国农业银行网点 ABCORGANIZE  有经纬度

# 已处理 12862

import hashlib
import re

from scripts import GenericScript


def data_shuffle(data, province_list, city_list, area_list):
    for city in city_list:
        if city["NAME_"] == "县":
            city_list.remove(city)

    # for data in mongo_data_list:
    # 以前的数据
    if "AREA_NAME_" not in data:
        return None
    else:
        re_data = dict()
        addr_ = None
        area_c = None
        area_n = None
        city_c = None
        city_n = None
        prov_c = None
        prov_n = None

        # 西藏地区编码与数据库编码不符，单独清理
        if "西藏" in data["PROVINCE_NAME_"]:
            data["CITY_"] = data["CITY_"].replace("西藏自治区", "")
            if "西藏" in data["ADDR_"]:
                data["ADDR_"] = data["ADDR_"].replace("西藏", "西藏自治区")
            else:
                data["ADDR_"] = "西藏自治区" + data["ADDR_"]

            for city in city_list:
                if city["CODE_"][:2] == "54":
                    if data["CITY_"][:2] == city["NAME_"][:2]:
                        data["ADDR_"] = data["ADDR_"].replace(data["CITY_"], city["NAME_"])
                        data["CITY_"] = city["NAME_"]
                        data["CITY_CODE_"] = city["CODE_"]
                        data["ADDR_"] = data["ADDR_"].replace(data["CITY_"][:-1]+"地区", data["CITY_"])

                    if data["CITY_"][:-1] not in data["ADDR_"]:
                        data["ADDR_"] = data["ADDR_"][:5] + data["CITY_"] + data["ADDR_"][5:]

        # 青海地区编码与数据库编码不符，单独清理
        if "青海" in data["PROVINCE_NAME_"]:
            data["PROVINCE_NAME_"] = "青海省"
            data["CITY_"] = data["CITY_"].replace("青海", "")

            if "青海省" not in data["ADDR_"]:
                data["ADDR_"] = "青海省" + data["ADDR_"]

            for city in city_list:
                if city["CODE_"][:2] == "63":
                    if city["NAME_"][:2] == data["CITY_"][:2]:
                        data["CITY_"] = city["NAME_"]
                        data["CITY_CODE_"] = city["CODE_"]

                if data["CITY_"][:-1] not in data["ADDR_"]:
                    data["ADDR_"] = data["ADDR_"][:3] + data["CITY_"] + data["ADDR_"][3:]

        # 新疆地区编码与数据库编码不符，单独清理
        if "新疆" in data["PROVINCE_NAME_"]:
            data["PROVINCE_NAME_"] = "新疆维吾尔自治区"
            data["CITY_"] = data["CITY_"].replace("新疆维吾尔自治区", "")
            data["CITY_"] = data["CITY_"].replace("新疆", "")

            if ("新疆维吾尔自治区" not in data["ADDR_"]) and ("新疆" not in data["ADDR_"]):
                data["ADDR_"] = "新疆维吾尔自治区" + data["ADDR_"]
            elif ("新疆" in data["ADDR_"]) and("新疆维吾尔自治区" not in data["ADDR_"]):
                data["ADDR_"] = "新疆维吾尔自治区" + data["ADDR_"][2:]

            for city in city_list:
                if city["CODE_"][:2] == "65":
                    if city["NAME_"][:2] == data["CITY_"][:2]:
                        data["CITY_"] = city["NAME_"]
                        data["CITY_CODE_"] = city["CODE_"]

            # 哈密市只有一个伊州区，网点信息都是此区的
            if data["CITY_"] == "哈密市":
                data["AREA_NAME_"] = "伊州区"
                data["AREA_CODE_"] = "650502"
            for area in area_list:
                if area["CODE_"][:2] == "65":
                    if area["NAME_"][:2] in data["AREA_NAME_"]:
                        data["AREA_NAME_"] = area["NAME_"]
                        data["AREA_CODE_"] = area["CODE_"]

        # 内蒙古, 广西, 宁夏 字段统一：
        if (("内蒙古" in data["ADDR_"]) or ("广西" in data["ADDR_"]) or
                ("新疆" in data["ADDR_"]) or ("宁夏" in data["ADDR_"])):
            if data["PROVINCE_NAME_"] not in data["ADDR_"]:
                data["ADDR_"] = data["ADDR_"].replace("内蒙古", "内蒙古自治区")
                data["ADDR_"] = data["ADDR_"].replace("广西", "广西壮族自治区")
                data["ADDR_"] = data["ADDR_"].replace("宁夏", "宁夏回族自治区")
            if data["PROVINCE_NAME_"] in data["CITY_"]:
                data["CITY_"] = data["CITY_"].replace(data["PROVINCE_NAME_"], "")
            if data["CITY_"][:-1] not in data["ADDR_"]:
                data["ADDR_"] = data["ADDR_"][:len(data["PROVINCE_NAME_"])] + data["CITY_"] + data["ADDR_"][len(data["PROVINCE_NAME_"]):]
                data["ADDR_"] = re.sub(r"{}{}地?区?市?".format(data["CITY_"], data["CITY_"][:2]), data["CITY_"], data["ADDR_"])
            if "区区" in data["ADDR_"]:
                data["ADDR_"] = data["ADDR_"].replace("区区", "区")

        # 吉林省吉林市清洗
        if "吉林" in data["PROVINCE_NAME_"]:
            if "吉林市" not in data["CITY_"]:
                data["CITY_"] = data["CITY_"].replace("吉林省", "")
                data["CITY_"] = data["CITY_"].replace("吉林", "")
                data["CITY_CODE_"] = "220200"

        # 省级名称清洗
        for prov in province_list:
            if prov["CODE_"][:2] == data["PROVINCE_CODE_"][:2]:
                data["PROVINCE_CODE_"] = prov["CODE_"]
                data["PROVINCE_NAME_"] = prov["NAME_"]
                break

        # 市级清洗
        if data["PROVINCE_NAME_"][:2] in data["CITY_"]:
            if data["CITY_"] == '北京市' or data["CITY_"] == '天津市' or data["CITY_"] == '上海市' or data["CITY_"] == '重庆市':
                pass
            else:
                data["CITY_"] = data["CITY_"].replace(data["PROVINCE_NAME_"], "")
                data["CITY_"] = data["CITY_"].replace(data["PROVINCE_NAME_"][:-1], "")
                data["CITY_"] = data["CITY_"].replace(data["PROVINCE_NAME_"][:3], "")
                data["CITY_"] = data["CITY_"].replace(data["PROVINCE_NAME_"][:2], "")
        for city in city_list:
            if city["NAME_"] == "市辖区":
                continue
            elif city["CODE_"][:2] == data["PROVINCE_CODE_"][:2]:
                if city["CODE_"] == data["CITY_CODE_"]:
                    data["CITY_CODE_"] = city["CODE_"]
                    data["CITY_"] = city["NAME_"]
                    break
                elif (city["NAME_"][:2] == data["CITY_"][:2]) and (city["CODE_"] != data["CITY_CODE_"]):
                    data["CITY_CODE_"] = city["CODE_"]
                    data["CITY_"] = city["NAME_"]
                    break
                elif (city["NAME_"] in data["ADDR_"][:len(data["PROVINCE_NAME_"])+len(city["NAME_"])]) and (not data["CITY_"]):
                    data["CITY_CODE_"] = city["CODE_"]
                    data["CITY_"] = city["NAME_"]
                    break

        # 区县级清洗
        if data["PROVINCE_NAME_"][:2] in data["AREA_NAME_"]:
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["PROVINCE_NAME_"], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["PROVINCE_NAME_"][:-1], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["PROVINCE_NAME_"][:4], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["PROVINCE_NAME_"][:3], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["PROVINCE_NAME_"][:2], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["CITY_"], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["CITY_"][:-1], "")
            data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["CITY_"][:3], "")
            # data["AREA_NAME_"] = data["AREA_NAME_"].replace(data["CITY_"][:2], "")
            data["AREA_NAME_"] = data["AREA_NAME_"][:2].replace("地区", "") + data["AREA_NAME_"][2:]
        for area in area_list:
            if area["CODE_"][:2] == data["PROVINCE_CODE_"][:2]:
                if area["CODE_"] == data["AREA_CODE_"]:
                    data["AREA_NAME_"] = area["NAME_"]
                    data["AREA_CODE_"] = area["CODE_"]
                    break
                elif (area["NAME_"] == data["AREA_NAME_"]) and (area["CODE_"] != data["AREA_CODE_"]):
                    data["AREA_NAME_"] = area["NAME_"]
                    data["AREA_CODE_"] = area["CODE_"]
                    break
                elif ((area["NAME_"] in data["ADDR_"][:len(data["PROVINCE_NAME_"]) +
                      len(data["CITY_"]) + len(area["NAME_"])]) and (not data["AREA_NAME_"])):
                    data["CITY_CODE_"] = city["CODE_"]
                    data["CITY_"] = city["NAME_"]

        # 地址清洗
        # 地址中有省级和市级
        if (data["PROVINCE_NAME_"] in data["ADDR_"]) and (data["CITY_"] in data["ADDR_"]):
            addr_ = data["ADDR_"]

        # 地址中有省级没有市级
        elif (data["PROVINCE_NAME_"] in data["ADDR_"]) and (data["CITY_"] not in data["ADDR_"]):
            if data["CITY_"][:-1] in data["ADDR_"][:len(data["PROVINCE_NAME_"])+len(data["CITY_"])]:
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])] +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]):len(data["PROVINCE_NAME_"])+len(data["CITY_"])].
                         replace(data["CITY_"][:-1], data["CITY_"]) +
                         data["ADDR_"][len(data["PROVINCE_NAME_"])+len(data["CITY_"]):])
            elif data["CITY_"][:3] in data["ADDR_"][:len(data["PROVINCE_NAME_"])+len(data["CITY_"])]:
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])] +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]):len(data["PROVINCE_NAME_"]) +
                         len(data["CITY_"])].replace(data["CITY_"][:3], data["CITY_"]) +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]) + len(data["CITY_"]):])
            elif data["CITY_"][:2] in data["ADDR_"][:len(data["PROVINCE_NAME_"])+len(data["CITY_"])]:
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])] +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]):len(data["PROVINCE_NAME_"]) +
                         len(data["CITY_"])].replace(data["CITY_"][:2], data["CITY_"]) +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]) + len(data["CITY_"]):])
            else:
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])] +
                         data["CITY_"] + data["ADDR_"][len(data["PROVINCE_NAME_"]):])

        # 地址中没有省级有市级
        elif (data["PROVINCE_NAME_"] not in data["ADDR_"]) and (data["CITY_"] in data["ADDR_"]):
            if data["PROVINCE_NAME_"][:-1] in data["ADDR_"][:len(data["PROVINCE_NAME_"])]:
                if data["CITY_"] == "吉林市" and ("吉林省" not in data["ADDR_"]):
                    addr_ = data["PROVINCE_NAME_"] + data["ADDR_"]
                else:
                    addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])].
                             replace(data["PROVINCE_NAME_"][:-1], data["PROVINCE_NAME_"]) +
                             data["ADDR_"][len(data["PROVINCE_NAME_"]):])
            elif (data["PROVINCE_NAME_"][:3] in data["ADDR_"][:len(data["PROVINCE_NAME_"])]) and \
                    (data["CITY_"] in data["ADDR_"]):
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])].
                         replace(data["PROVINCE_NAME_"][:3], data["PROVINCE_NAME_"]) +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]):])
            elif (data["PROVINCE_NAME_"][:2] in data["ADDR_"][:len(data["PROVINCE_NAME_"])]) and\
                    (data["CITY_"] in data["ADDR_"]):
                addr_ = (data["ADDR_"][:len(data["PROVINCE_NAME_"])].
                         replace(data["PROVINCE_NAME_"][:2], data["PROVINCE_NAME_"]) +
                         data["ADDR_"][len(data["PROVINCE_NAME_"]):])
            else:
                addr_ = data["PROVINCE_NAME_"] + data["ADDR_"]

        # 地址中没有省级没有市级
        elif (data["PROVINCE_NAME_"] not in data["ADDR_"]) and (data["CITY_"] not in data["ADDR_"]):
            if data["CITY_"][:-1] in data["ADDR_"][:len(data["CITY_"])]:
                addr_ = (data["PROVINCE_NAME_"] +
                         data["ADDR_"][:len(data["CITY_"])].replace(data["CITY_"][:-1], data["CITY_"]) +
                         data["ADDR_"][len(data["CITY_"]):])
            elif data["CITY_"][:3] in data["ADDR_"][:len(data["CITY_"])]:
                addr_ = (data["PROVINCE_NAME_"] +
                         data["ADDR_"][:len(data["CITY_"])].replace(data["CITY_"][:3], data["CITY_"]) +
                         data["ADDR_"][len(data["CITY_"]):])
            elif data["CITY_"][:2] in data["ADDR_"][:len(data["CITY_"])]:
                addr_ = (data["PROVINCE_NAME_"] +
                         data["ADDR_"][:len(data["CITY_"])].replace(data["CITY_"][:2], data["CITY_"]) +
                         data["ADDR_"][len(data["CITY_"]):])
            else:
                addr_ = data["PROVINCE_NAME_"] + data["CITY_"] + data["ADDR_"]

        # 地址中有区县级
        if data["AREA_NAME_"] in addr_:
            pass
        # 直辖市
        elif data["CITY_CODE_"] == data["PROVINCE_CODE_"]:
            if data["AREA_NAME_"][:-1] in addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])]:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])].
                         replace(data["AREA_NAME_"][:-1], data["AREA_NAME_"]) +
                         addr_[len(data["PROVINCE_NAME_"])+len(data["AREA_NAME_"]):])
            elif data["AREA_NAME_"][:4] in addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])]:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"])].replace(data["AREA_NAME_"][:4], data["AREA_NAME_"]) +
                         addr_[len(data["PROVINCE_NAME_"])+len(data["AREA_NAME_"]):])
            elif data["AREA_NAME_"][:3] in addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])]:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])].
                         replace(data["AREA_NAME_"][:3], data["AREA_NAME_"]) +
                         addr_[len(data["PROVINCE_NAME_"])+len(data["AREA_NAME_"]):])
            elif data["AREA_NAME_"][:2] in addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])]:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"])].
                         replace(data["AREA_NAME_"][:2], data["AREA_NAME_"]) +
                         addr_[len(data["PROVINCE_NAME_"])+len(data["AREA_NAME_"]):])
            else:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"])] + data["AREA_NAME_"] +
                         addr_[len(data["PROVINCE_NAME_"]):])
        # 非直辖市
        elif (data["AREA_NAME_"] == "城区") or (data["AREA_NAME_"] == "郊区"):
            addr_ = addr_.replace(data["AREA_NAME_"], "")
        elif (data["AREA_NAME_"][:-1] in
              addr_[:len(data["PROVINCE_NAME_"]) + len(data["CITY_"]) + len(data["AREA_NAME_"])]):
            addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["CITY_"])+len(data["AREA_NAME_"])].
                     replace(data["AREA_NAME_"][:-1], data["AREA_NAME_"]) +
                     addr_[len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"]):])
        elif (data["AREA_NAME_"][:4] in
              addr_[:len(data["PROVINCE_NAME_"])+len(data["CITY_"])+len(data["AREA_NAME_"])]):
            addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["CITY_"]) + len(data["AREA_NAME_"])].
                     replace(data["AREA_NAME_"][:4], data["AREA_NAME_"]) +
                     addr_[len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"]):])
        elif (data["AREA_NAME_"][:3] in
              addr_[:len(data["PROVINCE_NAME_"])+len(data["CITY_"])+len(data["AREA_NAME_"])]):
            addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["CITY_"]) + len(data["AREA_NAME_"])].
                     replace(data["AREA_NAME_"][:3], data["AREA_NAME_"]) +
                     addr_[len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"]):])
        elif (data["AREA_NAME_"][:2] in
              addr_[:len(data["PROVINCE_NAME_"])+len(data["CITY_"])+len(data["AREA_NAME_"])]):
            addr_ = (addr_[:len(data["PROVINCE_NAME_"]) + len(data["CITY_"]) + len(data["AREA_NAME_"])].
                     replace(data["AREA_NAME_"][:2], data["AREA_NAME_"]) +
                     addr_[len(data["PROVINCE_NAME_"]) + len(data["AREA_NAME_"]):])
        else:
            if len(data["AREA_NAME_"]) > 3:
                addr_ = (addr_[:len(data["PROVINCE_NAME_"])+len(data["CITY_"])] +
                         data["AREA_NAME_"] + addr_[len(data["PROVINCE_NAME_"]) + len(data["CITY_"]):])

        # 剩余数据在数据库中无区县级
        if not addr_:
            if data["PROVINCE_NAME_"] not in data["ADDR_"][:len(data["PROVINCE_NAME_"])]:
                data["ADDR_"] = data["PROVINCE_NAME_"] + data["ADDR_"]
            if data["CITY_"] not in data["ADDR_"][:len(data["PROVINCE_NAME_"]) + len(data["CITY_"])]:
                data["ADDR_"] = (data["ADDR_"][:len(data["PROVINCE_NAME_"])] + data["CITY_"] +
                                 data["ADDR_"][len(data["PROVINCE_NAME_"]):])
            addr_ = data["ADDR_"]
            data["AREA_CODE_"] = data["CITY_CODE_"]

        if "直辖" in data["CITY_"]:
            addr_ = data["ADDR_"]

        # # 添加分行编码
        # branch_code = None
        # for i in range(1, 10000):
        #     branch_code = "ABC" + "_" + data["CITY_CODE_"] + "_" + "00000"
        #     branch_code = branch_code[:len(branch_code)-len(str(i))] + "{}".format(i)
        #     if branch_code in branch_code_list:
        #         continue
        #     else:
        #         branch_code_list.append(branch_code)
        #         break

        # re_data["_id"] = data["_id"]
        # "C"
        hash_m = hashlib.md5()
        hash_m.update(data["NAME_"].encode("utf-8"))
        hash_title = hash_m.hexdigest()
        re_data["ID_"] = (data["ENTITY_CODE_"] + "_" +
                          str(9999999999 - int(float(data["DEALTIME_"]))) + "_" + str(hash_title))
        re_data["BANK_CODE_"] = "ABC"
        re_data["BANK_NAME_"] = data["ENTITY_NAME_"][:-2]
        re_data["CREATE_TIME_"] = data["DATETIME_"]
        re_data["AREA_CODE_"] = data["AREA_CODE_"]
        re_data["UNIT_CODE_"] = "ABC" + "_" + data["CITY_CODE_"]

        # "F"
        re_data["ADDR_"] = addr_
        re_data["CITY_CODE_"] = data["CITY_CODE_"]
        re_data["CITY_"] = data["CITY_"]
        re_data["LAT_"] = data["LAT_"]
        re_data["LNG_"] = data["LNG_"]
        re_data["NAME_"] = data["NAME_"]
        re_data["PROVINCE_CODE_"] = data["PROVINCE_CODE_"]
        re_data["PROVINCE_NAME_"] = data["PROVINCE_NAME_"]
        re_data["DISTRICT_CODE_"] = data["AREA_CODE_"]
        re_data["DISTRICT_NAME_"] = data["AREA_NAME_"]
        re_data["ENTITY_CODE_"] = data["ENTITY_CODE_"]
        re_data["DEALTIME_"] = data["DEALTIME_"]
        re_data["URL_"] = data["URL_"]
        re_data["TEL_"] = ""
        re_data["BUSINESS_HOURS_"] = ""

        # "S"
        re_data["STATUS_1"] = "1"

        return re_data

# ENTITY_CODE_ + PERIOD_TIME_ + HASHLIB(NAME_)


def run():
    script = GenericScript(entity_code="ABCORGANIZE", entity_type="ORGANIZE_FINASSIST")
    mongo_data_list = script.data_from_mongo()

    province_list, city_list, area_list, dir_area_list = script.area_from_mysql()

    batch_list = data_shuffle(mongo_data_list, province_list, city_list, area_list)


if __name__ == '__main__':
    run()
