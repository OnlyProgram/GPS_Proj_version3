"""
涉及到时间排序，异常值处理，和网格化
"""
import pandas as pd
import datetime
import math
import os

def findcsv(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".csv"):
                ret.append(de_path)
    return ret


# 处理异常时间，筛选出符合时间段的GPS数据，并根据时间排序
def gps_processing(FilePath,starttime,endtime):
    df = pd.read_csv(FilePath, header=None,  usecols=[0, 1, 2, 3])
    df.iloc[:,1] = pd.to_datetime(df.iloc[:, 1], format="%Y%m%d ", errors='coerce')
    start = datetime.datetime.strptime(starttime,'%Y-%m-%d')
    end = datetime.datetime.strptime(endtime,'%Y-%m-%d')
    df = df.dropna(axis=0, how='any')  # 删除表中含有任何NaN的行 ,subset=[1]可添加 只关注时间这一列，不添加也会处理其他列为空的行
    df = (df[(df.iloc[:,1]>=start)&(df.iloc[:,1]<=end)])  #筛选某个是时间段
    #Sort_Index = df.sort_values(by=1).index
    df = df.sort_values(by=1)
    df.to_csv(r"Processed.csv",index=0,header=0)
    return df



"""
数据网格化，单元格单位近似100米（0.001）
单元格编号规则（1,1）代表第一行（从下往上），第一列（从左至右）
读取csv文件时，会报（sys:1: DtypeWarning: Columns (0,1) have mixed types. Specify dtype option on import or set low_memory=False.）
警告，这里设置low_memory = false ，如果读取数据过大，此方法可能到时内存溢出，今后了解后改进
"""
def Meshing(filepath,savepath,filename):
    df = pd.read_csv(filepath, header=None,
                     usecols=[0, 1, 2, 3],low_memory=False)
    df.iloc[:,1] = pd.to_datetime(df.iloc[:, 1], format="%Y%m%d ", errors='coerce')
    start = datetime.datetime.strptime("2000-01-01", '%Y-%m-%d')
    end = datetime.datetime.strptime("2099-12-31", '%Y-%m-%d')
    df = df.dropna(axis=0, how='any')  # 删除表中含有任何NaN的行 ,subset=[1]可添加 只关注时间这一列，不添加也会处理其他列为空的行
    df = (df[(df.iloc[:, 1] >= start) & (df.iloc[:, 1] <= end)])  # 筛选某个是时间段
    df = df[(df.iloc[:, 2] < 118) & (df.iloc[:, 2] > 115) & (df.iloc[:, 3] < 42) & (df.iloc[:, 3] > 39)]  # 去除北京外GPS坐标
    df = df.sort_values(by=1)  #时间排序
    row =0
    df[4] = None  #添加列
    df[5] = None
    for num in df.iloc[:, 0]:
        x_grid = math.ceil((df.iloc[row,2]-115)/0.001)  #x方向格子编号
        y_grid = math.ceil((df.iloc[row,3]-39)/0.001)   #y方向格子编号
        df.iloc[row, 4] = str(x_grid)
        df.iloc[row,5] = str(y_grid)
        row += 1
    filenames = filename + ".csv"
    resultpath = os.path.join(savepath,filenames)
    df.to_csv(resultpath,index=0,header=0)
    print("**********网格化完成**********")
"""
#使用举例：
path ="H:\GPS_Data\\20170901\Top20\Top20Trunk/0dd1b47d-f845-48d6-b5bb-105d9160cf54.csv"
spath = "H:\GPS_Data\\20170901\Top20\Top20Meshed"
name = "0dd1b47d-f845-48d6-b5bb-105d9160cf54"
Meshing(path,spath,name)
"""
#同时网格化多个车辆
list_dir = findcsv('H:\GPS_Data\\20170901\Top20\Top20Trunk')
#spath = "D:\postgraduate-2017-2020\Data_set\GPS\Top200w\Data_gridding" #文件保存路径
for file in list_dir:
    temname = (str(os.path.split(file)[-1]).split('.')[0])
    #Meshing(file,spath,temname)



