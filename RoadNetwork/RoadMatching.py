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
import os
from RoadNetwork import Common_Functions
from RoadNetwork import MapNavigation
import copy
import time
def FindPointCandidateWay():
    """
    找出坐标点的候选路段，此部分已经通过角度（大于90）、距离（大于40米）筛除一部分候选路段
    :return:
    """
    # 读时间 经纬度 网格编号
    df = pd.read_csv("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv",
                     header=None, usecols=[1, 2, 3, 4, 5])
    points_num = df.shape[0]  # 坐标数量
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # print(df.iloc[:,1:4])
    drop_list = []  # 要删除的索引列表
    for row in range(1, points_num):
        if row == points_num:
            break
        points_dis = Common_Functions.haversine(df.iloc[row, 1], df.iloc[row, 2], df.iloc[row - 1, 1],
                                                df.iloc[row - 1, 2])  # 相邻坐标点之间的距离
        if points_dis < 0.01:  # 距离小于10米
            drop_list.append(row)
    # print(drop_list)
    newdf = df.drop(drop_list)  # 删除相邻点在10米之内的点
    # print(newdf.iloc[:,1:3])
    newdf = newdf.reset_index(drop=True)
    file = open(
        "H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')
    print("本车辆共查找坐标点数为：{}".format(newdf.shape[0]))
    for row in range(newdf.shape[0]):
        if row == 0:
            # print("处理起始坐标点{}".format([df.iloc[row, 2],df.iloc[row, 3],df.iloc[row + 1,2],df.iloc[row + 1, 3]]))
            dic = Common_Functions.Find_Candidate_Route(
                [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]],
                [newdf.iloc[row + 1, 1], newdf.iloc[row + 1, 2], newdf.iloc[row + 1, 3], newdf.iloc[row + 1, 4]],
                flag=1)
            if dic:  # 有候选路段才保存
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
        elif row == newdf.shape[0] - 1:
            # print("处理终点坐标点{}".format([df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
            dic = Common_Functions.Find_Candidate_Route(
                [newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]],
                [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]], flag=2)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
        else:
            dis1 = Common_Functions.haversine(newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row - 1, 1],
                                              newdf.iloc[row - 1, 2])
            dis2 = Common_Functions.haversine(newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row + 1, 1],
                                              newdf.iloc[row + 1, 2])
            # 找相邻最近的点做为轨迹方向
            if dis2 > dis1:
                # print("处理终点坐标点{}".format([df.iloc[row-1, 2], df.iloc[row-1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]],
                    [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]], flag=2)

            else:
                # print("处理起始坐标点{}".format([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row + 1, 2], df.iloc[row + 1, 3]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]],
                    [newdf.iloc[row + 1, 1], newdf.iloc[row + 1, 2], newdf.iloc[row + 1, 3], newdf.iloc[row + 1, 4]],
                    flag=1)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
    file.close()
def SelectFinalRoute(candidatewaypath,savefinalroutespath,savefilename):
    """
    根据坐标点的候选路段选出路网的匹配路线
    保存格式为：车辆名：路线（如果不确定，可能为多条），车辆名为txt文件名
    :param candidatewaypath:  坐标点候选路段的txt文件路径，如H:\\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt
    :param savefinalroutespath: 路线保存路径
    :param savefilename: 最终路线保存的文件名
    :return:
    """
    file = open(
        "H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')
    savetxtfilename = savefilename + ".txt"
    (tempath, tempfilename) = os.path.split(candidatewaypath)  # tempfilename为txt文件名（包含后缀）
    (trunkname, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    with open(candidatewaypath) as candidatewayfile:
        filelines = candidatewayfile.readlines()
        linesnum = len(filelines)
        finalline = []     #存储最终路线，可能为多条，随着坐标点的迭代，会变化，直到处理完最有一个坐标点
        for key in eval(filelines[0].strip('\n').split(">>>")[-1]).keys():
            finalline.append([key])
        #print(finalline)
        # 遍历每个坐标点的候选路段
        print("需要处理坐标数为：{}".format(linesnum))
        for lineindex in range(1,linesnum):
            #print(eval(filelines[lineindex].strip('\n').split(">>>")[-1]))
            templine = []   #存储临时路线
            # 遍历到最后一行
            if lineindex == linesnum - 1:
                break
            else:
                print("处理路段{}".format(eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
                for subline in finalline:
                    for key in eval(filelines[lineindex].strip('\n').split(">>>")[-1]).keys():
                        temsubline = []
                        #print("路段{}匹配key{}".format(subline[-1], key))
                        # 只需要查看subline的最后一个路段与路段key是否连通即可，因为subline的连通性是通过测试的
                        connectroute = MapNavigation.waytoway(subline[-1], key)  # 为列表
                        if connectroute:
                            temsubline = copy.deepcopy(subline)
                            temsubline.append(key)  # 只加入轨迹点所属路段，而不加入这两个路段走通的路线
                            templine.append(temsubline)
                        else:
                            #此路线不连通，舍弃当前路段key
                            pass
                        """
                        #此代码块是加入完整路线
                        if subline[-1] == key:
                            temsubline = copy.deepcopy(subline)
                            templine.append(temsubline)
                        elif connectroute:
                            #路段可连通
                            temsubline = copy.deepcopy(subline)
                            temsubline.extend(connectroute[1:])   #将走通的路线加入到子路线，扩展当前路线
                            templine.append(temsubline)
                        else:pass
                        """

                        #print(temsubline)
                        #print(templine)

            finalline.clear()
            finalline = templine
            #finalline = Common_Functions.Double_layer_list(templine)  #去重
            #finalline = Common_Functions.Sequential_subset(finalline)  #去除前缀（两个及以上）
            #print(finalline)
            print(len(finalline))
            file.write(str(finalline)+"\n")
            file.flush()
        print("共选出{}条路".format(len(finalline)))
        print(finalline)

starttime = time.time()
SelectFinalRoute("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt",
                 "H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes","final")
print("耗时：{}".format(time.time()-starttime))


