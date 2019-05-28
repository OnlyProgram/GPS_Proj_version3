# -*- coding: utf-8 -*-
# @Time    : 2019/5/9 9:29
# @Author  : WHS
# @File    : SimilarFilledRoute.py
# @Software: PyCharm

# -*- coding: utf-8 -*-
# @Time    : 2019/4/26 20:11
# @Author  : WHS
# @File    : FilledRoute_text.py
# @Software: PyCharm
"""
此文件为轨迹分类的补点策略，并完整生成补点文件（完整轨迹）
"""
from functools import reduce
import pandas as pd
import os
import numpy as np
from math import radians, cos, sin, asin, sqrt
def findcsvpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".csv"):
                ret.append(de_path)
    return ret
def findtxtpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".txt"):
                ret.append(de_path)
    return ret
def haversine(lon1, lat1, lon2, lat2):
    """
    :param lon1: 第一个点经度
    :param lat1: 第一个点纬度
    :param lon2: 第二个点经度
    :param lat2: 第二个点纬度
    :return: 返回距离，单位公里
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r
def Trajectory_Similar(tra1,tra2):
    """
    求两个轨迹的相似度
    :param tra1:轨迹1的坐标集合[[],[]]
    :param tra2: 轨迹2的坐标集合[[],[]]
    :return: 返回相似度
    """
    distance1,distance2 = [],[]

    for coor1 in tra1:
        min = float('inf')
        for coor2 in tra2:
            tem_dis = haversine(coor1[0],coor1[1],coor2[0],coor2[1])
            if tem_dis < min:
                min =tem_dis
        distance1.append(min)
    distance1_mean =  np.array(distance1).mean()

    for coor2 in tra2:
        min = float('inf')
        for coor1 in tra1:
            tem_dis = haversine(coor1[0],coor1[1],coor2[0],coor2[1])
            #print(tem_dis)
            if tem_dis < min:
                min =tem_dis
        distance2.append(min)
    distance2_mean = np.array(distance2).mean()
    return max(distance1_mean,distance2_mean)

meshed_path = "H:\GPS_Data\\20170901\Top20\Meshed"   #前20%车辆网格化的文件路径
def FindAllRouteSimilar(dic):
    #Alldf = pd.DataFrame(None)
    Similarity = {}
    for key in dic.keys():
        tem_dic = {}
        coordinate1 = []
        filename = key + ".csv"
        df = pd.read_csv(os.path.join(meshed_path, filename), header=None, usecols=[2, 3], names=[0, 1])
        df = df.iloc[dic[key][2][0]:dic[key][2][1] + 1, :]
        for row in range(df.shape[0]):
            tem = [df.iloc[row, 0], df.iloc[row, 1]]
            coordinate1.append(tem)
        #Alldf = pd.concat([Alldf, df], ignore_index=True)
        for key2 in dic.keys():
            if key2 == key:
                tem_dic[key2] = 0
            else:
                coordinate2 = []
                filename = key2 + ".csv"
                df = pd.read_csv(os.path.join(meshed_path, filename), header=None, usecols=[2, 3], names=[0, 1])
                df = df.iloc[dic[key2][2][0]:dic[key2][2][1] + 1, :]
                for row in range(df.shape[0]):
                    tem = [df.iloc[row, 0], df.iloc[row, 1]]
                    coordinate2.append(tem)
                tem_dic[key2] = Trajectory_Similar(coordinate1, coordinate2)

        Similarity[key] = tem_dic
    return Similarity  #返回所有此路段相似路段的相似度字典，

def FindRouteNumber(threshold_value = 1):
    """
    :param dic 待补路段字典
    :param trunknum 待补车辆车牌号
    :param startend 待补车辆待补路段的起终点坐标及其对应的网格坐标
    :param threshold_value 相似性阈值 小于此值，判定为这两条线路为同一条线
    :param savename 如果待补路段出现多类路线，存储多类路线的具体坐标文件名
    统计待补路段中与其相似的路段数目，如待补路段的通过AB两点，但是与其相似的为10条路线，统计10条路线可归并
    为几类线路并统计出每类路线含有几条线路
    :return:返回被选中的车辆列表
    """
    AllSimilar = FindAllRouteSimilar(dic)  #记录所有补路段的相互相似程度
    #print(AllSimilar)
    Routes = []  #存储路线，格式为[[]],一类为一个子列表
    key_lis = list(AllSimilar.keys())
    for key in AllSimilar.keys():
        flag = 0
        for li in Routes:
            if key in li:
                flag = 1
        if flag == 0:
            tem_routes = []
            for key2 in AllSimilar[key]:
                flag1 = 0
                for li in Routes:
                    if key2 in li:
                        flag1 = 1
                if flag1==0:
                    if AllSimilar[key][key2] < threshold_value:
                        tem_routes.append(key2)
                        key_lis.remove(key2)
                else:pass
            Routes.append(tem_routes)
        else:pass
    print("可分为线路类别为：{}".format(len(Routes)))
    if len(Routes) > 1:
        """
        #此代码块为可视化观察轨迹分类的可靠性，后期调试完毕可删除
        All_df = pd.DataFrame(None)  # 记录所有的补充点，此行以下为可视化查看
        class_flag = 1  # 标记路线类别
        for route_class in Routes:  # 遍历线路类别
            for trunk in route_class:  # 遍历每个路线类别下的具体路线
                trunkfilename = trunk + ".csv"
                df = pd.read_csv(os.path.join('H:\GPS_Data\\20170901\Top20\Meshed', trunkfilename), header=None,
                                 usecols=[2, 3], names=[0, 1])
                df = df.iloc[dic[trunk][2][0]:dic[trunk][2][1] + 1, :]  # 一个路段的补点
                df[2] = class_flag
                All_df = pd.concat([All_df, df], ignore_index=True)
            class_flag += 1
        All_df.loc[All_df.shape[0]] = [startend[0][0],startend[0][1],0]#待补路段起点终点标记
        All_df.loc[All_df.shape[0]] = [startend[0][2],startend[0][3],0]  # 待补路段起点终点标记
        savetrunkclassfilename = savename+ ".csv"  #
        Originalfilename = trunknum + ".csv"
        Originaldf = pd.read_csv(os.path.join('H:\GPS_Data\\20170901\Top20\Meshed',Originalfilename),header=None,usecols=[2, 3], names=[0, 1])#待补车辆的原始数据
        Originaldf[2] = -1  #标记为原始点
        All_df = pd.concat([All_df,Originaldf],ignore_index=True)
        All_df.to_csv(os.path.join('H:\GPS_Data\\20170901\Top20\classRoute', savetrunkclassfilename), index=0, header=0)
        """
        class_max_num = 0   #记录类别中的最大轨迹数
        print(Routes)
        Final_select_class = 0  #记录最终被选出的路线类别
        for class_index in range(len(Routes)):  # 遍历线路类别，找出含有轨迹最多数目的类别
            if len(Routes[class_index]) > class_max_num:
                Final_select_class = class_index
                class_max_num = len(Routes[class_index])
        return Routes[Final_select_class],True
    else:
        return Routes[0],False


FilledList = findtxtpath("H:\GPS_Data\\20170901\Top20\SimilarArea")
for singleFile in FilledList:
    trunknum = str(os.path.split(singleFile)[-1]).split('SimilarAreas.txt')[0] # 待补车辆车牌号

    if trunknum == "4e3dae9e-6dc6-4fe0-875d-dc29af45ab5b":
        with open(singleFile, 'r') as file:
            AllFilledpoint = pd.DataFrame(None)  # 记录所有路段的补充点
            for line in file.readlines():  # 一行为一个路段，即此循环为补一个车辆
                if line.strip():
                    tem_list = line.strip('\n').split("的相似区域为:")
                    startend = eval(tem_list[0])[0]  # 首先转换为列表，再取出起点终点坐标
                    dic = eval(tem_list[1])
                    print("************路段{}的补充路段有以下几类路线可补*************".format(tem_list[0]))
                    print(dic)
                    Candidate_Trunk_num,class_flag = FindRouteNumber()   #接受被选中的车辆列表,class_flag为Ttrue代表轨迹分为两类以上
                    if class_flag:
                        new_dic = {}
                        print(Candidate_Trunk_num)
                        for key, value in dic.items():
                            if key in Candidate_Trunk_num:
                                new_dic[key] = value
                            else:
                                pass
                        del dic
                        dic = new_dic
                        print(dic)
                    else:
                        print(dic)
                    RoutePoint = pd.DataFrame(None)  # 路段的所有补点
                    order_key_dic = {}
                    for key in dic.keys():  # 此循环为补充一个路段
                        order_key_dic[key] = dic[key][2][1] - dic[key][2][0] + 1  # 被选中的相似区域坐标数

                    order_key_dic = dict(sorted(order_key_dic.items(), key=lambda x: x[1], reverse=True))  # 降序
                    # 开始迭代补点
                    totalFillPoints = 0
                    for seckey in order_key_dic.keys():
                        totalFillPoints += order_key_dic[seckey]
                        tem_num = seckey
                        csvfile = tem_num + ".csv"
                        singleTrunkpath = os.path.join(meshed_path, csvfile)  # 打开补点文件
                        df = pd.read_csv(singleTrunkpath, header=None, usecols=[2, 3], names=[0, 1])  # 读经纬度
                        df = df.iloc[dic[tem_num][2][0]:dic[tem_num][2][1] + 1, :]  # 一个路段的补点
                        RoutePoint = pd.concat([RoutePoint, df], ignore_index=True)
                        if totalFillPoints >= 10:   #10为阈值   0.5-1公里之间补点数要大于10
                            break
                        else:
                            pass
                    # print(RoutePoint)
                    RoutePoint = RoutePoint.reset_index(drop=True)  # 重置索引,并删除之前的索引
                    RoutePoint[2] = 2  # 标记  2 表示补充点
                    RoutePoint.loc[RoutePoint.shape[0]] = [startend[0], startend[1],1]#待补路段起点终点标记  # 加入路段起始坐标  标记为1 代表起点终点坐标
                    RoutePoint.loc[RoutePoint.shape[0]] = [startend[2], startend[3],1]
                    # print(RoutePoint)
                    AllFilledpoint = pd.concat([AllFilledpoint, RoutePoint], ignore_index=True)
            Originalfilename = trunknum + ".csv"
            df = pd.read_csv(os.path.join('H:\GPS_Data\\20170901\Top20\Meshed', Originalfilename), header=None,
                                     usecols=[2, 3], names=[0, 1])  # 待补车辆的原始数据
            df = df.reset_index(drop=True)
            df[2] = 0  # 标记为原始点
            df = pd.concat([df, AllFilledpoint], ignore_index=True)
            Filledcsvname = trunknum +".csv"
            df.to_csv(os.path.join('H:\GPS_Data\\20170901\Top20\AllFilled\\SimilarFilled', Filledcsvname), index=0,
                      header=0)  # 补点文件和原始文件合并后保存路径
    else:pass

