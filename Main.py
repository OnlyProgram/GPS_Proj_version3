# -*- coding: utf-8 -*-
# @Time    : 2019/4/22 13:15
# @Author  : WHS
# @File    : Main.py
# @Software: PyCharm
"""
步骤：
1、异常处理：时间异常，地点异常
2、网格化
3、存数据库，提取前20%车辆（提取出后，删除不重复坐标点数<500的车辆）
4、（时间排序）提取待补路段
5、找到相似区域
6、轨迹补点
（1,2步合成一步）
"""
import pandas as pd
from DataProcessing import Data_process
from DataProcessing import SortTrunk
from DataProcessing import csv2db
def main():
    #df = pd.DataFrame({'A': [1, 2, 3], 'B': [1, 1, 1]})
    #print(df.iloc[:,0].nunique())
    path = "H:\GPS_Data\\20170901\Top20\Top20Trunk/0dd1b47d-f845-48d6-b5bb-105d9160cf54.csv" #待网格化文件
    spath = "H:\GPS_Data\\20170901\Top20\Top20Meshed" # 网格化后文件保存路径
    name = "0dd1b47d-f845-48d6-b5bb-105d9160cf54"# 网格化后文件名
    #异常值处理及网格化，异常值处理只处理时间异常（默认异常时间为2000-2099之外的时间）和不在北京地区的坐标
    Data_process.Meshing(path, spath, name)

    # 按坐标数排序，并提取前20%（可设定）
    reapath = "H:\GPS_Data\\20170901\\20170901.csv" #待排序总表
    sapath = "H:\GPS_Data\\20170901" #坐标数目排序字典保存路径
    Sortname = "All20170901_Trunk_Sort"  #排序后的文件名，默认json格式
    Topname = "Top20Sort"  #提取的前20%（默认）文件名，默认json,如需修改提取比例，修改参数percent
    SortTrunk.Save_Trunk_GPS(reapath, sapath,Sortname ,Topname,percent=5)

    #csv文件存入mongodb数据库
    """
    #csvpath 为网格化后的数据，collection为mongodb集合名，如果不存在会自动创建
    注意：如果输入已存在集合，会删除当前数据！！！！！！！！！
    """
    #csv2db.Insert(csvpath,collection)
    """
    #提取前20%车辆对应坐标
    lis =SortTrunk.Get_top_trunk_list("H:\GPS_Data\\20170901\\Top20Sort_part1.json")
    print("此部分共计{}辆车".format(len(lis)))
    start = time.time()
    Inquire(lis,"H:\GPS_Data\\20170901\Top20"，collection)
    print("总共消耗时间为：{}".format(datetime.timedelta(seconds=(time.time()-start))))
    """

if __name__ == '__main__':
    main()