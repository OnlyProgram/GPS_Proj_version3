# -*- coding: utf-8 -*-
# @Time    : 2019/6/4 19:24
# @Author  : WHS
# @File    : Common_Functions.py
# @Software: PyCharm
import pymysql
import math
from math import radians, cos, sin, asin, sqrt


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
def Get_way_Nodes(way_id):
    """
    根据way_id得出此路段node,及对应的sequenceid
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
def angle(v1, v2):
    """
    计算两个路段之间的夹角
    :param v1: 传入轨迹1的两个经纬度坐标
    :param v2: 传入轨迹2的两个经纬度坐标
    :return:  角度和余弦值
    """
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180/math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180/math.pi)
    # print(angle2)
    if angle1*angle2 >= 0:
        included_angle = abs(angle1-angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    # included_angle  角度
    #print(included_angle)
    return included_angle  #返回角度
    #return math.sin((included_angle/180)*math.pi)
def Point_Line_Distance(x,y,z):
    """
    点到线的距离
    :param x: 线的第一个坐标 如[x1,y1]
    :param y: 线的第二个坐标  如[x2,y2]
    :param z: 此点到线的距离
    :return: 距离
    b = (x1-x2)/y2-y1
    """
    if (y[0]-x[0])==0:  # 此线垂直x轴
        d = abs(z[0]-x[0])
    elif (y[1]-x[1]) == 0:#垂直y轴
        d = abs(z[1]-x[1])
    else:
        a = 1
        k = (y[1] - x[1]) / (y[0] - x[0])
        b = -1 / k
        c = x[1] / k - x[0]
        d = abs(a * z[0] + b * z[1] + c) / math.sqrt(a ** 2 + b ** 2)
    return d
def Get_Coordinate(node_id):
    """
    根据node_id查坐标
    :param node_id:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    sql = 'SELECT Lon,Lat FROM nodes WHERE nodes.Node_id={}'.format(node_id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)
        cursor.close()
        connection.close()
def Find_two_Point(Candidate_way_lis,lon,lat):
    """
    从候选路段中的点集中选出距轨迹点最近的两个
    :param Candidate_way_lis 某候选路段的坐标点集合 如：[[4611240391, 68], [4611240390, 69], [4611240389, 70]]
    :param lon 原始轨迹点经度
    :param lat 原始轨迹点维度
    :return:
    """
    tem_lis = []
    for i in range(len(Candidate_way_lis)):
        tem_coor = Get_Coordinate(Candidate_way_lis[i][0])  #坐标点
        tem_lis.append(haversine(lon,lat,tem_coor[0],tem_coor[1]))
    index_lis = sorted(range(len(tem_lis)), key=lambda k: tem_lis[k])
    return index_lis[0],index_lis[1]
def Find_next_Point(sequence_id,way_id):
    """
    根据路段和坐标点，找到该路段的下一个点
    :param sequence_id: 序列编号
    :param way_id:  路段编号
    :return: 返回下一个坐标点编号 及其序列号
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")
    sql = """SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE ways_nodes.way_id={} AND ways_nodes.sequence_id={}""".format(str(way_id),str(sequence_id+1))
    cursor.execute(sql)
    result = cursor.fetchone()
    if  result:
        pass
    else:
        sql = "SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE ways_nodes.way_id={} AND ways_nodes.sequence_id={}".format(
            str(way_id), str(sequence_id - 1))
        cursor.execute(sql)
        result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result
def Find_nearby_Point(x_grid,y_grid,difference = 3):
    """
    找出该坐标点相邻格子中的所有坐标点，一个格子为100米，
    :param x_greid:
    :param y_grid:
    :param difference 相邻格子数，默认为1，即以改坐标所在的格子为中心，向外扩展一圈
    :return:返回字典 键为way_id  值为node_id
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosm;")

    sql = """ SELECT a.way_id,b.Node_id,a.sequence_id FROM ways_nodes a,(
		SELECT nodes.Node_id FROM nodes WHERE nodes.X_Grid >= {}
		AND nodes.X_Grid <= {} AND nodes.Y_Grid >= {} AND nodes.Y_Grid <= {}) b
        WHERE a.node_id = b.Node_id""".format(x_grid-difference,x_grid+difference,y_grid-difference,y_grid+difference)
    node_id_dict = {}
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            #print(row)
            tem_lis = [row[1], row[2]]
            if row[0] in node_id_dict:
                node_id_dict[row[0]].append(tem_lis)
            else:
                node_id_dict[row[0]] = [tem_lis]
            #node_id_lists.append(row[0])
    except Exception as e:
        print(e)
        connection.rollback()
        cursor.close()
        connection.close()
    return  node_id_dict
def Find_Candiate_Point(dic,coordinate1,coordinate2,flag=1):
    """
    返回某个坐标该归属于哪条路段，可返回多条
    :param dic:
    :param coordinate1:
    :param coordinate2:
    :return:
    """
    Candidate_dic = {}  # 存储待选路段与轨迹的方余弦值和距离
    v1 = [coordinate1[0], coordinate1[1], coordinate2[0], coordinate2[1]]  # 轨迹向量
    #print("轨迹向量V1{}".format(v1))
    for key in dic.keys():
        if len(dic[key]) == 1:  #如果候选路段只有一个点
            tem_coor1 =  Get_Coordinate(dic[key][0][0])#临时坐标1
            tem_li = Find_next_Point(dic[key][0][1],key) #接受返回的查询结果 node_id  sequence_id (2207731639, 17)
            tem_coor2 = Get_Coordinate(tem_li[0])

            if dic[key][0][1]>tem_li[1]:
                #tem_coor1的sequence_id 大于tem_coor2的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]

            Cosine =  angle(v1,v2)  #接受角度
            #print("{}轨迹向量V2:{}".format(key,v2))
            if flag==1:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
            else:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
            Candidate_dic[key] = [distance,Cosine]
        elif len(dic[key])==2:

            tem_coor1 = Get_Coordinate(dic[key][0][0])  # 临时坐标1
            tem_coor2 = Get_Coordinate(dic[key][1][0])  # 临时坐标1
            if dic[key][0][1] > dic[key][1][1]:  # 第一个点的sequence_id 大于 第二点的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]
            #print("{}轨迹向量V2:{}".format(key, v2))
            Cosine = angle(v1, v2)
            if flag == 1:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
            else:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
            Candidate_dic[key] = [distance, Cosine]
        else:
            # 候选路段有三个点及以上
            if flag==1:
                num1, num2 = Find_two_Point(dic[key], coordinate1[0], coordinate1[1])  #在路段上选出距离轨迹点最近的两个node
            else:
                num1, num2 = Find_two_Point(dic[key], coordinate2[0], coordinate2[1])
            tem_coor1 = Get_Coordinate(dic[key][num1][0])  # 临时坐标1
            tem_coor2 = Get_Coordinate(dic[key][num2][0])  # 临时坐标1
            if dic[key][num1][1] > dic[key][num2][1]:  # 第一个点的sequence_id 大于 第二点的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]
            #print("{}轨迹向量V2:{}".format(key, v2))
            Cosine = angle(v1, v2)
            if flag == 1:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
            else:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
            Candidate_dic[key] = [distance, Cosine]
    return Candidate_dic
def Find_Candidate_Route(coordinate1,coordinate2,flag=1):
    """
    通过车辆轨迹的两个坐标选出匹配的候选路段
    :param coordinate1: 坐标1 及其编号   如[116.5256651,39.7467991，1526,747]
    :param coordinate2: 坐标2 及其编号   如[116.5256651,39.7467991，1526,747]
    :param flag 如果flag==1 计算coordinate1 ==2 计算coordinate2
    :return: 返回候选路段编号  way_id及其序列编号sequence
    """
    dic = {} #候选路段，没有距离，方向约束
    if flag == 1:  # 计算该路段的起点归属相近点
        dic = Find_nearby_Point(coordinate1[2], coordinate1[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2, flag=1)
    # print(dic)
    elif flag == 2:  # 计算该路段的终点相近点
        dic = Find_nearby_Point(coordinate2[2], coordinate2[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2, flag=2)
    else:
        return None
    point_Candidate = {}
    for key in Candidate_Route_dic.keys():
        # 两个原始轨迹点方向与道路轨迹方向夹角大于90 或者轨迹点到地图道路距离大于40米
        if Candidate_Route_dic[key][1] > 90 or Candidate_Route_dic[key][0] > 0.0004:
            pass
        else:
            point_Candidate[key] = Candidate_Route_dic[key]
    return point_Candidate
def Double_layer_list(doublelist:list):
    """
    双层列表去重
    :param doublelist:  双层列表
    :return:
    """
    new_list = [list(t) for t in set(tuple(_) for _ in doublelist)]  # 嵌套列表去重
    new_list.sort(key=doublelist.index)
    return new_list
def Is_List_Prefix(list1:list,list2:list):
    """
    判断两个是否为另一个前缀,
    :param list1:
    :param list2:
    :return:返回前缀
    """
    len1 = len(list1)
    len2 = len(list2)
    flag = 1
    if len1<=len2:
        for index in range(len1):
            if list1[index]==list2[index]:
                pass
            else:
                flag=0
        if flag==1:
            return list1
        else:return None
    elif len1>len2:
        for index in range(len2):
            if list1[index]==list2[index]:
                pass
            else:
                flag=0
        if flag==1:
            return list2
        else:return None
def Sequential_subset(slist):
    """
    #传入时不会有重复子列表
    如果一个列表是两个及以上的前缀，则会被删除，如果只是一个列表的前缀，则不会被删除（路口）

    去除子集  如[[1,2,3],[1,2]]
    :param slist: 为双层嵌套列表
    :return:
    """
    del_list = []  # 要删除的子列表
    index_list = [i for i in range(len(slist))]
    # print(index_list)
    compared = []  # 已经比较的
    for index in index_list:
        compared.append(index)
        for index2 in index_list:
            if index2 in compared:  # 不比较本身
                pass
            else:
                temdel = Is_List_Prefix(slist[index], slist[index2])
                if temdel:
                    del_list.append(temdel)
    # print(del_list)
    seta = Double_layer_list(del_list)   #去重
    n = [del_list.count(i) for i in seta]  # 统计频率
    z = zip(seta, n)
    z = sorted(z, key=lambda t: t[1], reverse=True)
    # 统计出每个前缀出现的次数
    del_list = [i[0] for i in z if i[1] > 1]
    #print(del_list)
    for subdellist in del_list:
        slist.remove(subdellist)
    # print(slist)
    return slist
def del_adjacent(alist):
    """
    删除相邻重复元素
    :param alist:
    :return:
    """
    for i in range(len(alist) - 1, 0, -1):
         if alist[i] == alist[i-1]:
             del alist[i]
    return alist
def DoubleDel(dlist:list):
    """
    对双层列表的每一个子列表进行相邻元素去重，然后去重
    :param dlist: 双层列表
    :return:
    """
    for sub in dlist:
        sub = del_adjacent(sub)
    dlist = Double_layer_list(dlist)
    return dlist
def Main_Auxiliary_road(slist:list):
    """
    传入双层列表 ，去除类似[47574526, 318323104, 47574526], [47574526, 210697572, 318323104, 47574526]种的路段，即通过某个路段之后又回到此路段
    先只考虑头尾
    :param slist:双层列表
    :return:
    """
    startenddel_waylist = []  #路段头尾路段编号相同 待删除路段
    for sub in slist:
        if sub[0]==sub[-1]:
            startenddel_waylist.append(sub)
    for subdel in startenddel_waylist:
        slist.remove(subdel)
    # 以上的去除同一条候选路线头尾路段编号相同的路线

    return  slist
def Start_End(slist:list):
    # 以下为去除 ：对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
    del_list = []  # 要删除的子列表
    index_list = [i for i in range(len(slist))]
    # print(index_list)
    compared = []  # 已经比较的
    for index in index_list:
        compared.append(index)
        for index2 in index_list:
            if index2 in compared:  # 不比较本身
                pass
            else:
                # 候选路线slist[index] slist[index2] 的头尾路段编号是一样的
                if slist[index][0] == slist[index2][0] and slist[index][-1] == slist[index2][-1]:
                    if len(slist[index]) > len(slist[index2]):
                        del_list.append(slist[index])
                    elif len(slist[index]) < len(slist[index2]):
                        del_list.append(slist[index2])
                    else:
                        pass
                else:
                    pass
    del_list = Double_layer_list(del_list)
    for delsub in del_list:
        slist.remove(delsub)
    return slist
di = {42500477: [[727309730, 7], [727309731, 8], [727309734, 9], [727309736, 10], [2207731541, 11], [727309621, 12]],
      47574526: [[727309576, 2], [2207731519, 3], [727309578, 4], [727309579, 5], [727309582, 6]],
      47574777: [[605279076, 1], [605279309, 2]],
      242945794: [[2503838158, 1]],
      242945798: [[2207731537, 5], [2207731536, 6], [605279377, 7]],
      318323143: [[3247242212, 1], [2503838158, 2]],
      403874394: [[2207731533, 1], [605279377, 2], [320534688, 3]],
      403874395: [[320535158, 13], [605279076, 14], [4061751582, 15]],
      403874396: [[4061751582, 1]],
      403874397: [[2207731533, 7]],
      461830999: [[3247242212, 1]]}
#print(Find_Candidate_Route([116.395731,39.719466,1396,720],[116.40172,39.719368,1402,720],flag=2))
#print(haversine(116.438871,39.720601,116.440767,39.721627))
#{47574526: [0.00011744496663786911, 2], 47574777: [3.804790392400445e-05, 4], 242945794: [0.00033793311935096965, 76], 403874395: [2.6417826493659107e-05, 1], 403874396: [2.2342567885180277e-05, 1]}
testlist = [[47574526, 47574526, 47574526, 47574526], [47574526, 47574526, 47574526, 210697572],
            [47574526, 47574526, 47574526, 318323104], [47574526, 47574526, 210697572, 210697572],
            [47574526, 47574526, 210697572, 318323104], [47574526, 47574526, 318323104, 47574526],
            [47574526, 47574526, 318323104, 318323104]]
startendtest = [[47574526, 210697572, 210697572], [47574526, 210697572, 318323104],
                [47574526, 210697572, 318323104, 47574526], [47574526, 210697572, 318323104, 318323104],
                [47574777, 47574526, 47574526], [47574777, 47574526, 210697572], [47574777, 47574526, 318323104],
                [47574777, 47574526, 318323104, 47574526], [47574777, 47574526, 318323104, 318323104], [47574777, 210697572, 210697572],
                [47574777, 210697572, 318323104], [47574777, 210697572, 318323104, 47574526], [47574777, 210697572, 318323104, 318323104],
                [403874395, 47574526, 47574526], [403874395, 47574526, 210697572], [403874395, 47574526, 318323104],
                [403874395, 47574526, 318323104, 47574526], [403874395, 47574526, 318323104, 318323104], [403874395, 210697572, 210697572],
                [403874395, 210697572, 318323104], [403874395, 210697572, 318323104, 47574526], [403874395, 210697572, 318323104, 318323104],
                [403874395, 403874396, 318323104, 47574526], [403874395, 403874396, 318323104, 318323104], [403874395, 403874396, 47574526],
                [403874395, 403874396, 318323104], [403874396, 47574526, 210697572, 210697572], [403874396, 47574526, 210697572, 318323104],
                [403874396, 47574526, 318323104, 47574526], [403874396, 47574526, 318323104, 318323104]]

#print(Start_End(startendtest))
#print(DoubleDel(testlist))