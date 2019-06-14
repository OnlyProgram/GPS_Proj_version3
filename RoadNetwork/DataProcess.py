# -*- coding: utf-8 -*-
# @Time    : 2019/6/14 9:26
# @Author  : WHS
# @File    : DataProcess.py
# @Software: PyCharm
"""
从osm文件中提取node信息、way（剔除人行道、建筑物、河流等信息）
k值：footway；cycleway（自行车道）；pedestrian；track（小径 通常指未铺设的道路）bus_guideway（公交车专用通道）raceway（比赛专用车道）

目前只剔除河流、footway；cycleway raceway  residential
"""
import re
import os
import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
def CountHighwayclass(osmpath):
    """
    示例：CountHighwayclass("H:\GPS_Data\Road_Network\BYQBridge\BYQ2.osm")
    统计osm文件中key=highway 的对应的value的取值范围
    :param osmpath: osm文件路径 如：H:\GPS_Data\Road_Network\BYCBridge\BYC.osm
    :return:
    """
    highway_set = set()
    with open(osmpath, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            high_class = re.findall('<tag k="highway" v="(.*?)"/>',line)
            if high_class:
                highway_set.add(high_class[0])
    print(highway_set)


def FindClassNode(osmpath,savejsonpath,classNode = "highway"):
    """
    查找路节点，保存为json
    :param osmpath osm文件路径  如：H:\GPS_Data\Road_Network\BYCBridge\BYC.osm
    :param savejsonpath json文件保存路径 :param savekmlpath kml文件保存路径 如：H:\GPS_Data\Road_Network\BYCBridge\KML  若路径不存在会自动创建，文件名与classNode同名
    :param classNode 要查找的类别节点 默认查找类别为：highway
    :param saveAllNodespath 所有点保存的json
    :return:
    """
    kmlfilename = "AllNodes" + ".json"
    kmlfullpath = savejsonpath + os.sep + kmlfilename
    if os.path.exists(kmlfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将覆盖，请先删除对应json文件!".format(kmlfullpath))
        return
    if os.path.isfile(savejsonpath):
        print("第二个参数应该为目录，而不是文件,如：H:\GPS_Data")
        return
    if not os.path.isdir(savejsonpath):
        os.mkdir(savejsonpath)
    osmfile = open(osmpath, 'r', encoding='utf-8')
    dom = xml.dom.minidom.parse(osmfile)
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')  #所有的node
    waylist = root.getElementsByTagName('way')  #所有的路

    node_dic = {}
    # 统计记录所有node
    for node in nodelist:
        node_id = node.getAttribute('id')
        node_lat = float(node.getAttribute('lat'))
        node_lon = float(node.getAttribute('lon'))
        node_dic[node_id] = (node_lat, node_lon)

    print("节点数：{}".format(len(node_dic)))
    with open(kmlfullpath, 'w') as fout:
        json.dump(node_dic, fout,indent=4)
    print("文件保存路径为{}".format(kmlfullpath))  #所有节点
    jsonfilename = classNode + ".json"
    jsonfullpath = savejsonpath + os.sep + jsonfilename
    if os.path.exists(jsonfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将覆盖，请先删除对应的json文件!".format(jsonfullpath))
        return
    # 排除非路node，如果node在way中，则保留
    way_node_lists = []
    for way in waylist:
        taglist = way.getElementsByTagName('tag')
        road_flag = False
        for tag in taglist:                     #遍历way中的所有tag标签
            if tag.getAttribute('k') == classNode:

                road_flag = True                 #标记这个way为highway
        if road_flag:
            ndlist = way.getElementsByTagName('nd')  #way中的所有node
            for nd in ndlist:
                nd_id = nd.getAttribute('ref')
                way_node_lists.append(nd_id)
    way_node_dic = {}
    for key in node_dic.keys():
        if key in way_node_lists:
            way_node_dic[key] = node_dic[key]
        else:pass
   # print(len(way_node_dic))
    #print(way_node_dic)
    with open(jsonfullpath, 'w') as fout:
        json.dump(way_node_dic,fout,indent=4)
    osmfile.close()
    print("文件保存路径为{}".format(jsonfullpath))
def Find_all_way_node(osmpath,savejsonpath,classNode = "highway"):
    """
    分别保存所有节点node和路对应的node，（剔除河流、footway；cycleway raceway  residential），
    FindClassNode没有剔除footway；cycleway raceway  residential，其他功能与本函数功能相同
    :param osmpath osm文件路径  如：H:\GPS_Data\Road_Network\BYCBridge\BYC.osm
    :param savejsonpath json文件保存路径 :param savekmlpath kml文件保存路径 如：H:\GPS_Data\Road_Network\BYCBridge\KML  若路径不存在会自动创建，文件名与classNode同名
    :param classNode 要查找的类别节点 默认查找类别为：highway
    :param saveAllNodespath 所有点保存的json
    :return:
    """
    del_ways_v = ['footway', 'cycleway', 'raceway', 'residential']
    kmlfilename = "AllNodes" + ".json"
    kmlfullpath = savejsonpath + os.sep + kmlfilename
    if os.path.exists(kmlfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将覆盖，请先删除对应json文件!".format(kmlfullpath))
        return
    if os.path.isfile(savejsonpath):
        print("第二个参数应该为目录，而不是文件,如：H:\GPS_Data")
        return
    if not os.path.isdir(savejsonpath):
        os.mkdir(savejsonpath)
    osmfile = open(osmpath, 'r', encoding='utf-8')
    dom = xml.dom.minidom.parse(osmfile)
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')  #所有的node
    waylist = root.getElementsByTagName('way')  #所有的路

    node_dic = {}
    # 统计记录所有node
    for node in nodelist:
        node_id = node.getAttribute('id')
        node_lat = float(node.getAttribute('lat'))
        node_lon = float(node.getAttribute('lon'))
        node_dic[node_id] = (node_lat, node_lon)

    print("节点数：{}".format(len(node_dic)))
    with open(kmlfullpath, 'w') as fout:
        json.dump(node_dic, fout,indent=4)
    print("文件保存路径为{}".format(kmlfullpath))  #所有节点
    jsonfilename = classNode + ".json"
    jsonfullpath = savejsonpath + os.sep + jsonfilename
    if os.path.exists(jsonfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将覆盖，请先删除对应的json文件!".format(jsonfullpath))
        return
    # 排除非路node，如果node在way中，则保留
    way_node_lists = []
    for way in waylist:
        taglist = way.getElementsByTagName('tag')
        road_flag = False
        for tag in taglist:                     #遍历way中的所有tag标签
            if tag.getAttribute('k') == classNode:
                if tag.getAttribute('v') not in del_ways_v:
                   road_flag = True                 #标记这个way为highway
        if road_flag:
            ndlist = way.getElementsByTagName('nd')  #way中的所有node
            for nd in ndlist:
                nd_id = nd.getAttribute('ref')
                way_node_lists.append(nd_id)
    way_node_dic = {}
    for key in node_dic.keys():
        if key in way_node_lists:
            way_node_dic[key] = node_dic[key]
        else:pass
   # print(len(way_node_dic))
    #print(way_node_dic)
    with open(jsonfullpath, 'w') as fout:
        json.dump(way_node_dic,fout,indent=4)
    osmfile.close()
    print("文件保存路径为{}".format(jsonfullpath))

def JsontoKml(jsonpath,kmlsavepath):
    """
    FindClassNode函数生成的Json文件转KML文件
    :param jsonpath: json文件路径 如：H:/text.json
    :param kmlsavepath:  kml文件保存路径 如：H:\GPS_Data\Road_Network\BYCBridge\KML 文件名与传入json文件名同名
    :return:
    """
    if not os.path.isfile(jsonpath):
        print("不是文件,函数{}的第一个参数应传入文件，如H:/text.json".format(JsontoKml))
        return
    with open(jsonpath, 'r') as fout:
        dic = json.loads(fout.read())
    (filepath, tempfilename) = os.path.split(jsonpath)
    (filename, extension) = os.path.splitext(tempfilename)  # extension为后缀
    kmlfilename = filename + ".kml"
    kmlfullpath = kmlsavepath + os.sep + kmlfilename
    if os.path.exists(kmlfullpath):
        print("{}文件已存在，如要继续运行，请删除对应kml文件!".format(kmlfullpath))
        return
    kmlfile = open(kmlfullpath, 'a')
    kmlfile.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
    kmlfile.write('<kml xmlns="http://earth.google.com/kml/2.0">' + '\n')
    kmlfile.write('<Document>' + '\n')
    for key in dic.keys():
        kmlfile.write('<Placemark>' + '\n')
        coordinates = "<Point><coordinates>" + str(dic[key][1]) + "," + str(dic[key][0]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
        kmlfile.write(coordinates + '\n')
        kmlfile.write('</Placemark>' + '\n')
    kmlfile.write('</Document>' + '\n')
    kmlfile.write('</kml>' + '\n')
    kmlfile.close()
    print("文件保存路径为{}".format(kmlfullpath))

def Extract_Way(osmpath,savejsonpath):
    """
    提取路（剔除河流、footway；cycleway raceway  residential），
    :param osmpath:
    :param savejsonpath:
    :return:
    """
    del_ways_v = ['footway', 'cycleway', 'raceway', 'residential']
    jsonfilename = "wayslist" + ".json"
    jsonfullpath = savejsonpath + os.sep + jsonfilename
    if os.path.exists(jsonfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将覆盖，请先删除对应的json文件!".format(jsonfullpath))
        return
    way_dic = {}
    tree = ET.parse(osmpath)
    root = tree.getroot()
    for way in root.findall('way'):
        road_flag = False
        nd_id_list = []
        for tag in way.iter('tag'):
            if tag.attrib['k'] == "highway":
                if tag.attrib['v']  not in del_ways_v:
                    road_flag = True                 #标记这个way为highway
        if road_flag:
            for nd in way.iter('nd'):
                nd_id_list.append(nd.attrib['ref'])
            way_dic[way.attrib['id']] = nd_id_list
        else:pass
    with open(jsonfullpath, 'w') as fout:
        json.dump(way_dic, fout,indent=4)
    print("提取路段共：{}".format(len(way_dic)))
    print("文件保存路径为{}".format(jsonfullpath))
osmpath = "H:\GPS_Data\Road_Network\BYQBridge\BYQ2.osm"
savejsonpath = "H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\Delfootwayetc"
#Extract_Way(osmpath,savejsonpath)
#JsontoKml("H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\Delfootwayetc\highway.json","H:\GPS_Data\Road_Network\BYQBridge\KML\BigBYCQ\delfootway")
#Find_all_way_node(osmpath,savejsonpath)

