# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 19:18
# @Author  : WHS
# @File    : RoadMatching.py
# @Software: PyCharm
"""
此模块不采用滑动窗口式方法
思路：
（1）选出所有点的候选路段
（2）根据车的行驶方向减少候选路段
"""
import pandas as pd
from RoadNetwork import Common_Functions
#读时间 经纬度 网格编号
df = pd.read_csv("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv",header=0,usecols=[1,2,3,4,5])
points_num = df.shape[0]  #坐标数量
for index in range(points_num):
    if index > 0:
        points_dis = Common_Functions.haversine(df.iloc[index,1], df.iloc[index,2],df.iloc[index-1,1], df.iloc[index-1,2]) #相邻坐标点之间的距离
        if points_dis < 0.01:  #距离小于10米
            continue
        else:pass


