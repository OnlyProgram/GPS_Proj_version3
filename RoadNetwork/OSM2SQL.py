# -*- coding: utf-8 -*-
# @Time    : 2019/5/14 19:03
# @Author  : WHS
# @File    : OSM2SQL.py
# @Software: PyCharm
"""
OSM文件转到数据库
"""
import pymysql
import json
from tqdm import tqdm
import math
# 打开数据库连接
connection = pymysql.connect(host='localhost', user='root',passwd='123456', charset='utf8')

def CreatMysqlDatabase(database_name):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = connection.cursor()
    sql = "create database {} character set utf8;".format(database_name)
    try:
        cursor.execute(sql)
        print('创建{}库完成'.format(database_name))
    except Exception as e:
        print(e)
    cursor.close()
def CreatTable(dbname,tablename,sql):
    """

    :param dbname: 数据库名
    :param tablename: 表名
    :param sql  sql语句
    :return:
    """
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    cursor.execute("DROP TABLE IF EXISTS {}".format(tablename))

    # 使用预处理语句创建表

    cursor.execute(sql)
    cursor.close()
    print('表{}创建完成'.format(tablename))
def InsrtNodes(dbname,tablename):
    print("Nodes开始导入数据库...")
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    count = 0
    with open(r'H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\AllNodes.json','r') as file:
        dic = json.loads(file.read())
        with tqdm(total=len(dic)) as pbar:
            for key in dic.keys():
                x_grid = math.ceil((dic[key][1] - 115) / 0.001)  # x方向格子编号
                y_grid = math.ceil((dic[key][0] - 39) / 0.001)  # y方向格子编号
                sql_insert = 'insert into {}(Node_id,Lon,Lat,X_Grid,Y_Grid) values({},{},{},{},{});'.format(tablename,key, dic[key][1],
                                                                                            dic[key][0],x_grid,y_grid)
                try:
                    cursor.execute(sql_insert)  # 执行sql语句
                    connection.commit()  # 提交
                    count += 1
                    pbar.update(1)
                except Exception as e:
                    print(e)
                    connection.rollback()
                    cursor.close()

    #print("\n已成功添加{}条记录".format(count))
def InsrtWays(dbname,tablename):
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    print("ways信息开始导入数据库...")
    count = 0
    with open(r'H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\ways.json', 'r') as file:
        dic = json.loads(file.read())
        with tqdm(total=len(dic)) as pbar:
            for key in dic.keys():
                if len(dic[key])==1:
                    sql_insert = 'insert into {}(way_id,node_id,sequence_id) values({},{},{},{});'.format(tablename,key, dic[key],1)
                    try:
                        cursor.execute(sql_insert)  # 执行sql语句
                        connection.commit()  # 提交
                        count += 1
                        pbar.update(1)
                    except Exception as e:
                        print(e)
                        connection.rollback()
                        cursor.close()

                else:
                    for num in range(len(dic[key])):  # sequence代表每条路中node的排序号
                        sequence = num + 1
                        sql_insert = 'insert into {}(way_id,node_id,sequence_id) values({},{},{});'.format(tablename,
                                                                                                              key,
                                                                                                              dic[key][num],
                                                                                                              sequence)
                        try:
                            cursor.execute(sql_insert)  # 执行sql语句
                            connection.commit()  # 提交
                            count += 1
                        except Exception as e:
                            print(e)
                            connection.rollback()
                            cursor.close()
                    pbar.update(1)
def Extract_Inflection_point(databasename,tablename):
    """
    从数据库的ways_nodes表中提取拐点,并保存到tablename表
    #返回字典  键为node_id   值为way_id  值为列表，代表此node_id是哪几个way的交叉点
    :param databasename 数据库名
    :param tablename 存储拐点的表名
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(databasename))
    sql =   """
    (SELECT a.node_id,a.way_id
    FROM ways_nodes a,(select way_id,node_id,COUNT(node_id)
    FROM ways_nodes
    GROUP BY node_id
    HAVING COUNT(node_id)>1
    ORDER BY way_id) b
    WHERE a.node_id =b.node_id AND a.way_id<>b.way_id )
    UNION
    (SELECT a.node_id,b.way_id
    FROM ways_nodes a,(select way_id,node_id,COUNT(node_id)
    FROM ways_nodes
    GROUP BY node_id
    HAVING COUNT(node_id)>1
    ORDER BY way_id) b
    WHERE a.node_id =b.node_id AND a.way_id<>b.way_id)
    """
    #node_way_dict ={}  #键为node_id，值为way_id
    index = 1
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            sql_insert = 'insert into {}(`Index_id`, `NodeID`, `WayID`) values({},{},{});'.format(tablename, index,
                                                                                                    row[0], row[1])
            try:
                cursor.execute(sql_insert)  # 执行sql语句
                connection.commit()  # 提交
                index += 1
            except Exception as e:
                print(e)
                connection.rollback()
                cursor.close()

            # tem_lis = [row[1]]
            # if row[0] in node_way_dict:
            #     node_way_dict[row[0]].extend(tem_lis)
            # else:
            #     node_way_dict[row[0]] = tem_lis
    except Exception as e:
        print(e)
        connection.rollback()
        cursor.close()
        connection.close()
    #return node_way_dict


#运行示例
#nodesql = """CREATE TABLE {}(`Node_id` BIGINT  NOT NULL PRIMARY KEY,`Lon` DOUBLE   NOT NULL,`Lat` DOUBLE   NOT NULL,`X_Grid` INT NOT NULL,`Y_Grid` INT NOT NULL)CHARSET=utf8;""".format(tablename)
#CreatMysqlDatabase("BJOSM")
#CreatTable("bjosm","Nodes",nodesql)
#InsrtNodes("bjosm","Nodes")
#InsrtWays("bjosm","ways_nodes")
Extract_Inflection_point("bjosm","inflectionpoint")
