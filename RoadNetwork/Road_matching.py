# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 9:01
# @Author  : WHS
# @File    : Road_matching.py
# @Software: PyCharm
"""
道路匹配,直接采用GPS坐标在直角坐标系下算距离，0.001大概为100米左右，即0.1公里
"""
import pymysql
import math
import os
from math import radians, cos, sin, asin, sqrt
import glob
import time
from tqdm import tqdm
import RoadNetwork.FilesFunctions as RoadFile
from RoadNetwork import map_navigation
import pandas as pd
from tqdm import tqdm

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
    #print(node_id_dict)
    #print(len(node_id_dict))
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
            #print(key, v2,Cosine)
            if flag==1:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
            else:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate2[0], coordinate2[1]])  # 计算轨迹点(终点)到道路的距离
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
            #print("{}轨迹向量V2:{}".format(key,v2))
            Cosine = angle(v1, v2)
            #print(key, v2, Cosine)
            if flag == 1:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
            else:
                distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                               [coordinate2[0], coordinate2[1]])  # 计算轨迹点(终点)到道路的距离
            Candidate_dic[key] = [distance, Cosine]
    #print(Candidate_dic)
    return Candidate_dic
def Select_Route_By_Normal(dic):
    """
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
    if flag==1:   #计算该路段的起点归属相近点
        dic = Find_nearby_Point(coordinate1[2], coordinate1[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2,flag=1)
       # print(dic)
    elif flag==2:  #计算该路段的终点相近点
        dic = Find_nearby_Point(coordinate2[2], coordinate2[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2, flag=2)
    else:
        return None
    #print("轨迹点的相近路网点{}".format(dic))

    point_Candidate = {}
    for key in Candidate_Route_dic.keys():
        # 轨迹与路网方向阈值暂定设置为180，由于轨迹中前后点方向可能与路网相反,点到道路距离大 于30米
        if Candidate_Route_dic[key][1] > 180 or Candidate_Route_dic[key][0] > 0.0004:
            pass
        else:
            point_Candidate[key] = Candidate_Route_dic[key]
    #print("候选路段：{}".format(point_Candidate))
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
    if not os.path.isdir(csvpath):
        os.mkdir(csvpath)
    (tempath, tempfilename) = os.path.split(filepath)  #tempfilename为csv文件名（包含后缀）
    (filename, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    txtfilename = filename + ".txt"
    file = open(os.path.join(txtpath,txtfilename), 'a')
    df = pd.read_csv(filepath, header=None)
    df = df[(df.iloc[:, 2] < maxlon) & (df.iloc[:, 2] > minlon) & (df.iloc[:, 3] < maxlat) & (
            df.iloc[:, 3] > minlat)]
    #df = df.sort_values(by=1)  #第一次处理加上
    #pd.set_option('display.max_columns', None)
    # 显示所有行
    #pd.set_option('display.max_rows', None)
    #df.to_csv(os.path.join(csvpath,tempfilename),index=0,header=0)
    #print(df.iloc[:,1:4])
    for row in range(df.shape[0]):
        #print(row,df.iloc[row, 2], df.iloc[row, 3])
        if row==0:
            pass
        elif df.iloc[row, 2]==df.iloc[row-1,2] and df.iloc[row, 3]==df.iloc[row-1,3]: #当前点与上一点重复，则不查找此点
            continue
        if row == 0:
            #print("处理起始坐标点{}".format([df.iloc[row, 2],df.iloc[row, 3],df.iloc[row + 1,2],df.iloc[row + 1, 3]]))
            dic = Find_Candidate_Route([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],
                                       [df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4],
                                        df.iloc[row + 1, 5]],flag=1)
            if dic:  #有候选路段才保存
                file.write(str(dic) + "\n")
        elif row == df.shape[0] - 1:
            #print("处理终点坐标点{}".format([df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
            dic = Find_Candidate_Route(
                [df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4], df.iloc[row - 1, 5]],
                [df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],flag=2)
            if dic:
                file.write(str(dic) + "\n")
        else:
            dis1 = haversine(df.iloc[row, 2], df.iloc[row, 3], df.iloc[row - 1, 2], df.iloc[row - 1, 3])
            dis2 = haversine(df.iloc[row, 2], df.iloc[row, 3], df.iloc[row + 1, 2], df.iloc[row + 1, 3])
            #找相邻最近的点做为轨迹方向
            if dis2 > dis1:
                #print("处理终点坐标点{}".format([df.iloc[row-1, 2], df.iloc[row-1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
                dic = Find_Candidate_Route(
                    [df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4], df.iloc[row - 1, 5]],
                    [df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],flag=2)

            else:
               # print("处理起始坐标点{}".format([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row + 1, 2], df.iloc[row + 1, 3]]))
                dic = Find_Candidate_Route([df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4], df.iloc[row, 5]],
                                           [df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4],
                                            df.iloc[row + 1, 5]],flag=1)
            if dic:
                file.write(str(dic) + "\n")
    file.close()
def routelist_process(route_list):
    """
    route_list 是双层嵌套列表，此函数实现双层列表去重，并展开为一层列表，再对相邻重复元素去重
    :param route_list: 如：
    :return:
    """
    new_list = [list(t) for t in set(tuple(_) for _ in route_list)]  # 嵌套列表去重
    new_list.sort(key=route_list.index)
    print(new_list)
    # res = list(filter(None, s))
    result = [item for sub in new_list for item in sub]  # 二层嵌套列表展开为一层
    print(result)
    #del_adjacent(result)  # 去除相邻的重复元素
    #print(result)
    newlist = list(set(result))
    newlist.sort(key=result.index)
    return  newlist
def del_adjacent(alist):
    """
    删除相邻重复元素
    :param alist:
    :return:
    """
    for i in range(len(alist) - 1, 0, -1):
         if alist[i] == alist[i-1]:
             del alist[i]
def FindRouteBatchProcess(csvpath,txtpath,areacsvpath):
    """
    批量处理所有车辆，找出轨迹点的候补路段
    :param csvpath: 车辆csv路径
    :param txtpath: 候选路段保存路径
    :param areacsvpath: 选出车辆指定区域后将其保存的路径
    :return:
    """
    if not os.path.isdir(txtpath):
        os.mkdir(txtpath)
    #if not os.path.isdir(csvpath):
        #os.mkdir(csvpath)
    #
    #with open(r"H:\GPS_Data\Road_Network\BYQBridge\Trunks\BYC.txt",'r') as files:
        #for line in files.readlines():
            #path = line.strip('\n')
    csvpathlist = RoadFile.findcsvpath(csvpath)
    with tqdm(total=len(csvpathlist)) as pbar:
        for path in csvpathlist:
            if path == "H:\GPS_Data\Road_Network\BYQBridge\TextArea\\334e4763-f125-425f-ae42-8028245764fe.csv" or \
                    path == "H:\GPS_Data\Road_Network\BYQBridge\TextArea\\f1f99a55-76cb-413c-b959-5b0dfe00d528.csv":  # 这两个文件已测试处理
                pbar.update(1)
                continue
            Area_Process(path, areacsvpath, txtpath, 115, 38, 118, 40)  # 此区域以北野场桥区域为例
            pbar.update(1)
csvpath = "H:\GPS_Data\Road_Network\BYQBridge\TextArea"
#FindRouteBatchProcess(csvpath,"H:\GPS_Data\Road_Network\BYQBridge\CandidateWay","H:\GPS_Data\Road_Network\BYQBridge\TrunksArea") #第一个参数后期更换

def SelectFinalRoute(txtpath,finalroutesavepath,finalname):
    """

    :param txtpath: 候选路段txt文件路径
    :param finalroutesavepath:  选出的最后路径保存为txt文件
    :return:
    """
    (tempath, tempfilename) = os.path.split(txtpath)  # tempfilename为csv文件名（包含后缀）
    (filename, extension) = os.path.splitext(tempfilename)  # filename 为传入的txt文件名 extension为后缀
    Point_attr_line = []  #存储每个轨迹点所属的路段
    route_list = []  # 完整路线
    with open(txtpath, 'r') as file:
        lines = file.readlines()
        linesNums = len(lines)
        #print(linesNums)
        for linenum in range(linesNums):

            if linenum + 4 >= linesNums:  # 最后一次滑动大于最后一个点的编号，linenum代表行数
                #print("处理坐标编号{},{},{},{},{}".format(linenum, linenum + 1, linenum + 2, linenum + 3,linenum + 4))
                routeline = map_navigation.Select_Route(eval(lines[-5].strip('\n')),
                                              eval(lines[-4].strip('\n')),
                                              eval(lines[-3].strip('\n')),
                                              eval(lines[-2].strip('\n')),
                                              eval(lines[-1].strip('\n')))
                route_list.append(routeline)
                break
            else:
                start_linenum = linenum
                #print("处理坐标编号{},{},{},{},{}".format(start_linenum, start_linenum + 1, start_linenum + 2,start_linenum + 3,start_linenum + 4))
                routeline = map_navigation.Select_Route(eval(lines[start_linenum].strip('\n')),
                                              eval(lines[start_linenum + 1].strip('\n')),
                                              eval(lines[start_linenum + 2].strip('\n')),
                                              eval(lines[start_linenum + 3].strip('\n')),
                                              eval(lines[start_linenum + 4].strip('\n')))
                route_list.append(routeline)
    for index in range(len(route_list)):
        if index == len(route_list)-1:
            Point_attr_line.extend(route_list[index])
        elif len(route_list[index])!=0:
            Point_attr_line.append(route_list[index][0])
        else:
            pass
    safilename = finalname +".txt"
    with open(os.path.join(finalroutesavepath,safilename),'a') as file:
        file.write(filename + "\n")
        file.write(str(route_list)+"\n")
        file.write(str(Point_attr_line)+"\n\n")


#Find_Candidate_Route([116.435285,39.73246,1436,733],[116.435285,39.732461,1436,733],flag=1)
#print(Point_Line_Distance([116.4347764, 39.7326724], [116.434316, 39.7335476],[116.435285,39.73246]))
def BatchProcessFinalRoutes():
    """
    批量处理选取最后的路线
    :return:
    """
    txtfilespath = "H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\test"
    txt_list = glob.glob(os.path.join(txtfilespath, '*.txt'))
    savepath = "H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes"
    savefilename = "tsetfinallines"
    csvfilenum = len(txt_list)
    # for subfile in txt_list:
    #     print("\n正在处理{} \n".format(str(subfile).split("\\")[-1]))
    #     SelectFinalRoute(subfile, savepath, savefilename)
    with tqdm(total=csvfilenum) as pbar:
        for subfile in txt_list:
            print("\n正在处理{} \n".format(str(subfile).split("\\")[-1]))
            SelectFinalRoute(subfile, savepath, savefilename)
            pbar.update(1)
#starttime = time.time()
#BatchProcessFinalRoutes()
#print("耗时：{}".format(time.time()-starttime))
