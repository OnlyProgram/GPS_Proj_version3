# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 22:08
# @Author  : WHS
# @File    : way2way.py
# @Software: PyCharm
"""
实现导航功能（考虑了方向），从一路段到另一路段是否互通，注意方向，示例：210697572,403874396，
虽然这两个路段能通过318323104连接，但是通过方向所以路段210697572不能到达403874396

******需要多个路口检验**********
"""
import pymysql
from RoadNetwork import Common_Functions
def Get_key_by_value(dic, value):
    for key in dic.keys():
        if value in dic[key]:
            return key
    return None
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
def waytoway(way_id1, way_id2):
    """
    实现从way_id1到way_id2的路线规划,
    :param way_id1:
    :param way_id2:
    :return:
    首先判断两个路段是否有交集，有交集则这两条路不需要经过其他路线的连接
    """
    route = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        wayslist2 = Common_Functions.Get_way_Nodes(way_id2)  #示例：[320524866, 2207731964, 320524867]
        index = wayslist2.index(node_id[0][0])
        if index==len(wayslist2)-1:  #交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
            return None

        else:
            route.extend([way_id1, way_id2])
            return route
    else:
        # print("没有直接交集")
        tem_way = way_id1  # 代表被查询的路段
        index = 0
        node_dic = {}  # 拐点对应的way,键为拐点，值为way
        way_list = [way_id1]  #存储处理过的way
        way_dic = {}  # 路段对应的拐点，键为way 值为拐点（可能为列表，因为一条路段可能有多个拐点）
        #print("开始路段:{},结束路段：{}".format(tem_way, way_id2))
        while True:
            # print("拐点：{}".format(Find_inflectionpoint(tem_way)))
            tem_list = []  #临时存储一个路段的所有拐点
            for i in Find_inflectionpoint(tem_way):  # 找出路段1的所有拐点
                if i in node_dic:
                    pass
                else:
                    tem_list.append(i)
                    node_dic[i] = None
            way_dic[tem_way] = tem_list
            # print(node_dic)
            if index < len(node_dic):  #查看是否所有的拐点已经处理完毕
                tem_lis = []  #临时存储这个拐点对应的所有way，去除上一步找出此拐点的基准way
                # print("拐点:{}对应的way:{}".format((list(node_dic.keys())[index]),Find_way_By_inflectionpoint(list(node_dic.keys())[index])))
                for j in Find_way_By_inflectionpoint(list(node_dic.keys())[index]):  # 找出拐点对应的way
                    if j in way_list:  #表示此路段已处理
                        pass
                    else:
                        way_list.append(j)
                        tem_lis.append(j)
                node_dic[list(node_dic.keys())[index]] = tem_lis   #键为拐点  值为way
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
            #以下for循环检查此路径的方向是否正确，因为有交点不一定能通过
            for wayid in range(len(new_route)):
                if wayid==len(new_route)-1:
                    return new_route
                Intersection = TwoWay_intersection(new_route[wayid], new_route[wayid + 1])  # 两条路段交点
                wayslist2 = Common_Functions.Get_way_Nodes(new_route[wayid + 1])  # 示例：[320524866, 2207731964, 320524867]
                index = wayslist2.index(Intersection[0][0])
                if index == len(wayslist2) - 1:  # 交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
                    return None
        else:
            #print("无法从路段:{}行驶到路段:{}".format(way_id1,way_id2))
            return None
