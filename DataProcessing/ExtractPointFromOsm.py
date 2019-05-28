# -*- coding: utf-8 -*-
# @Time    : 2019/5/9 14:48
# @Author  : WHS
# @File    : ExtractPointFromOsm.py
# @Software: PyCharm
"""
从osm中提取路网点，提出河流 建筑物等
"""
# 116.4291555478   116.4484684983
#  39.7145287254    39.7288490146
import re
import os
import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
def CountHighwayclass(osmpath):
    """
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
"""
#可删除此函数
def GetAllNodes(osmpath,savekmlpath):
    #从osm中提取所有坐标点，包含河流，建筑物，路网等,并保存为kml文件
    #:param osmpath: osm文件所在路径  如：H:\GPS_Data\Road_Network\BYCBridge\BYC.osm
    #:param savekmlpath kml文件保存路径 如：H:\GPS_Data\Road_Network\BYCBridge\KML  若路径不存在会自动创建，文件名与osm文件同名
    #:return:
    
    if os.path.isfile(savekmlpath):
        print("第二个参数应该为目录，而不是文件,如：H:\GPS_Data")
        return
    if not os.path.isdir(savekmlpath):
        os.mkdir(savekmlpath)

    (filepath, tempfilename) = os.path.split(osmpath)
    (filename, extension) = os.path.splitext(tempfilename)  # extension为后缀
    kmlfilename = filename +".kml"
    kmlfullpath = savekmlpath+os.sep+kmlfilename
    if os.path.exists(kmlfullpath):
        print("{}文件已存在，请勿重复运行，否则数据将重复，或者删除kml文件!".format(kmlfullpath))
        return
    kmlfile = open(kmlfullpath, 'a')
    with open(osmpath, 'r', encoding='utf-8') as file:
        coordinatenum = 0
        kmlfile.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        kmlfile.write('<kml xmlns="http://earth.google.com/kml/2.0">' + '\n')
        kmlfile.write('<Document>' + '\n')
        for line in file.readlines():
            coordinate = re.findall('<node id.*?lat="(.*?)" lon="(.*?)"/>', line.strip('\n'), re.M | re.S)
            coordinate2 = re.findall('<node id.*?lat="(.*?)" lon="(.*?)">', line.strip('\n'), re.M | re.S) #此类点都做了标记 如车站等，可以选择不提取
            if coordinate:
                kmlfile.write('<Placemark>' + '\n')
                coordinates = "<Point><coordinates>" + coordinate[0][1] + "," + str(
                    coordinate[0][0]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
                kmlfile.write(coordinates + '\n')
                kmlfile.write('</Placemark>' + '\n')
                coordinatenum += 1
                #print(coordinate[0][1], coordinate[0][0])
            elif coordinate2:
                kmlfile.write('<Placemark>' + '\n')
                coordinates = "<Point><coordinates>" + coordinate2[0][1] + "," + str(
                    coordinate2[0][0]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
                kmlfile.write(coordinates + '\n')
                kmlfile.write('</Placemark>' + '\n')
                coordinatenum += 1
                #print(coordinate2[0][1], coordinate2[0][0])
            else:
                pass
        kmlfile.write('</Document>' + '\n')
        kmlfile.write('</kml>' + '\n')
        kmlfile.close()
        print("提取坐标点数目为：{}".format(coordinatenum))
        print("文件保存路径为{}".format(kmlfullpath))
"""
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
    kmlfullpath = savekmlpath + os.sep + kmlfilename
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
    jsonfilename = "ways" + ".json"
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
                road_flag = True                 #标记这个way为highway
                break
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
savejsonpath = "H:\GPS_Data\Road_Network\BYCBridge\JSON"
savekmlpath = "H:\GPS_Data\Road_Network\BYQBridge\KML\BigBYCQ"
jsonsavepath = "H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ"
jsonfile = "H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\\highway.json"

#FindClassNode(osmpath,jsonsavepath)
#JsontoKml(jsonfile,savekmlpath)
#CountHighwayclass(osmpath)
Extract_Way(osmpath,jsonsavepath)
"""
#根据节点编号得到经纬度
waypointlist = [1318916989,1318917028,4572789792,1318917013,1318917042,2207731472,2207731447,3247242149]
with open(jsonfile,'r') as file:
    dic = json.loads(file.read())
for nodeid in waypointlist:
    print(dic[str(nodeid)][1],dic[str(nodeid)][0])
"""
