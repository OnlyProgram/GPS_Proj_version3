# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 19:56
# @Author  : WHS
# @File    : FillTrajectory.py
# @Software: PyCharm

import pandas as pd
import math
import os
from math import radians, cos, sin, asin, sqrt


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


"""
def findcsv(path):

    #:param path: 传入存储每辆车GPS记录数的文件夹
    #:return: 返回该文件夹下所有的csv文件（包含路径）

    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".csv"):
                ret.append(de_path)
    return ret
"""


def findcsvpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".csv"):
                ret.append(de_path)
    return ret
def findtxtpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".txt"):
                ret.append(de_path)
    return ret


def FilterRoute(filepath, minKilometer=0.5, maxKilometer=1, timechoose=1, Calculation=1):
    """
    筛选出缺失GPS坐标路段
    :param filepath: 传入待处理车辆的文件路径，注意：此处传入的是单辆车的GPS数据文件
    :param minKilometer: 距离阈值（单位公里，相邻坐标距离大于此阈值会被筛选出，默认为0.5公里）
    :param timechoose: 代表是否已按照时间排序，1(默认)代表已经排序完成，0代表未按时间排序
    :param Calculation: 代表距离计算方式，1（默认）代表按经纬度计算，0代表按照格子计算(可能存在问题，
    如在相邻格子计算是按照100米，但是实际中，可能会很小)，如果Kilometer设置大于0.1，可以用格子计算
    :param maxKilometer: 距离最大阈值，超过此阈值不会被筛选
    :return: 返回待补充的相邻点的经纬度坐标,所在格子XY编号
    """
    result = []  # 存储返回列表
    if (Calculation == 1):
        if (timechoose == 1):
            try:
                df = pd.read_csv(filepath, header=None, usecols=[1, 2, 3, 4, 5],names=[0,1,2,3,4])#,names=[0,1,2,3,4]
                if df.nunique()[1] < 5 or df.nunique()[2]< 5:
                    print("*********该车辆坐标点过少，暂不处理**********")
                    return 0
                df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format="%Y%m%d ", errors='coerce')
                for num in range(df.shape[0] - 1):
                    # print(df.iloc[num, 1], df.iloc[num, 2], df.iloc[num + 1, 1], df.iloc[num + 1, 2])
                    pointdistance = haversine(df.iloc[num, 1], df.iloc[num, 2], df.iloc[num + 1, 1],
                                              df.iloc[num + 1, 2])
                    #Time_difference = (df.iloc[num+1,0]-df.iloc[num,0]).total_seconds() #时间差
                    # if pointdistance/Time_difference >: # 速度（公里/s）大于多少，
                    # 删除这个点  距离瞬间增大超出客观事实
                    # pass
                    if minKilometer <= pointdistance <= maxKilometer:
                        tem = [[df.iloc[num, 1], df.iloc[num, 2], df.iloc[num + 1, 1], df.iloc[num + 1, 2]],
                               [df.iloc[num, 3], df.iloc[num, 4], df.iloc[num + 1, 3], df.iloc[num + 1, 4]]]
                        result.append(tem)
                return result
            except Exception as e:
                print(e)
        else:
            # df = pd.read_csv(filepath, header=None, usecols=[1, 4, 5])  # 只读取时间和所属网格
            print("原文件时间未排序")
    else:
        print("采用格子计算距离")


"""
思路：
1、首先找出通过这两个格子的所有车辆
2、然后筛选出在阈值之内的车辆
3、返回车辆列表
"""


def Similar_area(trunkpath, x_grid1, y_grid1, x_grid2, y_grid2, x1, y1, x2, y2, ranges=0.03):
    """
    找出与待补充路段两端相近区域
    :param trunkpath: 车辆csv文件路径
    :param x_grid1: 起始点X方向的格子编号
    :param y_grid1: 起始点Y方向的格子编号
    :param x_grid2: 终始点X方向的格子标记
    :param y_grid2: 终点Y方向的格子标记
    :param x1: 起点经度
    :param y1: 起点纬度
    :param x2: 终点经度
    :param y2: 终点纬度
    :param ranges: 默认值为0.03，即30米,距离小于此值的为相近区域,此时不能再通过格子计算距离，需要按照经纬度
    :return: 格式如下 {"车牌号":[[起始点坐标],[终点坐标]]}
    """
    flag = 0  # 标记是否先经过起始点
    Trunk_list = []  # 存储经过此路段的坐标
    Trunk_dict = {}
    # print(list_dir)
    Trunk_number = str(os.path.split(trunkpath)[-1]).split('.')[0]  # 车牌号

    try:
        df = pd.read_csv(trunkpath, header=None, usecols=[1,2, 3, 4, 5])  # 读经纬度 网格X，Y
        df.iloc[:,0] = pd.to_datetime(df.iloc[:, 0], format="%Y%m%d ", errors='coerce')
        start_row = 0
        end_row = 0
        for num in range(df.shape[0]):

            if not flag:  # 先找起始点
                if df.iloc[num, 3] == x_grid1 and df.iloc[num, 4] == y_grid1:  # 经过A点
                    if (haversine(x1, y1, df.iloc[num, 1], df.iloc[num, 2]) < ranges):  # 距离小于阈值
                        Trunk_list = [[df.iloc[num, 1], df.iloc[num, 2]]]
                        start_row = num
                        flag = 1
            elif flag:  # 找到起始点后再找终点
                if df.iloc[num, 3] == x_grid2 and df.iloc[num, 4] == y_grid2:
                    if (haversine(x2, y2, df.iloc[num, 1], df.iloc[num, 2]) < ranges):  # 距离小于阈值,经过终点
                        Time_difference = (df.iloc[num, 0] - df.iloc[start_row, 0]).total_seconds()  # 时间差
                        if(Time_difference <  1200):  #经过这个路段（0.5-1公里）超1200秒，则不算相似区域
                            end_row = num
                            # 此处加判断 ，保证经过起终点的坐标之间的坐标数有多少可以上，在选择，避免相似区域中此路段做标数目也过少，
                            if end_row - start_row > 0:
                                Trunk_list.append([df.iloc[num, 1], df.iloc[num, 2]])
                                Trunk_list.append([start_row, end_row])
                                Trunk_dict[Trunk_number] = Trunk_list
                                return Trunk_dict
                            else:
                                pass
                        else:pass
                    else:pass
                else:pass
            else:
                pass
        """
        数据已按照时间排序，先找到是否经过A，找到A后，判断该点是否经过B
        """

    except Exception as e:
        print(e)




def findSimilarArea(path, trunknumber, savepath, trunkcoordinate):
    """
    #找出相近区域
    :param path: 所有车所在文件夹路径
    :param trunknumber: 待补路段所属车牌号
    :param savepath:结果文件要保存的路径
    :param trunkcoordinate:待补路段坐标信息，起点终点经纬度，所属格，如：
    [[116.14683500000001, 40.091654999999996, 116.144581, 40.086686], [1147, 1092, 1145, 1087]]
    :return: 无返回 存储
    """
    flag = 0
    list_dir = findcsvpath(path)  # 获取当前文件夹下所有文件名
    EndResult = {}
    print("**********正在查找路段：{}的相似区域**********".format(trunkcoordinate))
    for file in list_dir:

        if str(os.path.split(file)[-1]).split('.')[0] == trunknumber:
            pass
        else:
            temresult = Similar_area(file, trunkcoordinate[1][0], trunkcoordinate[1][1], trunkcoordinate[1][2],
                                     trunkcoordinate[1][3],
                                     trunkcoordinate[0][0], trunkcoordinate[0][1], trunkcoordinate[0][2],
                                     trunkcoordinate[0][3])
            if temresult:
                flag = 1
                EndResult.update(temresult)
    if flag !=0:
        tem = trunknumber + "SimilarAreas.txt"
        with open(os.path.join(savepath, tem), 'a') as temfile:
            temfile.write("{}的相似区域为:".format(str(trunkcoordinate)))
            temfile.write(str(EndResult) + "\n\n")
        print("**********路段：{}的相似区域查找完成，已保存至{}文件夹下**********".format(trunkcoordinate, savepath))
    else:
        print("**********未找到相似区域**********")

# 无相似路段补充策略
def FillNoSimilarRoute():
    pass
#单个车辆补充
def FillTracks(Trunkpath, SingleTrunkTxt,savepath,savename,choose=1,maxpoints = 0):
    """

    :param Trunkpath: 比较路径，即单个车辆网格化后的路径
    :param SingleTrunkTxt: 相似区域文件路径
    :param savepath: 文件保存路径
    :param savename: 保存的文件名
    :param startend:起点终点坐标
    :param choose:补点策略，1表示车辆补点，0表示路网补点
    :param maxpoints 表示在迭代补点中，待补路段至少要获得的补点数，即如果所有的相似区域中的最大坐标数仍小于maxpoints,则要迭代补点
    :return:
    """
    if choose == 1:
        AllFilledpoint = pd.DataFrame(None)  # 一辆车的所有补点
        with open(SingleTrunkTxt,'r') as file:
            for line in file.readlines():  # 一行为一个路段，即此循环为补一个车辆

                if line.strip():
                    tem_list = line.strip('\n').split("的相似区域为:")
                    startend = eval(tem_list[0])[0]  # 首先转换为列表，再取出起点终点坐标
                    dic = eval(tem_list[1])
                    if dic:
                        RoutePoint = pd.DataFrame(None)  # 路段的所有补点
                        order_key_dic ={}
                        for key in dic.keys():  # 此循环为补充一个路段
                            order_key_dic[key] =  dic[key][2][1] - dic[key][2][0] + 1   #被选中的相似区域坐标数
                        order_key_dic = dict(sorted(order_key_dic.items(), key=lambda x: x[1],reverse=True)) #降序
                        #print(order_key_dic)
                        # 开始迭代补点
                        totalFillPoints = 0
                        for seckey in order_key_dic.keys():
                            totalFillPoints += order_key_dic[seckey]
                            tem_num = seckey
                            #print(dic[tem_num][2][0], dic[tem_num][2][1])
                            # # 补点数目大于设置阈值
                            csvfile = tem_num + ".csv"
                            singleTrunkpath = os.path.join(Trunkpath, csvfile)  # 打开补点文件
                            df = pd.read_csv(singleTrunkpath, header=None, usecols=[2, 3], names=[0, 1])  # 读经纬度
                            df = df.iloc[dic[tem_num][2][0]:dic[tem_num][2][1] + 1, :]  # 一个路段的补点
                            RoutePoint = pd.concat([RoutePoint,df],ignore_index = True)
                            if totalFillPoints >= maxpoints:
                                break
                            else:pass
                        #print(RoutePoint)
                        RoutePoint = RoutePoint.reset_index(drop=True)  # 重置索引,并删除之前的索引
                        RoutePoint[2] = 2  # 标记  2 表示补充点
                        RoutePoint.loc[RoutePoint.shape[0]] = [startend[0], startend[1], 1]  # 加入路段起始坐标  标记为1 代表起点终点坐标
                        RoutePoint.loc[RoutePoint.shape[0]] = [startend[2], startend[3], 1]
                        #print(RoutePoint)
                        AllFilledpoint = pd.concat([AllFilledpoint, RoutePoint], ignore_index=True)
                    else:
                        pass
            Fullname = savename + ".csv"
            AllFilledpoint.to_csv(os.path.join(savepath, Fullname), header=0, index=0)
    elif choose == 0:
        pass
    else:
        print("补点策略函数参数错误，只能传入0或1,请重新选择")
"""
#示例
#补点示例，将原始文件与补点文件合并
Trunkpath = 'H:\GPS_Data\\20170901\Top20\Meshed'
FilledSavePath = 'H:\GPS_Data\\20170901\Top20\FilledRoute'
SaveFilename = 'text'
Filledtxt= 'H:\GPS_Data\\20170901\Top20\SimilarArea\old\\036f3c48-fed9-4acc-80ac-61fbad58b1c2SimilarAreasttrxt.txt'
FilledPoints = FillTracks(Trunkpath,Filledtxt,FilledSavePath,SaveFilename)  #补点csv文件
Filledcsvname = str(os.path.split(Filledtxt)[-1]).split('SimilarAreas')[0] +".csv" #提出被补车辆的车牌号
df = pd.read_csv(os.path.join(Trunkpath,Filledcsvname),header=None,usecols=[2,3],names=[0, 1])  #此处names不能缺少，切记！！！！！
df = df.reset_index(drop=True)
df[2] = 0   #标记为原始点
df = pd.concat([df,FilledPoints],ignore_index=True)
#df.to_csv(os.path.join('H:\GPS_Data\\20170901\Top20\AllFilled',Filledcsvname),index=0,header=0)
"""

def FindAllRoute(AllTrunkPath, savePAth):
    """
    找出所有车辆的待补路段，需要传网格化后的数据
    :param AllTrunkPath:  所有单独车辆数据所在的文件夹
    :param savePAth: 结果保存路径
    :return: 无返回
    """
    list_dir = findcsvpath(AllTrunkPath)
    NoFind = []  # 记录未查找待补路段的车牌号
    for file in list_dir:
        print("**********正在查找车辆：{}的待补路段**********".format(str(os.path.split(file)[-1]).split('.')[0]))
        Filledresult = FilterRoute(file)  # 接受对应车辆的结果

        if Filledresult == 0:
            NoFind.append(str(os.path.split(file)[-1]).split('.')[0])
        elif Filledresult:
            finame = str(os.path.split(file)[-1]).split('.')[0] + ".txt"
            filpa = "H:\GPS_Data\\20170901\Top20\Top20Meshed" #
            savep = "H:\GPS_Data\\20170901\Top20\SimilarArea"  #相似区域文件保存路径

            with open(os.path.join(savePAth, finame), 'w') as f:
                for num in Filledresult:
                    string = str(num[0][0])+','+str(num[0][1])+','+str(num[0][2])+','+str(num[0][3])+','+\
                             str(num[1][0])+','+str(num[1][1])+','+str(num[1][2])+','+str(num[1][3])
                    f.write(string +"\n")
            print("**********车牌号为{}的车辆轨迹待补路段查找完成**********".format(str(os.path.split(file)[-1]).split('.')[0]))

        else:
            print("**********车辆：{}的没有待补路段**********".format(str(os.path.split(file)[-1]).split('.')[0]))
    if NoFind:
        print("坐标点过少，未查找待补路段的车辆为：{}".format(NoFind))
    else:pass


"""
#寻找待补路段示例：
FindAllRoute('H:\GPS_Data\\20170901\Top20\Meshed',
             'H:\GPS_Data\\20170901\Top20\Trajectory')
"""
"""
#找出相近区域
filpa = "H:\GPS_Data\\20170901\Top20\Meshed"
savep = "H:\GPS_Data\\20170901\Top20\SimilarArea"
#num = "4b3142ee-5d31-416c-9653-fc3368e24055"
paths = findtxtpath(r'H:\GPS_Data\20170901\Top20\\text')
for pa in paths:
    #print(str(os.path.split(pa)[-1]).split('.')[0])
    if str(os.path.split(pa)[-1]).split('.')[0]=="4e3dae9e-6dc6-4fe0-875d-dc29af45ab5b":
        print("正在处理车辆：{}".format(str(os.path.split(pa)[-1]).split('.')[0]))
        with open(pa, 'r') as file:
            for line in file.readlines():
                line_list = []
                list1 = [eval(i) for i in line.strip('\n').split(',')]  # str转换为int
                line_list.append(list1[0:4])
                line_list.append(list1[4:])

                findSimilarArea(filpa, str(os.path.split(pa)[-1]).split('.')[0], savep, line_list)

"""



"""
#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
dic = {'22312ebe-16e1-49b2-91a3-b4677c3eb0dd': [[116.51049499999999, 39.671583], [116.50081499999999, 39.6759], [5017, 12587]],
       '3d9c80d6-7b09-4969-8a81-54cfc96995e7': [[116.51036599999999, 39.671551], [116.500735, 39.675863], [153, 430]],
        '49782d17-207e-4a90-a054-342e6f7cccd2': [[116.510566, 39.6716], [116.500831, 39.675763], [4594, 11875]]
       }
FillTrack("H:\GPS_Data\\20170901\Top20\Top20Meshed",dic,'H:\GPS_Data\\20170901\Top20\FilledRoute','19e74af4-7d9d-43ef-8c28-83ca01f527e3Filled')

"""