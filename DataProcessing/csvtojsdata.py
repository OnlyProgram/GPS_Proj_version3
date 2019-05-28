# -*- coding: utf-8 -*-
# @Time    : 2019/5/10 13:59
# @Author  : WHS
# @File    : csvtojsdata.py
# @Software: PyCharm
"""
实现csv文件转换到可动态查看轨迹的js数据
"""
import pandas as pd
import os
from datetime import datetime
from DataProcessing import Transform
import time
#f09c3b4c-15b5-4a36-a154-0d1edf4b2f57
filename = "4e3dae9e-6dc6-4fe0-875d-dc29af45ab5b"
Meshrootpath = "H:\GPS_Data\\20170901\Top20\Meshed"
processfile = Meshrootpath + os.path.sep + filename + ".csv"
df = pd.read_csv(processfile, header=None,usecols=[1, 2, 3],low_memory=False)  #只读时间 经纬度 列
# runtime = datetime.strptime(str(df.iloc[0,0]), '%Y-%m-%d %H:%M:%S')
Cortrans = Transform.coordinate_trans()
#BDlon,BDlat = Cortrans.wgs84toBD09(df.iloc[0,1],df.iloc[0,2])
tem_lis = []
jspath = "H:\GPS_Data\web\\assets\data"
savejs =  jspath + os.path.sep + filename + "New.js"
file = open(savejs,'a')
file.write("var data = [\n")
for num in range(df.shape[0]):
    tem_dic = {}
    runtime = time.strptime(str(df.iloc[num, 0]), '%Y-%m-%d %H:%M:%S')
    Pointruntime = time.strftime("%Y/%m/%d %H:%M:%S", runtime)  # %H:%M:%S
    #BDlon, BDlat = Cortrans.wgs84toBD09(df.iloc[num,1],df.iloc[num,2])
    #tem_dic["date"] = Pointruntime
    #tem_dic["lng"] = BDlon
    #tem_dic["lat"] = BDlat
    tem_lis.append(tem_dic)
    if num == df.shape[0] - 1:
        #print(str(tem_lis[li]))
        file.write('{"date":"'+Pointruntime+'","lng":'+str(df.iloc[num,1])+', "lat":'+str(df.iloc[num,2])+'}\n')
    else:
        file.write('{"date": "'+Pointruntime+'","lng":'+str(df.iloc[num,1])+', "lat":'+str(df.iloc[num,2])+'},\n')
file.write("];")
"""
file.write("var data = [\n")
for li in range(len(tem_lis)):
    if li == len(tem_lis)-1:
        print(str(tem_lis[li]))
        file.write(str(tem_lis[li]) + "\n")
    else:
        file.write(str(tem_lis[li]) + ",\n")
file.write("];")
"""


#df.iloc[:,1] = pd.to_datetime(df.iloc[:, 1], format="%Y%m%d ", errors='coerce')