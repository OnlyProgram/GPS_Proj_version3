# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 12:20
# @Author  : WHS
# @FileName: CombineCsvFile.py
# @Software: PyCharm
# @Python Version：3.6.0
"""
合并多个文件夹下的同名csv文件
"""
import os
import json
import pandas as pd
def Get_top_trunk_list():
    Trunk_list = []
    with open(r"D:\postgraduate-2017-2020\Data_set\GPS\top100w.json", 'r') as file:
        strs = file.read()
        Trunk_dict = json.loads(strs)
    for key in Trunk_dict.keys():
        Trunk_list.append(key)
    return Trunk_list
def findcsv(path):
    """
    :param path: 传入存储每辆车GPS记录数的文件路径
    :return: 返回该文件夹下所有的csv文件（包含路径）
    """
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        if filename.endswith(".csv"):
            ret.append(filename)
    return ret
def combinecsvfile(path,filename,savepath):
    combinecsv = pd.DataFrame()
    print(path)
    for file in path: #遍历文件列表
        df = pd.read_csv(file,header=None)
        combinecsv=combinecsv.append(df,ignore_index=True)
    combinecsv.to_csv(os.path.join(savepath,filename),index=0,header=0)
def Combine_file(pathlsits,savepath):
    """
    :param pathlsits:  待合并文件夹（下的csv文件）的所有路径
    :param savepath: 合并后文件的保存路径
    :return:  无返回
    """
    filelists = Get_top_trunk_list() #存储排名前。。的车牌
    total_file_lists = []  #存储所有文件夹下的csv文件
    for path in pathlsits:
        single_file_lists = findcsv(path)
        total_file_lists.append(single_file_lists)
    #开始合并
    for file in filelists:                 #遍历要合并的文件名列表
        conbinepath = []
        count = 0  # 记录遍历到第几个文件夹
        print(file)
        for single in total_file_lists:   #遍历分割后的文件夹
            flag = 0                      #标记是否在该文件夹下有同名文件

            for singlefile in single:     #遍历文件夹下的csv文件
                if file == singlefile.split(".")[0]:    #在该文件夹下找出同名文件
                    conbinefile = singlefile
                    flag = 1
                    break

            if flag == 1:
                conbinepath.append(os.path.join(pathlsits[count], conbinefile))
            count += 1
        if conbinepath:
            filename = file+".csv"
            combinecsvfile(conbinepath,filename,savepath)
        else:pass
    print("文件合并完毕！")


folder_lists = ['D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\part1','D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\part2',
                'D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\part3','D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\part4',
                'D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\part5']
savep = "D:\postgraduate-2017-2020\Data_set\GPS\\top1000000\Combine"
Combine_file(folder_lists,savep)
