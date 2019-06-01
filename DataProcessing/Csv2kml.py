# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 15:12
# @Author  : WHS
# @File    : Csv2kml.py
# @Software: PyCharm
import pandas as pd
import os
import glob
from tqdm import tqdm

"""格式
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
<Placemark>
<description>2</description>
<Point><coordinates>116.56184,39.566791,0</coordinates></Point>
</Placemark>
<Placemark>
<description>2</description>
<Point><coordinates>116.557926,39.5619,0</coordinates></Point>
</Placemark>
</Document>
</kml>
"""
def csvtokml(filename,savepath,cavfilepath):
    df = pd.read_csv(cavfilepath, header=None, usecols=[0, 1, 2])  # 读经纬度，标记
    fullname = filename+'.kml'
    with open(os.path.join(savepath,fullname), 'a') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>' +'\n')
        file.write('<kml xmlns="http://earth.google.com/kml/2.0">' +'\n')
        file.write('<Document>' +'\n')
        for num in range(df.shape[0]):
            file.write('<Placemark>' +'\n')
            des = "<description>"+ str(df.iloc[num,2])+"</description>"
            coordinate = "<Point><coordinates>"+str(df.iloc[num,0])+","+str(df.iloc[num,1])+",0</coordinates></Point>"#此处0代表海拔，如果有海拔，可更改
            file.write(des +'\n')
            file.write(coordinate +'\n')
            file.write('</Placemark>' +'\n')
        file.write('</Document>' +'\n')
        file.write('</kml>' +'\n')
#示例
#csvtokml('text','H:\GPS_Data\\20170901\Top20\KML','H:\GPS_Data\\20170901\Top20\FilledRoute\\036f3c48-fed9-4acc-80ac-61fbad58b1c2Filled.csv')


def original_csvtokml(filename,savepath,cavfilepath):
    """
    原始csv转kml
    :param filename: kml文件名
    :param savepath: 保存路径
    :param cavfilepath: 网格化后的单个车辆路径
    :return:
    """
    df = pd.read_csv(cavfilepath, header=None, usecols=[2, 3],names=[0,1])  # 读经纬度，标记
    fullname = filename+'.kml'
    with open(os.path.join(savepath,fullname), 'a') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>' +'\n')
        file.write('<kml xmlns="http://earth.google.com/kml/2.0">' +'\n')
        file.write('<Document>' +'\n')
        for num in range(df.shape[0]):
            file.write('<Placemark>' +'\n')
            coordinate = "<Point><coordinates>"+str(df.iloc[num,0])+","+str(df.iloc[num,1])+",0</coordinates></Point>"#此处0代表海拔，如果有海拔，可更改
            file.write(coordinate +'\n')
            file.write('</Placemark>' +'\n')
        file.write('</Document>' +'\n')
        file.write('</kml>' +'\n')
#示例
#original_csvtokml('000dd3e8-d174-4f59-ae90-6d9863fe2ab9','H:\GPS_Data\Road_Network\BYCBridge\Trunks\KML','H:\GPS_Data\\20170901\Top20\Meshed\\000dd3e8-d174-4f59-ae90-6d9863fe2ab9.csv')
#original_csvtokml('0a17a227-9702-4723-9234-24d0626e3e02','H:\GPS_Data\Road_Network\BYQBridge\KML\TrunksAreakml','H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\0a17a227-9702-4723-9234-24d0626e3e02.csv')


#with open(r'H:\GPS_Data\Road_Network\BYQBridge\Trunks\BYC.txt','r') as file:
   # for line in file.readlines():
       #print(os.path.split(line.strip('\n'))[-1] )
       #name = os.path.splitext(os.path.split(line)[-1])[0]
       #original_csvtokml(name,'H:\GPS_Data\Road_Network\BYQBridge\Trunks\KML',line.strip('\n'))


"""
#批处理
savepath = "H:\GPS_Data\Road_Network\BYQBridge\KML\TrunksAreakml"
csvx_list = glob.glob('H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\*.csv')
csvfilenum = len(csvx_list)
with tqdm(total=csvfilenum) as pbar:
    for i in csvx_list:
        (tempath, tempfilename) = os.path.split(i)  # tempfilename为csv文件名（包含后缀）
        (filename, extension) = os.path.splitext(tempfilename)  # extension为文件后缀
        original_csvtokml(filename,savepath,i)
        pbar.update(1)
"""