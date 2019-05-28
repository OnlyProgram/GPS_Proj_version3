# -*- coding: utf-8 -*-
# @Time    : 2019/4/17 21:41
# @Author  : WHS
# @File    : csv2db.py
# @Software: PyCharm
from pymongo import MongoClient
import csv
import os
import json
import pandas as pd
import time
import  datetime
from DataProcessing import SortTrunk
# 1:连接本地MongoDB数据库服务
conn=MongoClient("localhost")
# 2:连接本地数据库(guazidata)。没有时会自动创建
db=conn.GPSData
# 3:创建集合
#myset=db.totaldata

# 4:看情况是否选择清空(两种清空方式，第一种不行的情况下，选择第二种)
#第一种直接remove
#myset.remove(None)
#第二种remove不好用的时候
# set1.delete_many({})
def Insert(insertpath,collection):
    """
    :param insertpath: 要保存到数据库的文件路径，如：H:\GPS_Data\\20170901\\20170901.csv
    :return:
    """
    myset = db[collection]
    myset.remove(None)
    counts = 0  # 记录添加记录数
    chunker = pd.read_csv(insertpath, chunksize=2000000, header=None,
                          names=['TrunkNumber', 'Time', 'lon',
                                 'lat','x_grid','y_grid'])  # 分块读取 每一块200万条数据,如果不加header=None 第一行会被当做索引，而不被处理
    for df in chunker:

        for index, row in df.iterrows():
            row['TrunkNumber'] = str(row['TrunkNumber'])
            row['Time'] = str(row['Time'])
            row['lon'] = float(row['lon'])
            row['lat'] = float(row['lat'])
            row['x_grid'] = int(row['x_grid'])
            row['y_grid'] = int(row['y_grid'])
            row_dict = {"TrunkNumber": row['TrunkNumber'], "Time": row['Time'], "lon": row['lon'], "lat": row['lat'],"x_grid":row['x_grid'],
                        "y_grid":row['y_grid']}
            myset.insert(row_dict)
            counts += 1
    print('成功添加了' + str(counts) + '条数据 ')
def Inquire(Trunknumber_lists,savepath,collection):
    myset = db[collection]
    flag = 0
    starttime = 0
    for number in Trunknumber_lists:
        starttime = time.time()
        flag += 1
        fname = number + ".csv"
        results = myset.find({'TrunkNumber':number})
        with open(os.path.join(savepath, fname), 'a', newline='') as csvfile:
            fileheader = ["TrunkNumber", "TIme", "lon", "lat"]
            dict_writer = csv.DictWriter(csvfile,fileheader)
            #dict_writer.writeheader()  #不加文件头
            for result in results:
                del result['_id']
                dict_writer.writerow(result)
        print("处理第{}辆车数据时间消耗为：{}".format(flag,datetime.timedelta(seconds=(time.time()-starttime))))
"""
lis =SortTrunk.Get_top_trunk_list("H:\GPS_Data\\20170901\\Top20Sort_part1.json")
print("此部分共计{}辆车".format(len(lis)))
start = time.time()
Inquire(lis,"H:\GPS_Data\\20170901\Top20")
print("总共消耗时间为：{}".format(datetime.timedelta(seconds=(time.time()-start))))
"""