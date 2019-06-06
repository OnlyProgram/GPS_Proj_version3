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
import os
import sys
import copy
from RoadNetwork import Common_Functions
def Get_key_by_value(dic, value):
    for key in dic.keys():
        if value in dic[key]:
            return key
    return None
def Get_way_NodeID(way_id):
    """
    根据way_id得出此路段node
    :param way_id:
    :return: 饭后node列表
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    sql = 'SELECT ways_nodes.node_id FROM ways_nodes WHERE way_id = {}'.format(way_id)
    way_nodes_list = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()   #元组
        for row in result:
            way_nodes_list.append(row[0])
        return way_nodes_list
    except Exception as e:
        print(e)
        cursor.close()
        connection.close()
def TwoWay_intersection(wayid1, wayid2):
    """
    判断两个way是否有交集
    :param wayid1:
    :param wayid2:
    :return: 返回交叉点

    """
    if wayid1==wayid2:
        print("两条路段相同，如果想判断两个路段是否有交点，请输入两个不同的wayid")
        return None
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
def Get_way_NodesSequenceId(way_id):
    """
    根据way_id得出此路段node sequenceid
    :param way_id:
    :return: 饭后node列表
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    sql = 'SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE way_id = {}'.format(way_id)
    way_nodes_list = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()   #元组
        for row in result:
            way_nodes_list.append([row[0],row[1]])
        return way_nodes_list
    except Exception as e:
        print(e)
        cursor.close()
        connection.close()
class myException(Exception):
    def __init__(self,error):
        self.error = error
    def __str__(self,*args,**kwargs):
        return self.error
def JudgeLines(slist:list):
    """
    判断连通性，传入的路段都有交点 这部分主要判断方向,至少传入三个路段
    注意  如果只传入两个路段，默认判别为不能通行
    :param slist: 路段列表
    :return:
    """

    try:
        listlen = len(slist)
        if listlen <= 2:
            raise myException("自定义异常>>>{}函数连通性判断，传入的路线列表中要至少含有三个路段！！".format(sys._getframe().f_code.co_name))
        First_intersection_sequenceId = None
        Second_intersection_sequenceId = None
        for index in range(listlen):
            if index == listlen - 2:
                break
            if slist[index]!=slist[index + 1] and slist[index + 1]!=slist[index + 2]:
                if JudgeTwoWay(slist[index], slist[index + 1]):
                    pass
                else:
                    return False
                if JudgeTwoWay(slist[index+1], slist[index + 2]):
                    pass
                else:
                    return False
                First_intersection = TwoWay_intersection(slist[index],slist[index + 1])  # 注意First_intersection 为嵌套元组 ，如((320533913,),)
                Second_intersection = TwoWay_intersection(slist[index + 1], slist[index + 2])
                # print("{}与{}交点为{} {}与{}交点为{}".format(slist[index],slist[index+1],First_intersection,slist[index+1],slist[index+2],Second_intersection))
                Midwaylist = Get_way_NodesSequenceId(slist[index + 1])
                for sub in Midwaylist:
                    if First_intersection[0][0] == sub[0]:
                        First_intersection_sequenceId = sub[1]  # 第一个交点的sequenceId
                for sub in Midwaylist:
                    if Second_intersection[0][0] == sub[0]:
                        Second_intersection_sequenceId = sub[1]  # 第二个交点的sequenceId
                if Second_intersection_sequenceId >= First_intersection_sequenceId:
                    pass
                else:
                    return False
            elif slist[index]!=slist[index + 1]  and slist[index + 1]==slist[index + 2]:
                if JudgeTwoWay(slist[index],slist[index + 1]):
                    return True
                else:
                    return False
            elif slist[index]==slist[index + 1]  and slist[index + 1]!=slist[index + 2]:
                if JudgeTwoWay(slist[index + 1],slist[index + 2]):
                    return True
                else:
                    return False
            else:
                return True
        return True
    except myException as e:
        print(e)
        return False
def FindNextWay(curway):
    """
    返回curway下一步能走的路段列表
    :param curway:
    :return:
    """
    nextwaylists = []
    InflectionpointLists = Find_inflectionpoint(curway)  # 路段的所有拐点
    for subnode in InflectionpointLists:  # 遍历处理路段对应的拐点
        temways = Find_way_By_inflectionpoint(subnode)  # 通过节点找出下一步的路段
        #print(temways)
        temways.remove(curway)

        delsub = []
        for temsubway in temways:
            if not JudgeTwoWay(curway, temsubway):  # 路段key到temsubway不能通过
                delsub.append(temsubway)
        for sub in delsub:
            temways.remove(sub)  #
        if len(temways) != 0:  # 拐点subnode下一步有可走的路
            nextwaylists.extend(temways)
    return set(nextwaylists)
def JudgeTwoWay(wayid1,wayid2):
    """
    判断两个相邻有交点路段是否能够互通，即从way1 是否能到达way2
    注意：此部分只判断有交点的两个路段  没有交点的两个路段会直接判断为不能互通
    :param wayid1:
    :param wayid2:
    :return:
    """
    if wayid1==wayid2:
        return True
    node_id = TwoWay_intersection(wayid1, wayid2)  # 两条路段交点
    #print(node_id)
    if not node_id:     #两个路段没有交点
        return False
    wayslist1 = Get_way_NodeID(wayid1)
    wayslist2 = Get_way_NodeID(wayid2)  # 示例：[320524866, 2207731964, 320524867]
    index = wayslist2.index(node_id[0][0])    # node_id[0][0]为取出交点 node_id为嵌套元组
    if index == len(wayslist2) - 1:  # 交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
        return False
    elif wayslist1.index(node_id[0][0]) == 0:  # 交点是way1的第一个点
        return False
    else:
        return True
def waytoway(way_id1,way_id2,max_num=8):
    """
    实现从way_id1到way_id2的路线规划,当此函数完全用作简易导航，可设置max_num为无穷
    设置 max_num 与Count 的原因为防止查找完全不通的两个路段而耗费过长的时间
    有方向通行
    问题：即使很近的两个路段（实际短距离不能通行），但是会花费较多的时间去判断是否能通行
    47574526,403874395两个路段不能互通 但是只在北野场桥一部分就花费了5分钟去判断可行性
    :param way_id1:
    :param way_id2:
    :return:
    首先判断两个路段是否有交集，有交集则这两条路不需要经过其他路线的连接
    """
    if way_id1 == way_id2:
        return [way_id1,way_id2]
    finalroute = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        if JudgeTwoWay(way_id1,way_id2):
            finalroute.extend([way_id1, way_id2])
            return finalroute
        else:
            return False
    else:
        #两条路段没有直接交点
        Candidate_Routes = [[way_id1]]  # 候选路线
        flag = 0
        count = 0  # 迭代多少次之后仍然没有找到可行路线，则认为不可走
        exitflag = 0  #标记是否是通过找到满足条件的路线而退出的
        while True:
            #print(Candidate_Routes)
            temCandidate_Routes = []  # 存储当前这一轮新的候选路线
            AllNextways = []
            MaxDel = []  # 存因路段数目大于阈值，而筛除的路线
            for sub in Candidate_Routes:
                if way_id2 in sub:
                    flag = 1
                    break
                if len(sub) > max_num:  # 防止寻找时间过长，如果目的是为了查找路线，可将此条件删除
                    MaxDel.append(sub)
            for sub in MaxDel:
                Candidate_Routes.remove(sub)
            if len(Candidate_Routes) == 0:
                flag = 1
                exitflag = 1
            if count == 5:    #此条件防止查找时间过长
                flag = 1
                exitflag = 1
            if flag == 1:
                break
            for subroute in Candidate_Routes:
                # subroute 表示正在处理的路线
                processingway = subroute[-1]  # 表示要处理的路段
                nextway = FindNextWay(processingway)  # 下一步的可选路段
                AllNextways.extend(nextway)
                for next in nextway:
                    temroute = copy.deepcopy(subroute)
                    temroute.append(next)
                    temCandidate_Routes.append(temroute)
            count += 1
            Candidate_Routes.clear()
            Candidate_Routes = temCandidate_Routes
            Candidate_Routes = Common_Functions.Double_layer_list(Candidate_Routes)
            Candidate_Routes = Common_Functions.Main_Auxiliary_road(Candidate_Routes)  # 去除头尾路段一样的候选路线
            Candidate_Routes = Common_Functions.Start_End(Candidate_Routes)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            Candidate_Routes = Common_Functions.Sequential_subset(Candidate_Routes)  # 最后去前缀
            delsub = []
            for sub in Candidate_Routes:
                if len(sub) >= 3:
                    if JudgeLines(sub):  # 判断当前路线是否能通
                        pass
                    else:
                        delsub.append(sub)
                        continue
            for sub in delsub:
                Candidate_Routes.remove(sub)
            if len(AllNextways)==0:
                #所有的候选路线都没有下一步路可走
                flag=1
                exitflag = 1
        if exitflag==1:
            #证明是循环跳出不是因为找到路径跳出的
            return False
        minnum = float("inf")
        for sub in Candidate_Routes:
            if way_id2 in sub:
                if len(sub) < minnum:
                    finalroute = sub
                    minnum = len(sub)
            else:
                pass
        if len(finalroute)==0:
            return False
        else:
            return finalroute
def NodirectionFindNextWay(curway):
    """
    返回curway下一步能走的路段列表,只要有交点则符合，不考虑方向
    :param curway:
    :return:
    """
    nextwaylists = []
    InflectionpointLists = Find_inflectionpoint(curway)  # 路段的所有拐点
    for subnode in InflectionpointLists:  # 遍历处理路段对应的拐点
        temways = Find_way_By_inflectionpoint(subnode)  # 通过节点找出下一步的路段
        #print(temways)
        temways.remove(curway)
        if len(temways) != 0:  # 拐点subnode下一步有可走的路
            nextwaylists.extend(temways)
    return set(nextwaylists)
def Nodirectionwaytoway(way_id1,way_id2,max_sum=8):
    """
    无方向  有交点就会认为通行
    :param way_id1:
    :param way_id2:
    :param max_sum:
    :return:
    """
    if way_id1 == way_id2:
        return [way_id1,way_id2]
    finalroute = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        if JudgeTwoWay(way_id1,way_id2):
            finalroute.extend([way_id1, way_id2])
            return finalroute
        else:
            return False
    else:
        #两条路段没有直接交点
        Candidate_Routes = [[way_id1]]  # 候选路线
        flag = 0
        count = 0   #迭代多少次之后仍然没有找到可行路线，则认为不可走
        exitflag = 0   #标记是否是通过找到满足条件的路线而退出的
        while True:
            temCandidate_Routes = []  # 存储当前这一轮新的候选路线
            AllNextways = []
            MaxDel = []   #存因路段数目大于阈值，而筛除的路线
            for sub in Candidate_Routes:
                if way_id2 in sub:
                    flag = 1
                    break
                if len(sub) > max_sum:   #防止寻找时间过长，如果目的是为了查找路线，可将此条件删除
                    MaxDel.append(sub)
            for sub in MaxDel:
                Candidate_Routes.remove(sub)
            if len(Candidate_Routes)==0:
                flag = 1
                exitflag = 1
            if count==10:
                flag=1
                exitflag = 1
            if flag == 1:
                break
            for subroute in Candidate_Routes:
                # subroute 表示正在处理的路线
                processingway = subroute[-1]  # 表示要处理的路段
                nextway = NodirectionFindNextWay(processingway)  # 下一步的可选路段
                AllNextways.extend(nextway)
                for next in nextway:
                    temroute = copy.deepcopy(subroute)
                    temroute.append(next)
                    temCandidate_Routes.append(temroute)
            count += 1
            Candidate_Routes.clear()
            Candidate_Routes = temCandidate_Routes
            Candidate_Routes = Common_Functions.Double_layer_list(Candidate_Routes)
            Candidate_Routes = Common_Functions.Main_Auxiliary_road(Candidate_Routes)  # 去除头尾路段一样的候选路线
            Candidate_Routes = Common_Functions.Start_End(Candidate_Routes)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            Candidate_Routes = Common_Functions.Sequential_subset(Candidate_Routes)  # 最后去前缀
            if len(AllNextways)==0:
                #所有的候选路线都没有下一步路可走
                flag=1
                exitflag = 1
        minnum = float("inf")
        if exitflag==1:
            #证明是循环跳出不是因为找到路径跳出的
            return False
        for sub in Candidate_Routes:
            #由于以上为没有方向的判断，所以在此循环中要加入方向的判断
            if way_id2 in sub:
                if len(sub)==1:
                    return sub
                elif len(sub)==2 and JudgeTwoWay(sub[0],sub[1]):
                    finalroute = sub
                    minnum = 2
                elif len(sub) >= 3 and JudgeLines(sub):
                    if len(sub) < minnum:
                        finalroute = sub
                        minnum = len(sub)
            else:
                pass
        if len(finalroute)==0:
            return False
        else:
            return finalroute
"""
#旧简易导航 问题多 无方向
def waytoway(way_id1, way_id2):
    if way_id1 == way_id2:
        return [way_id1,way_id2]
    route = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        wayslist1 = Common_Functions.Get_way_Nodes(way_id1)
        wayslist2 = Common_Functions.Get_way_Nodes(way_id2)  #示例：[320524866, 2207731964, 320524867]
        index = wayslist2.index(node_id[0][0])
        if index==len(wayslist2)-1:  #交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
            return None
        elif wayslist1.index(node_id[0][0]) ==0:    #交点是way1的第一个点
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
                wayslist1 = Common_Functions.Get_way_Nodes(new_route[wayid])
                wayslist2 = Common_Functions.Get_way_Nodes(new_route[wayid + 1])  # 示例：[320524866, 2207731964, 320524867]
                index = wayslist2.index(Intersection[0][0])
                # 交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的,或者交点是way1的起点，也无法通过
                if index == len(wayslist2) - 1 or wayslist1.index(Intersection[0][0]) ==0:
                    return None
        else:
            #print("无法从路段:{}行驶到路段:{}".format(way_id1,way_id2))
            return None
"""

