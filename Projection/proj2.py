# -*- coding: utf-8 -*-
# @Time    : 2019/4/25 9:03
# @Author  : WHS
# @File    : proj2.py
# @Software: PyCharm
"""
此分部投点为原始csv文件投影，即不包含补点
"""
# -*- coding: utf-8 -*-
# @Time    : 2019/4/25 9:03
# @Author  : WHS
# @File    : proj2.py
# @Software: PyCharm
"""
此分部投点为原始csv文件投影，即不包含补点
"""
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
df = pd.read_csv(r'H:\\GPS_Data\\20170901\\Top20\\Top20Trunk\\ed78a56c-e0d2-4af6-b73b-f57848f82f61.csv',\
	usecols=[1,2,3],names=['time','lng','lat'])


df = df[(df.iloc[:, 1] < 118) & (df.iloc[:, 1] > 115) & (df.iloc[:, 2] < 42) & (df.iloc[:,2] > 39)]  #去除北京外GPS坐标#去除北京外GPS坐标


sns.set(style="whitegrid")
#df['lng'] = df['lng'].map(lambda x: (x-116)*85)
#df['lat'] = df['lat'].map(lambda x: (x-40)*110)
#plt.xlim(-20,100)
#plt.ylim(-80,60)
#plt.xticks(np.linspace(-20,100,100,endpoint=True))
#plt.yticks(np.linspace(-80,60,100,endpoint=True))
#sns.scatterplot(df.iloc[:,1],df.iloc[:,2],data=df,marker='.',color='b')
for i in range(df.shape[0]):
	plt.scatter(df.iloc[i,1],df.iloc[i,2],color='black',marker='.')

plt.show()

