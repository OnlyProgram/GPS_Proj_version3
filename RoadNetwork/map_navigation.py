# -*- coding: utf-8 -*-
# @Time    : 2019/5/21 12:15
# @Author  : WHS
# @File    : map_navigation.py
# @Software: PyCharm
"""
实现openstreetmap简单的路径导航
"""
import pymysql
import time

def TwoWay_intersection(wayid1, wayid2):
    """
    判断两个way是否有交集
    :param wayid1:
    :param wayid2:
    :return: 返回交叉点

    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    SQL = """(SELECT a.NodeID FROM
            (SELECT * FROM inflectionpoint WHERE inflectionpoint.WayID={}) as a,
            (SELECT * FROM inflectionpoint WHERE inflectionpoint.WayID={}) as b
            WHERE a.NodeID = b.NodeID)""".format(wayid1, wayid2)
    cursor.execute(SQL)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if result:
        # 有交集
        return result
    else:
        return None


def FindWayStartEnd(way):
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    SQL = """(SELECT a.node_id,b.node_id FROM
             (SELECT * FROM ways_nodes WHERE way_id = {}  ORDER BY ways_nodes.sequence_id LIMIT 1) as a,
            (SELECT * FROM ways_nodes WHERE way_id = {}  ORDER BY ways_nodes.sequence_id DESC LIMIT 1) as b
            WHERE a.way_id = b.way_id)""".format(way, way)
    cursor.execute(SQL)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def Find_inflectionpoint(way):
    """
    找路段way的所有拐点
    :param way: 路段的编号
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    SQL = """(SELECT inflectionpoint.NodeID FROM
            inflectionpoint
            WHERE inflectionpoint.WayID = {})""".format(way)
    cursor.execute(SQL)
    point_list = []
    result = cursor.fetchall()
    for row in result:
        point_list.append(row[0])
    cursor.close()
    connection.close()
    return point_list


def Find_way_By_inflectionpoint(node):
    """
    根据拐点找出其所在的way
    :param node:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    SQL = """(SELECT inflectionpoint.WayID FROM
                inflectionpoint
                WHERE inflectionpoint.NodeID = {})""".format(node)
    cursor.execute(SQL)
    way_list = []
    result = cursor.fetchall()
    for row in result:
        way_list.append(row[0])
    cursor.close()
    connection.close()
    return way_list


def Get_key_by_value(dic, value):
    for key in dic.keys():
        if value in dic[key]:
            return key
    return None


def waytoway(way_id1, way_id2):
    """
    实现从way_id1到way_id2的路线规划,
    :param way_id1:
    :param way_id2:
    :return:
    首先判断两个路段是否有交集，有交集则这两条路不需要经过其他路线的连接
    """
    route = []
    node_id = TwoWay_intersection(way_id1, way_id2)
    if node_id:
        route.extend([way_id1, way_id2])
        return route
    else:
        # 无交集
        # print("没有直接交集")
        tem_way = way_id1  # 代表被查询的路段
        index = 0
        node_dic = {}  # 拐点对应的way
        way_list = [way_id1]
        way_dic = {}  # 路段对应的拐点
        #print("开始路段:{},结束路段：{}".format(tem_way, way_id2))
        while True:
            # print("拐点：{}".format(Find_inflectionpoint(tem_way)))
            tem_list = []
            for i in Find_inflectionpoint(tem_way):  # 找出路段1的所有拐点
                if i in node_dic:
                    pass
                else:
                    tem_list.append(i)
                    node_dic[i] = None
            way_dic[tem_way] = tem_list
            # print(node_dic)
            if index < len(node_dic):
                tem_lis = []
                # print("拐点:{}对应的way:{}".format((list(node_dic.keys())[index]),Find_way_By_inflectionpoint(list(node_dic.keys())[index])))
                for j in Find_way_By_inflectionpoint(list(node_dic.keys())[index]):  # 找出新的way
                    if j in way_list:
                        pass
                    else:
                        way_list.append(j)
                        tem_lis.append(j)
                node_dic[list(node_dic.keys())[index]] = tem_lis
            else:
                break
            if way_id2 in way_list:  # 目的道路在way_list中
                break
            if index == len(way_list) - 1:
                break
            else:
                tem_way = way_list[index + 1]
            index += 1
        #print("道路列表：{}".format(way_list))
        #print("way与与拐点对应表为：{}".format(way_dic))  # {"way_id":[node_id]}
        #print("拐点与way对应表为：{}".format(node_dic))  # {"node_id":[way_id]}
        if way_id2 in way_list:
            temway = way_id2
            route.append(temway)
            while True:
                temNode = Get_key_by_value(node_dic, temway)
                temway = Get_key_by_value(way_dic, temNode)
                route.append(temway)
                if way_id1 in route:
                    break
            new_route = route[::-1]
            #print("路段:{}行驶到路段:{}的路线为：{}".format(way_id1, way_id2,new_route))
            return new_route
        else:
            #print("无法从路段:{}行驶到路段:{}".format(way_id1,way_id2))
            return None


def Dic_Intersection(start_point_Candidate,end_point_Candidate):
    """
    求两个集合的交集
    :param start_point_Candidate:
    :param end_point_Candidate:
    :return:
    """
    # 求交集
    Intersection_dic = {}  # 交集字典
    for key in start_point_Candidate.keys():
        if key in end_point_Candidate:
            Intersection_dic[key] = [start_point_Candidate[key], end_point_Candidate[key]]
        else:
            pass
    print("交集为{}".format(Intersection_dic))

    if len(Intersection_dic) > 0:  # 交集之后候选路段大于1
        return Intersection_dic
      #elif len(Intersection_dic) == 1:
        #way_id = list(Intersection_dic.keys())[0]
    else:
        return None
#print(waytoway(437527025,318323104))
# print(Find_inflectionpoint(117082582))
# print(Find_way_By_inflectionpoint(1318916989))
#003b5b7e-e72c-4fc5-ac6d-bcc248ac7a16
dic1 = {152616724: [0.0003128038715210686, 8], 242945771: [0.00010030804556522377, 13], 437527024: [0.0001363336516206252, 10],
        466289457: [0.0001363336516206252, 12],
        466289461: [0.0003281441853758246, 79]}
dic2 = {47574526: [0.0012152176086689948, 26], 117082574: [0.0019419407249213682, 53], 117082584: [0.0019377766987287812, 56],
        318323104: [7.210338761900192e-05, 66], 466289455: [0.0006261494178913167, 42], 466289456: [0.0002294308136742203, 35],
        466289458: [0.0010035872522401056, 80], 606768161: [0.0021848974637776026, 11], 606768167: [0.0001863419845841099, 52]}
dic3 = {47574526: [0.0004943055391784846, 5], 117082588: [0.0003213427234098102, 85], 238769500: [0.0016513789668739316, 32],
        318323104: [0.0008263644406345266, 42], 318323155: [0.0005447798849191811, 52], 466289455: [0.00037697093483638757, 5],
        466289456: [0.0004285400665829553, 18], 606768161: [0.0024345392759626268, 35], 606768163: [0.00021793968028688493, 16],
        606768167: [7.330786218643421e-05, 3]}
dic4 = {47574526: [0.0001799749119644113, 50], 238769500: [0.0017224723539692813, 53], 318323155: [0.0012877193866950235, 31],
        466289455: [5.950295839452718e-05, 14], 466289456: [0.0008110609408500418, 55], 606768163: [0.00013476959103946726, 5],
        606768167: [0.0001877333198786578, 11]}
dic5 = {47574526: [0.00041892782540478606, 85], 238769500: [0.0022768842324561076, 68], 318323155: [0.0022768842324561076, 12],
        466289455: [0.0007194844748003498, 29], 606768161: [0.0002911250176899518, 1], 606768163: [0.00025703758625134906, 14],
        606768167: [2.8412980612075053e-05, 9]}
# 437527024 606768167
def Select_By_TwoDic(Intersection,dic,flag=0):
    """
    从交集和node候选字典中选归属路段
    :param Intersection:  路段交集
    :param dic: node候选路段字典
    :param flag 1表示从方向为交集——>node  0表示 node ——>交集
    :return:
    """
    resulr_lis = []  #存储可走通路段和其距离
    for key in Intersection:   #遍历交集，交集中可能存在多个路段
        for key2 in dic:
            if flag == 0:
                route = waytoway(key2,key)
                if route:# 路段key2能到到key
                    tem_lis = [key2,key,len(route),dic[key2][0]]  #第三个参数是key2到key所需经过的way数量
                    resulr_lis.append(tem_lis)
                else:
                    pass
            else:
                route = waytoway(key, key2)
                if route:  # 路段key2能到到key
                    tem_lis = [key, key2, len(route), dic[key2][0]]  # 第三个参数是key2到key所需经过的way数量
                    resulr_lis.append(tem_lis)
                else:
                    pass
    maxRouteNum = float('inf')
    result = None
    for m in resulr_lis:  #筛选出最终的路段
        if m[2] < maxRouteNum:
            result = m[0:2]
    print(result)
    return  result






def Select_Route(dic1,dic2,dic3,dic4,dic5):
    """
    根据候选点选出最终的路径
    :param dic1: ndoe1的候选路段字典
    :param dic2: ndoe2的候选路段字典
    :param dic3: ndoe3的候选路段字典
    :param dic4: ndoe4的候选路段字典
    :return: 返回选定的way  ID
    """
    routes = []  # 如果key1,key2,key3,key4,key5 能通过，则记录
    Absolute_routes = []
    ways = [] #记录路段 避免重复计算
    Flags = []  #记录路段是否能通行，对应位置记录该两个路段是够互通
    Absolute_path = []  #记录way2way的具体路线，记录ways的对应位置的两条路段互通的具体路线，如果不通，放入空列表
    route_distance = []  #路线key1,key2,key3,key4,key5 的总距离
    count = 1
    for key1 in dic1:
        for key2 in dic2:
            for key3 in dic3:
                for key4 in dic4:
                    for key5 in dic5:
                        flag = 1  #标记是否能走通
                        total_route = []  #记录key1,key2,key3,key4,key5 的完整路线
                        # 此路线是否能走通，如果不能直接舍弃，如果能：优先选way数目最少的
                        temlist = [key1,key2,key3,key4,key5]
                        if len(set(temlist))==1:  #key1,key2,key3,key4,key5  五个值相同
                            Absolute_routes.append([key1])
                            route_distance.append(dic1[key1][0]+dic2[key2][0]+dic3[key3][0]+dic4[key4][0]+dic5[key5][0])
                            break
                        #print("正在测试第{}条路线:{}".format(count,temlist))
                        for i in range(len(temlist)):
                            if i == len(temlist)-1:
                                break
                            else:
                                if [temlist[i],temlist[i+1]] in ways:  #减少计算
                                    if Flags[ways.index([temlist[i],temlist[i+1]])] == 1:
                                        total_route.extend(Absolute_path[ways.index([temlist[i],temlist[i+1]])])
                                    else:
                                        flag = 0
                                        break
                                else:
                                    if temlist[i] == temlist[i + 1]:
                                        pass
                                    else:
                                        tem_line = waytoway(temlist[i], temlist[i + 1])
                                        if tem_line:  # 两个路段能互通
                                            total_route.extend(tem_line)

                                            ways.append([temlist[i], temlist[i + 1]])
                                            Flags.append(1)
                                            Absolute_path.append(tem_line)
                                            pass
                                        else:
                                            ways.append([temlist[i], temlist[i + 1]])
                                            Flags.append(0)
                                            Absolute_path.append([])
                                            flag = 0
                                            break
                        #print(ways)
                        #print(Flags)
                        if flag == 1:
                            #print("可以通行路线{}".format(temlist))
                            #tem2 = list(set(temlist)).append(len(set(temlist)))
                            routes.append(temlist)
                            Absolute_routes.append(total_route)
                            route_distance.append(dic1[key1][0] + dic2[key2][0] + dic3[key3][0] + dic4[key4][0] + dic5[key5][0])
                        else:
                            pass
                        count += 1
    # print("选出的路线如下：")
    # print(len(routes))
    # print(len(Absolute_routes))
    # print(len(route_distance))
    for i in range(len(routes)):
         #print("可走通的路线:{}".format(routes[i]))
         print("此路线的完整（具体）路线：{}".format(Absolute_routes[i]))
         #print("候选点距此路线总距离为：{}".format(route_distance[i]))
    minwaynum = float('inf')#单条路线中路段的数量
    return_route = []
    Absolute_routes_set = []
    for line in Absolute_routes:
        newline =  sorted(set(line), key=line.index)
        Absolute_routes_set.append(newline)
        if len(newline) < minwaynum:
            minwaynum = len(newline)
    for lineset in Absolute_routes_set:
        if len(lineset) == minwaynum:
            return_route.append(lineset)


    print("选出的路线为：{}".format(return_route))
    return return_route
#res = FindWayStartEnd(318323170)
#print(res[0][0],res[0][1])
#print(waytoway(466289461,606768167))
#print(Find_inflectionpoint(117082582))
#print(Find_way_By_inflectionpoint(1318916989))