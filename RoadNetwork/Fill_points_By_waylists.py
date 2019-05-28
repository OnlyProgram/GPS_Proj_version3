# -*- coding: utf-8 -*-
# @Time    : 2019/5/28 15:40
# @Author  : WHS
# @File    : Fill_points_By_waylists.py
# @Software: PyCharm
from RoadNetwork import Road_matching
from RoadNetwork import map_navigation
def Fill_coordinate_By_Routes(waylists:list):
    """
    根据最终的waylist求出路网坐标点
    :param waylists 路线中路段列表，以车辆"003b5b7e-e72c-4fc5-ac6d-bcc248ac7a16"经过北野场桥为例
    [437527026, 466289459, 466289461, 466289460, 606768166, 152616724]
    :return:
    """
    AllNodeLists = []  #道路坐标列表
    AllNodeIDLists = []  #道路坐标点编号列表
    First_intersection = None #第一个交点
    for index in range(len(waylists)):
        if index == len(waylists)-1:
            break
        else:
            Second_intersection = map_navigation.TwoWay_intersection(waylists[index],waylists[index+1])[0][0]  #两条路交点,TwoWay_intersection返回的为元组，如（（1213）,）
            nodelist = Road_matching.Get_way_nodes(waylists[index])  #获得该路段的所有坐标点
            if index==0:
                First_intersection_index = 0   #路段第一个交点在路段中的索引号
            else:
                First_intersection_index = nodelist.index(First_intersection)
            Second_intersection_index = nodelist.index(Second_intersection) #第二个坐标交点
            AllNodeIDLists.extend(nodelist[First_intersection_index:Second_intersection_index+1])
            First_intersection = Second_intersection
    for node in AllNodeIDLists:
        node_coordinate = Road_matching.Get_Coordinate(node)
        if 116.3906755<node_coordinate[0]<116.4958043 and 39.6905694<node_coordinate[1]<39.7506401:  #此范围为北野场桥扩大区域的范围
            AllNodeLists.append(node_coordinate)
    Road_matching.list2kml(AllNodeLists,"text","H:\GPS_Data\Road_Network\BYQBridge\KML\TrunksAreakml")  #列表转kml  测试用例
waylists = [437527026, 466289459, 466289461, 466289460, 606768166, 152616724] #测试

Fill_coordinate_By_Routes(waylists)