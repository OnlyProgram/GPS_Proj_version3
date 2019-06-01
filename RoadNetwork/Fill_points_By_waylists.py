# -*- coding: utf-8 -*-
# @Time    : 2019/5/28 15:40
# @Author  : WHS
# @File    : Fill_points_By_waylists.py
# @Software: PyCharm
"""
根据最终的路线，选出路线中的点，如果此路线不通，会出错
"""
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
                First_intersection_index = 0   #路段第一个交点在路段中的索引号,此时First_intersection_index还是None
            else:
                First_intersection_index = nodelist.index(First_intersection)
            Second_intersection_index = nodelist.index(Second_intersection) #第二个坐标交点
            AllNodeIDLists.extend(nodelist[First_intersection_index:Second_intersection_index+1])
            First_intersection = Second_intersection
    for node in AllNodeIDLists:
        node_coordinate = Road_matching.Get_Coordinate(node)
        if 116.3906755<node_coordinate[0]<116.4958043 and 39.6905694<node_coordinate[1]<39.7506401:  #此范围为北野场桥扩大区域的范围
            AllNodeLists.append(node_coordinate)
    return AllNodeLists
#waylists = [403874395, 403874396,318323104,466289455,466289456,606768164,606768158,606768162] #测试,0d201cd1-0a18-43c0-9e16-f10f62833dd9
#waylists = [403874396, 318323104, 466289455, 466289456, 606768164, 606768158, 606768162, 466839079, 606769458, 466839081] #334e4763-f125-425f-ae42-8028245764fe
#waylists = [169644553, 47574802, 47574526, 210697572, 318323104, 47574640, 210697630, 152616721, 29136296, 47574560]
waylists = [242945738, 242945782, 317913828, 242945739, 47574648, 242945750, 242945783, 242945771, 239743243, 117082584, 466289460, 606768166, 152616724, 47574782, 42500477, 242945798, 403874394, 47574807, 47574526, 47574777, 403874395, 403874396, 210697572, 318323104, 47574640]
def Judge_Route_connectivity(waylists:list):
    """
    判断一条路的连通性，如果不连通，则将其拆分为连通的几个部分
    :param waylists:
    :return:
    """
    All_routes = []  #存储所有的子连通路线
    subRoute = []  #存储子路线
    for index in range(len(waylists)):
        if index == len(waylists)-1:
            break
        intersection = map_navigation.TwoWay_intersection(waylists[index], waylists[index + 1]) #此两个路段的连通性
        if intersection:
            subRoute.extend([waylists[index], waylists[index + 1]])
        else:
            if len(subRoute)==0:    #此情况是子连通路线中只有一个路段，但是subRoute会为空，所以这里要加入waylists[index]
                subRoute.append(waylists[index])
            new_list = list(set(subRoute))
            new_list.sort(key=subRoute.index)
            All_routes.append(new_list)
            #print(All_routes)
            subRoute = []
    if len(subRoute)!=0:
        new_list = list(set(subRoute))
        new_list.sort(key=subRoute.index)
        All_routes.append(new_list)
    return All_routes
AllRoutes = Judge_Route_connectivity(waylists)
print(AllRoutes)
AllNodeLists = []   #路线中所有的坐标点
for subline in  AllRoutes:
    AllNodeLists.extend(Fill_coordinate_By_Routes(subline))
Road_matching.list2kml(AllNodeLists, "text","H:\GPS_Data\Road_Network\BYQBridge\KML\PartTrunksAreaKml")  # 列表转kml  测试用例
