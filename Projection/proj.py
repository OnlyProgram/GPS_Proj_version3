# -*- coding: utf-8 -*-
# @Time    : 2019/4/24 15:03
# @Author  : WHS
# @File    : proj.py
# @Software: PyCharm
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
#file = open(r'H:\GPS_Data\20170901\Top20\FilledRoute\4b3142ee-5d31-416c-9653-fc3368e24055.txt','r')

df = pd.read_csv(r'H:\GPS_Data\20170901\Top20\AllFilled\036f3c48-fed9-4acc-80ac-61fbad58b1c2Filled.csv',names=['lon','lat','Flag'])
#df = pd.read_csv(r'H:\GPS_Data\20170901\Top20\AllFilled\\Notime\4b3142ee-5d31-416c-9653-fc3368e24055.csv',names=['lon','lat','Flag'])
"""
fig = plt.figure()
axes = fig.add_subplot(111)

for line in range(df.shape[0]):
    if(df.iloc[line,2]==0):
        axes.scatter(df.iloc[line,0], df.iloc[line,1], color='black',marker='.')
    if (df.iloc[line,2]== 2):
        axes.scatter(df.iloc[line,0], df.iloc[line,1], color='blue',marker='.')
    if (df.iloc[line,2] == 1):
        axes.scatter(df.iloc[line,0], df.iloc[line,1], color='red', marker='.')
#plt.xlim(115,118)
#plt.ylim(39,42)
#plt.xticks(np.linspace(115,118,10))
#plt.yticks(np.linspace(39,42,10))
"""
plt.grid(True)
plt.xlabel('lon')
plt.ylabel('lat')
plt.title('Road')
#color_map = dict(zip(df.Flag.unique(),['black','red','blue']))
color_map = dict(zip(df.Flag.unique(),['yellow','red','blue','black']))
for species, group in df.groupby('Flag'):
    plt.scatter(group['lon'], group['lat'],
               color=color_map[species],
               label=species,marker='.')
#sns.scatterplot('lon','lat',data=df,hue='Flag',marker='.',)
plt.show()
