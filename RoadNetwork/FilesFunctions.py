# -*- coding: utf-8 -*-
# @Time    : 2019/5/28 15:56
# @Author  : WHS
# @File    : FilesFunctions.py
# @Software: PyCharm
"""
本部分实现与文件操作相关的函数
"""
import os
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
def SaveCandidateRoute(savapath,filename,dic:dict):
    """
    保存轨迹点候选路段，每辆车保存为一个txt文件
    :param savapath:保存路径
    :param filename: 保存的文件名
    :param dic: 轨迹点候选路段字典
    :return:
    """
    pass

