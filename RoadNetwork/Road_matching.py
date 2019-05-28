# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 9:01
# @Author  : WHS
# @File    : Road_matching.py
# @Software: PyCharm
"""
道路匹配
"""
import pymysql
import math
import os
from math import radians, cos, sin, asin, sqrt
import time
import RoadNetwork.FilesFunctions as RoadFile
import pandas as pd

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
    if (y[0] - x[0]) == 0:  # 此线垂直x轴
        d = abs(z[0] - x[0])
    elif (y[1] - x[1]) == 0:  # 垂直y轴
        d = abs(z[1] - x[1])
    else:
        a = 1
        k = (y[1] - x[1]) / (y[0] - x[0])
        b = -1 / k
        c = x[1] / k - x[0]
        d = abs(a * z[0] + b * z[1] + c) / math.sqrt(a ** 2 + b ** 2)
    return d
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
    #sql = 'SELECT nodes.Node_id FROM nodes WHERE nodes.X_Grid>={}  AND nodes.X_Grid<={} AND  nodes.Y_Grid>={} AND nodes.Y_Grid <= {}'.format\
      #  (x_grid-difference,x_grid+difference,y_grid-difference,y_grid+difference)

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
def Get_way_nodes(way_id):
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
    sql = "SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE ways_nodes.way_id={} AND ways_nodes.sequence_id={}".format(str(way_id),str(sequence_id+1))
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
    num1 = tem_lis.index(min(tem_lis))
    index_lis = sorted(range(len(tem_lis)), key=lambda k: tem_lis[k])
    return index_lis[0],index_lis[1]


def Find_Candiate_Point(dic,coordinate1,coordinate2):
    """
    返回某个坐标该归属于哪条路段，可返回多条
    :param dic:
    :param coordinate1:
    :param coordinate2:
    :return:
    """
    Candidate_dic = {}  # 存储待选路段与轨迹的方余弦值和距离
    v1 = [coordinate1[0], coordinate1[1], coordinate2[0], coordinate2[1]]  # 轨迹向量
    for key in dic.keys():
        if len(dic[key]) == 1:  #如果候选路段只有一个点
            tem_coor1 =  Get_Coordinate(dic[key][0][0])#临时坐标1
            tem_li = Find_next_Point(dic[key][0][1],key) #接受返回的查询结果 node_id  sequence_id (2207731639, 17)
            #print(tem_li)
            tem_coor2 = Get_Coordinate(tem_li[0])
            if dic[key][0][1]>tem_li[1]:
                #tem_coor1的sequence_id 大于tem_coor2的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]

            Cosine =  angle(v1,v2)  #接受角度
            #print(key, v2,Cosine)
            distance = Point_Line_Distance([coordinate1[0],coordinate1[1]],[coordinate2[0],coordinate2[1]],[tem_coor1[0],tem_coor1[1]])
            Candidate_dic[key] = [distance,Cosine]
        else:
            #候选路段有两个点及以上
            num1,num2 = Find_two_Point(dic[key],coordinate1[0], coordinate1[1])
            tem_coor1 = Get_Coordinate(dic[key][num1][0])  # 临时坐标1
            tem_coor2 = Get_Coordinate(dic[key][num2][0])  # 临时坐标1
            if dic[key][num1][1]>dic[key][num2][1]:     #第一个点的sequence_id 大于 第二点的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]

            Cosine = angle(v1, v2)
            #print(key, v2, Cosine)
            distance = Point_Line_Distance([coordinate1[0], coordinate1[1]], [coordinate2[0], coordinate2[1]],
                                           [tem_coor1[0], tem_coor1[1]])
            Candidate_dic[key] = [distance, Cosine]
    return Candidate_dic
def Select_Route_By_Normal(dic):
    """
    从候选路段中选出最终的way，由于距离和角度不在一个数量级，归一化后通过权重选出最终的way
    (x-min)/(max-min)
    :param dic: 候选路段字典如：{47574526: [0.00011365462819997119, 34]}
    :return:
    """
    weight = float("-inf")
    return_key = None

    for key in dic.keys():

        weight_d = (1/(1+dic[key][0]))*0.5
        weight_angle = (math.cos((dic[key][1]/180 ) * math.pi))*0.5
        tem_weight =weight_d + weight_angle
        print(tem_weight)
        if tem_weight > weight:

            weight = tem_weight
            return_key = key
    return return_key
def Find_Candidate_Route(coordinate1,coordinate2,flag=1):
    """
        通过车辆轨迹的两个坐标选出匹配的候选路段
        :param coordinate1: 坐标1 及其编号   如[116.5256651,39.7467991，1526,747]
        :param coordinate2: 坐标2 及其编号   如[116.5256651,39.7467991，1526,747]
        :param flag 如果flag==1 计算coordinate1 ==2 计算coordinate2
        :return: 返回候选路段编号  way_id及其序列编号sequence
        得到点的相近点  计算距离 方向
        """

    """
    dic示例：
    dic = {'47574526': [[2207731604,51], [2207731608,50],[3247242227,49]], '152616724': [[2207731637,16]], '606768166': [[2207731637,9]],
          '238769500': [[3247242225,2],[3247242227,1]],
          '242945771': [[6168242644,19]]}
    """
    dic = {}
    if flag == 1:  # 计算该路段的起点归属相近点

        dic = Find_nearby_Point(coordinate1[2], coordinate1[3])
        #print(dic)
    elif flag == 2:  # 计算该路段的终点相近点

        dic = Find_nearby_Point(coordinate2[2], coordinate2[3])
        #print(dic)
    else:
        return None
    Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2)
    point_Candidate = {}
    for key in Candidate_Route_dic.keys():
        if Candidate_Route_dic[key][1] > 120:  # 轨迹与路网大于90度
            pass
        else:
            point_Candidate[key] = Candidate_Route_dic[key]
    # print(point_Candidate)
    return point_Candidate

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
    way_id = None
    if len(Intersection_dic) > 1:  # 交集之后候选路段大于1
        # 方向与距离权重衡量
        pass
    elif len(Intersection_dic) == 1:  # 无交集
        way_id = list(Intersection_dic.keys())[0]
    else:
        pass
        # 如果没有交集 则分段,暂时不处理
    # return way_id
def list2kml(pointsList,filename,savepath):
    """
    列表转kml文件
    :param pointsList:
    :param filename:
    :param savepath:
    :return:
    """
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    fullname = filename + '.kml'
    with open(os.path.join(savepath, fullname), 'a') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        file.write('<kml xmlns="http://earth.google.com/kml/2.0">' + '\n')
        file.write('<Document>' + '\n')
        for num in pointsList:
            #print(str(num[0]) + "," + str(num[1]))
            file.write('<Placemark>' + '\n')
            coordinate = "<Point><coordinates>" + str(num[0]) + "," + str(num[1]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
            file.write(coordinate + '\n')
            file.write('</Placemark>' + '\n')
        file.write('</Document>' + '\n')
        file.write('</kml>' + '\n')
def Area_Process(filepath,csvpath,txtpath,minlon,minlat,maxlon,maxlat):
    """
            此函数实现单车辆的区域路径候选路段选取
            :param filepath:车辆文件路径(网格化之后的)
            :param minlon: 区域范围
            :param minlat:
            :param maxlon:
            :param maxlat:
            csvpath 取出该车辆的指定区域，并保存为csv文件，当处理全部区域的时候，可删除此相关部分
            txtpath  轨迹点候选路段保存路径，每辆车保存为一个txt文件
            :return:
        """
    # if not os.path.isdir(csvpath):
    #  os.mkdir(csvpath)
    (tempath, tempfilename) = os.path.split(filepath)  # tempfilename为csv文件名（包含后缀）
    (filename, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    txtfilename = filename + ".txt"
    file = open(os.path.join(txtpath, txtfilename), 'a')
    df = pd.read_csv(filepath, header=None)
    df = df[(df.iloc[:, 2] < maxlon) & (df.iloc[:, 2] > minlon) & (df.iloc[:, 3] < maxlat) & (
            df.iloc[:, 3] > minlat)]
    df = df.sort_values(by=1)
    # df.to_csv(os.path.join(csvpath,tempfilename),index=0,header=0)
    for row in range(df.shape[0]):
        print(df.iloc[row, 2], df.iloc[row, 3])
        if row == 0:

            dic = Find_Candidate_Route([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],
                                       [df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4],
                                        df.iloc[row + 1, 5]], flag=1)
            file.write(str(dic) + "\n")
        elif row == df.shape[0] - 1:
            dic = Find_Candidate_Route(
                [df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4], df.iloc[row - 1, 5]],
                [df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]], flag=2)
            file.write(str(dic) + "\n")
        else:
            dis1 = haversine(df.iloc[row, 2], df.iloc[row, 3], df.iloc[row - 1, 2], df.iloc[row - 1, 3])
            dis2 = haversine(df.iloc[row, 2], df.iloc[row, 3], df.iloc[row + 1, 2], df.iloc[row + 1, 3])
            # 找相邻最近的点做为轨迹方向
            if dis1 < dis2:
                dic = Find_Candidate_Route(
                    [df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4], df.iloc[row - 1, 5]],
                    [df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]], flag=2)

            else:
                dic = Find_Candidate_Route([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],
                                           [df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4],
                                            df.iloc[row + 1, 5]], flag=1)
            file.write(str(dic) + "\n")
    file.close()
def del_adjacent(alist):
    """
    删除相邻重复元素
    :param alist:
    :return:
    """
    for i in range(len(alist) - 1, 0, -1):
         if alist[i] == alist[i-1]:
             del alist[i]
def BatchProcess(csvpath,txtpath,areacsvpath):
    """
    批量处理所有车辆
    :param csvpath: 车辆csv路径
    :param txtpath: 候选路段保存路径
    :param areacsvpath: 选出车辆指定区域后将其保存的路径
    :return:
    """
    if not os.path.isdir(txtpath):
        os.mkdir(txtpath)
    #if not os.path.isdir(csvpath):
        #os.mkdir(csvpath)
    #csvpathlist = RoadFile.findcsvpath(csvpath)
    #for path in csvpathlist:
    with open(r"H:\GPS_Data\Road_Network\BYQBridge\Trunks\BYC.txt",'r') as files:
        print(len(files.readlines()))
        for line in files.readlines():
            path = line.strip('\n')
            Area_Process(path,areacsvpath,txtpath,116.3906755,39.6905694,116.4958043,39.7506401)  #此区域以北野场桥区域为例

#BatchProcess(None,"H:\GPS_Data\Road_Network\BYQBridge\CandidateWay","H:\GPS_Data\Road_Network\BYQBridge\TrunksArea") #第一个参数后期更换




"""
#以下代码均为测试
#以下点为000dd3e8-d174-4f59-ae90-6d9863fe2ab9辆在北野场桥的点  具体见图片H:\GPS_Data\Road_Network\BYCBridge\Trunks\KML
Point_A = [116.427295,39.721135,1428,722]
Point_B = [116.441663,39.720951,1442,721]
Point_C = [116.445263,39.723566,1446,724]
Point_D = [116.453246,39.724846,1454,725]
Point_E = [116.446415,39.724231,1447,725]
Point_F = [116.441463,39.723983,1442,724]
Point_G = [116.436166,39.7231,1437,724]

start_time = time.time()
#way_id = Find_Candidate_Route([116.427295,39.721135,1428,722],[116.441663,39.720951,1442,721])  #选出该轨迹的归属路段ID
Find_Candidate_Route([116.427295,39.721135,1428,722],[116.441663,39.720951,1442,721]) #A——B
Find_Candidate_Route([116.441663,39.720951,1442,721],[116.445263,39.723566,1446,724]) #B——C
Find_Candidate_Route(Point_D,Point_E)
Find_Candidate_Route(Point_E,Point_F)
Find_Candidate_Route(Point_F,Point_G) #F——G

#coor_list = Fill_Points(47574526,Point_A,Point_B)

#points = [[116.427295,39.721135],[116.4274047, 39.7211178], [116.428484, 39.721102], [116.4298015, 39.7210816], [116.4309455, 39.721055], [116.4314972, 39.7210466], [116.4318185, 39.7210295], [116.4322978, 39.7210258], [116.4329665, 39.7210645], [116.4337314, 39.7211236], [116.4350331, 39.7211041], [116.4355501, 39.7210265],[116.441663,39.720951]]
#list2kml(points,"text_47574526","H:\GPS_Data\Road_Network\BYQBridge\Trunks\KML")

#路段：A-B  被选出为：47574526
#路段：BC   被选出为：47574526
#路段 FG 应该选way_id  242945771




print("*********************************")
#以下点为003b5b7e-e72c-4fc5-ac6d-bcc248ac7a16辆在北野场桥的点  具体见图片H:\GPS_Data\Road_Network\BYCBridge\Trunks\KML
AB_1 = [116.443195,39.723886,1444,724]
AB_2 = [116.436326,39.72201,1437,723]

CD_1 = [116.437743,39.720175,1438,721]
CD_2 = [116.439421,39.71927,1440,720]
DE_2 = [116.440981,39.71747,1441,718]
EF_1 = [116.44636799999999,39.70594000000001,1447,706]
Find_Candidate_Route(AB_1,AB_2)  #有两个way_id
Find_Candidate_Route(AB_2,CD_1)
Find_Candidate_Route(CD_1,CD_2)
Find_Candidate_Route(CD_2,DE_2)
Find_Candidate_Route(DE_2,EF_1)


#以下点为00406a40-8734-4679-9b3c-35720c02af89辆在北野场桥的点  具体见图片H:\GPS_Data\Road_Network\BYCBridge\Trunks\KML
A = [116.429886,39.7212,1430,722]
B = [116.435615,39.721731,1436,722]
C = [116.442311,39.723415,1443,724]
D = [116.449615,39.724183,1450,725]
#Find_Candidate_Route(A,B)  #正确选择：318323104

#以下点为006b7fa2-c58b-4743-925f-d3da0764a362辆在北野场桥的点  具体见图片H:\GPS_Data\Road_Network\BYCBridge\Trunks\KML

print("*********************************")
AA = [116.4556,39.724853,1456,725]
BB = [116.448836,39.724255,1449,725]
CC = [116.436488,39.721958,1437,722]
DD = [116.439721,39.719035,1440,720]
EE = [116.442351,39.714918,1443,715]
FF = [116.444851,39.709875,1445,710]
Find_Candidate_Route(AA,BB)
Find_Candidate_Route(BB,CC)
Find_Candidate_Route(CC,DD)
Find_Candidate_Route(DD,EE)
Find_Candidate_Route(EE,FF)
print("*********************************")
#0d201cd1-0a18-43c0-9e16-f10f62833dd9
AAA = [116.442631,39.715395,1443,716]
BBB = [116.440796,39.720906,1441,721]
CCC = [116.441106,39.723395,1442,724]
DDD = [116.437556,39.723076,1438,724]
EEE = [116.424986,39.7214,1425,722]
FFF = [116.408851,39.720116,1409,721]
Find_Candidate_Route(AAA,BBB)
Find_Candidate_Route(BBB,CCC)
Find_Candidate_Route(CCC,DDD)
Find_Candidate_Route(DDD,EEE)
Find_Candidate_Route(EEE,FFF)


print("耗时：{}".format(time.time() - start_time))
di = Find_nearby_Point(1414,721)
print(di)
print(Find_Candiate_Point(di,[116.413665,39.720553,1714,721],[116.418073,39.721097,1719,722]))
#print(angle([116.4180109,39.7210628,116.4193757,39.7211948],[116.418073,39.721097,116.418073,39.721096]))
"""
di = Find_nearby_Point(1414,721)
print(di)
print(Find_Candiate_Point(di,[116.413665,39.720553,1714,721],[116.418073,39.721097,1719,722]))
