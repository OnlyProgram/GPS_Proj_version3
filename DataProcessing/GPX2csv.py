# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 22:21
# @Author  : WHS
# @File    : GPX2csv.py
# @Software: PyCharm
import pandas as pd
from xml.dom.minidom import parse
import xml.dom.minidom
import os

# 使用minidom解析器打开 XML 文档

def gpx2csv(infile,outfile):
    domtree = xml.dom.minidom.parse(infile)
    collection = domtree.documentElement

    edgeids=collection.getElementsByTagName("edgeid")
    edgeidarray=[]
    for i in edgeids:
        eid=float(i.childNodes[0].data)
        edgeidarray.append(int(eid))

    latarray=[]
    lonarray=[]
    pionts=collection.getElementsByTagName("trkpt")
    for piont in pionts:
        lat=piont.getAttribute('lat')
        latarray.append(lat)

        lon=piont.getAttribute('lon')
        lonarray.append(lon)

    data=pd.DataFrame({'lon':lonarray,'lat':latarray,'edgeid':edgeidarray})
    data[['lon','lat','edgeid']].to_csv(outfile,index=False)


def foreachfile(filespath):
    files=os.listdir(filespath)
    for file in files:
        infilepath=filespath+"\\"+file
        outfilepath="放csv文件的文件路径"
        gpx2csv(infilepath,outfilepath)

foreachfile("存gpx文件的文件夹")
