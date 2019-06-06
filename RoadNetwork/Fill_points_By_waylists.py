# -*- coding: utf-8 -*-
# @Time    : 2019/5/28 15:40
# @Author  : WHS
# @File    : Fill_points_By_waylists.py
# @Software: PyCharm
"""
根据最终的路线，选出路线中的点，如果此路线不通，会分段处理
"""
from RoadNetwork import Road_matching
from RoadNetwork import MapNavigation
import os
def del_adjacent(alist):
    """
    删除相邻重复元素
    :param alist:
    :return:
    """
    for i in range(len(alist) - 1, 0, -1):
         if alist[i] == alist[i-1]:
             del alist[i]
def Fill_coordinate_By_Routes(waylists:list):
    """
    根据最终的waylist求出路网坐标点   传入的列表是要是已经连通好的路线
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
            Second_intersection = MapNavigation.TwoWay_intersection(waylists[index],waylists[index+1])[0][0]  #两条路交点,TwoWay_intersection返回的为元组，如（（1213）,）
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
        intersection = MapNavigation.TwoWay_intersection(waylists[index], waylists[index + 1]) #此两个路段的连通性
        if intersection:
            subRoute.extend([waylists[index], waylists[index + 1]])
        else:
            if len(subRoute)==0:    #此情况是子连通路线中只有一个路段，但是subRoute会为空，所以这里要加入waylists[index]
                subRoute.append(waylists[index])
            #new_list = list(set(subRoute))
            #subRoute.sort(key=subRoute.index)
            del_adjacent(subRoute)

            All_routes.append(subRoute)
            #print(All_routes)
            subRoute = []
    if len(subRoute)!=0:
        #new_list = list(set(subRoute))
        #new_list.sort(key=subRoute.index)
        del_adjacent(subRoute)
        All_routes.append(subRoute)
    return All_routes
def GetAllLines(route_list:list):
    """
    通过每个轨迹点的归属路段找出完整轨迹，如果出现断路，先不处理
    :param route_list: 轨迹点的归属路段列表
    :return:
    """
    All_Lines = []
    del_adjacent(route_list)  #去重相邻重复元素
    for index in range(len(route_list)):
        if index == len(route_list) - 1:
            break
        else:
            temwaylist = MapNavigation.waytoway(route_list[index], route_list[index + 1])
            if temwaylist:  # and len(temwaylist)<5:  #加入相邻两个轨迹点不能够超过五个路段，但是对于相邻两个轨迹处于远距离可能会有问题
                All_Lines.extend(temwaylist)
            else:
                All_Lines.extend([route_list[index], route_list[index + 1]])
    del_adjacent(All_Lines)
    return All_Lines

def BatchProcessFinalLines(txtpath,kmlsavepath,savepath):
    """
    批量处理每辆车的完成路网匹配
    :param txtpath: txt文件路径，txt文件是最终确定的轨迹点所属路段的存储文件
    :param kmlsavepath: kml文件的保存路径
    :param savepath:路网匹配之后的完整路径
    :return:
    """
    savsfilename = "Complete_routes"
    if not os.path.isdir(kmlsavepath):
        os.mkdir(kmlsavepath)
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    count = 0
    temfilename = ""  #kml文件名
    with open(txtpath,'r') as file:
        lines = file.readlines()
        linesnum = len(lines)
        for i in range(linesnum):
            if lines[i].strip("\n"):
                count += 1
                if count%3 == 1:
                    temfilename = lines[i].strip("\n")
                elif count%3==0:
                    AllRoutes = Judge_Route_connectivity(GetAllLines(eval(lines[i].strip("\n"))))
                    AllNodeLists = []  # 路线中所有的坐标点
                    for subline in AllRoutes:
                        AllNodeLists.extend(Fill_coordinate_By_Routes(subline))
                    print(temfilename)
                    Road_matching.list2kml(AllNodeLists,temfilename,kmlsavepath)
                    temfilename = ""
#BatchProcessFinalLines("H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\\tsetfinallines.txt","H:\GPS_Data\Road_Network\BYQBridge\KML\PartTrunksAreaKml","H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes")
lis= [403874396, 47574526, 318323104, 47574526, 318323104, 466289456, 606768158, 466839079, 466839081]
print(GetAllLines(lis))
#nodes = Fill_coordinate_By_Routes(GetAllLines(lis))

#Road_matching.list2kml(nodes,"xtx","H:\GPS_Data\Road_Network\BYQBridge\KML\PartTrunksAreaKml\Batch\\334e")