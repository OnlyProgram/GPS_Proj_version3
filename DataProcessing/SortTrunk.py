
"""
涉及：车牌提取，文件分割，提取每辆车GPS记录
"""

"""
将车牌号按照其GPS记录数排序
参数解释：
Path:传入待处理文件路径，如：H:\GPS_Data\20170901.csv
sortpath: 传入排序后的字典保存路径
toppath：提取的前百分之20的车牌字典保存路径
percent:提取比例，默认为5，提取的是20%，可更改
"""
import pandas as pd
import json
import os

def Save_Trunk_GPS(readpath,savepath,savefilename,topname,percent=5):
    """
    #读数据，统计车辆GPS坐标数的排名
    :param readpath: 待统计文件路径 如：D:\postgraduate-2017-2020\Data_set\GPS\Top200w\Top200w.csv
    :param savepath: 保存路径：D:\postgraduate-2017-2020\Data_set\GPS\Top200w
    :param savefilename: 保存的文件名
    :param topname: 提取排序好的前*% 文件名
    :param percent:默认为5，即提取前20%
    :return:
    """
    try:
        chunker = pd.read_csv(readpath, chunksize=2000000,
                              header=None, usecols=[0])  # 分块读取 每一块100万条数据,如果不加header=None 第一行会被当做索引，而不被处理
        truck_dict = {}  # 存储车牌号及其对应的GPS坐标数量
        dictdata = {}  # 存储返回的前20%的车牌号
        for df in chunker:
            df.columns = ['']
            for num in df.iloc[:, 0]:
                if num not in truck_dict:
                    truck_dict[num] = 1
                else:
                    truck_dict[num] += 1
        trunk_lists = sorted(truck_dict.items(), key=lambda x: x[1], reverse=True)
        for l in trunk_lists[:int(len(trunk_lists) / percent)]:
            dictdata[l[0]] = l[1]
        dt = dict(trunk_lists)
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        fname1 = savefilename + ".json"
        fname2 = topname + ".json"
        Files = open(os.path.join(savepath,fname1), 'w')
        File = open(os.path.join(savepath,fname2), 'w')
        js = json.dumps(dt,indent=4)
        Files.write(js)
        File.write(json.dumps(dictdata,indent=4))
        Files.close()
        File.close()
        print("车牌号按照坐标数量排序完成 ")
        print("前{}%提取完成".format(100.0/percent))

        """
        #读
        with open(r"H:\GPS_Data\Trunk_GPS_Sort.json",'r') as load_f:
        load_dict = json.load(load_f)
        print(len(load_dict))
        """
    except Exception as e:
        print(e)
"""
#按坐标数排序，并提取前20%（可设定）
reapath = "H:\GPS_Data\\20170901\\20170901.csv"
sapath = "H:\GPS_Data\\20170901"
Save_Trunk_GPS(reapath,sapath,"All20170901_Trunk_Sort","Top20Sort")
"""


def Get_top_trunk_list(path):
    """
    :param path:  json文件,前20%车牌号json文件路径
    :return: 返回前20%车牌号列表
    """
    Trunk_list = []
    with open(path, 'r') as file:
        strs = file.read()
        Trunk_dict = json.loads(strs)
    for key in Trunk_dict.keys():
        Trunk_list.append(key)
    return Trunk_list