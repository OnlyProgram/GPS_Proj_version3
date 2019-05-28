# -*- coding: utf-8 -*-
# @Time    : 2019/5/26 19:01
# @Author  : WHS
# @File    : Get_line_By_routes.py
# @Software: PyCharm
import pymysql
import os
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
def list2kml(pointsList,filename,savepath):
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    fullname = filename + '.kml'
    with open(os.path.join(savepath, fullname), 'a') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        file.write('<kml xmlns="http://earth.google.com/kml/2.0">' + '\n')
        file.write('<Document>' + '\n')
        for num in pointsList:
            file.write('<Placemark>' + '\n')
            coordinate = "<Point><coordinates>" + str(num[0]) + "," + str(num[1]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
            file.write(coordinate + '\n')
            file.write('</Placemark>' + '\n')
        file.write('</Document>' + '\n')
        file.write('</kml>' + '\n')
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
routes = [58693809, 47574526, 242945775, 47574526, 318323155, 437527025, 606768160, 606768157,
          437527026, 606768158, 606768162, 466839077, 606769453, 47612702, 466839075]
All_nodes = []
All_coordinates = []
for wayid in set(routes):
    node_lis = Get_way_nodes(wayid)
    All_nodes.extend(node_lis)
for nodeid in All_nodes:
    All_coordinates.append(Get_Coordinate(nodeid))
list2kml(All_coordinates,"334e4763-f125-425f-ae42-8028245764fe","H:\GPS_Data\Road_Network\BYQBridge\Trunks")