# -*- coding: utf-8 -*-
# @Time    : 2019/5/14 15:48
# @Author  : WHS
# @File    : Extract_Area.py
# @Software: PyCharm
"""
提取指定区域的车辆
北野场桥：
116.4244311388,116.4564598279
39.7103429034,39.7314934567
"""
import pandas as pd
import os
from FillGPSTrack import FillTrajectory as FT
import pymysql
def ExtractArea(minlon,minlat,maxlon,maxlat,SavePath,savefilename,MeshPath):
    """
    提取经过指定区域的车辆
    :param minlon:最小经度
    :param minlat:最小纬度
    :param maxlon:最大经度
    :param maxlat:最大纬度
    :param SavePath:文件保存路径,文件名默认为ExtraArea.txt
    :param MeshPath:网格化后文件路径
    :return:
    """
    if os.path.isfile(MeshPath):
        print("最后一个参数应该为目录")
    if not os.path.isdir(SavePath):
        os.mkdir(SavePath)
    csvfilelist = FT.findcsvpath(MeshPath)  #接收该文件夹下的所有csv文件
    SaveFilepath = SavePath + os.sep + savefilename + ".txt"
    print("开始提取经过此区域的车辆......")
    from tqdm import tqdm
    for i in tqdm(range(len(csvfilelist))):
        df = pd.read_csv(csvfilelist[i], header=None, usecols=[0, 1, 2, 3], low_memory=False)
        # df = df.dropna(axis=0, how='any')  # 删除表中含有任何NaN的行 ,subset=[1]可添加 只关注时间这一列，不添加也会处理其他列为空的行
        df = df[(df.iloc[:, 2] < maxlon) & (df.iloc[:, 2] > minlon) & (df.iloc[:, 3] < maxlat) & (
                df.iloc[:, 3] > minlat)]  # 筛选坐标

        if df.shape[0] > 0:
            with open(SaveFilepath, 'a') as file:
                file.write(csvfilelist[i]+"\n")
        else:pass
    print("经过指定区域的车辆提取完成，已保存到如下路径：{}".format(SaveFilepath))


minlon,maxlon = 116.4244311388,116.4564598279
minlat,maxlat = 39.7103429034,39.7314934567
SavePath = "H:\GPS_Data\Road_Network\BYCBridge\Trunks"
Meshedpath = "H:\GPS_Data\\20170901\Top20\Meshed"
#ExtractArea(minlon,minlat,maxlon,maxlat,SavePath,"BYC",Meshedpath)



