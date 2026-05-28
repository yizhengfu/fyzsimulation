# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 19:44:44 2022

@author: 阿磊很努力
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pylab
import matplotlib.ticker as plticker
from matplotlib.pyplot import MultipleLocator
import xlrd
from matplotlib.lines import Line2D
import math
from scipy import optimize       #一个或多个变量的标量函数的最小化

plt.style.use('science')
def f_1(x, A, B):
    return A * x + B

def setup(ax,x_label,y_label):
   
    '''

    spines:边框线设置
    tick:刻度线设置
    label:刻度线标签
    xticklabel:x刻度线上的标签
    yticklabel:y刻度线上的标签
    title:图片标头
    marker:点样式
    markersize：点大小
    markevery:每几个点绘制一个点
    markeredgewidth:点边缘线宽
    markeredgecolor:点边缘颜色，默认与线同色
    markerfacecolor:点填充颜色，默认与线同色
    capthick:误差棒边界横杠高度
    capsize:误差棒边界横杠的长度
    ecolor: 误差棒图的线条颜色
    elinewidth: 误差棒的线条粗细
    
    '''
   

    # 边框线的线宽设置
   
    font1 = {'family': 'Times New Roman',
             'weight': 'bold',
             'size': 18,
             }
    font2 = {'family': 'Times New Roman',
             'weight': 'normal',
             'size': 11,
             }
    
    width = 1.5   
    ax.spines['top'].set_linewidth(width)       #设置上边框线粗1.5   
    ax.spines['bottom'].set_linewidth(width)    #设置下边框线粗1.5  
    ax.spines['left'].set_linewidth(width)      #设置左边框线粗1.5  
    ax.spines['right'].set_linewidth(width)     #设置右边框线粗1.5  
    # 边框上的刻度的出现
    ax.tick_params(top='on', bottom='on', left='on', right='on', direction='in')  #四个边框线都设有刻度，方向朝内
    # 边框上的ticks对应的lable,即数字的尺寸
    ax.tick_params(labelsize=20,pad=6)                       # 标签间距为20,刻度与标签间距离为6
    #ax.yaxis.set_ticks_position('right')
    ax.tick_params(which='major', width=1.50, length=6)      #主刻度线设置
    ax.tick_params(which='minor', width=0.75, length=0)      #副刻度线设置
    # 边框上的ticks的出现的间隔
    locx = plticker.MultipleLocator(base=1)                 # X间距1
    ax.xaxis.set_major_locator(locx)
    locy = plticker.MultipleLocator(base=0.2)                  # Y间距0.2
    ax.yaxis.set_major_locator(locy)
    # 边框上的注释labels
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    [label.set_fontname('Times New Roman') for label in labels]
    # 边框上的注释labels距离坐标轴的距离
    xAxisLable = x_label 
    yAxisLable = y_label
    ax.set_xlabel(xAxisLable, font1, labelpad=5)             #font1 是额外的设置
    ax.set_ylabel(yAxisLable, font1, labelpad=5)

    
# ----------------------------------------------------------------------#
# 读取excel
excel_path = r"Ar_viscosity_MP.xlsx"                                      #读取excel文件的地址,如果路径或者文件名有中文给前面加一个r拜师原生字符
work_sheet = xlrd.open_workbook(excel_path);  
# sheet的数量
sheet_num = work_sheet.nsheets;
# 获取sheet name
sheet_name = []
for sheet in work_sheet.sheets():
    sheet_name.append(sheet.name)

# 选取sheet；读取哪个工作表
now_sheet = work_sheet.sheets()[0]  #第一个表
# sheet的行
row = now_sheet.nrows                                   # 获得sheet的行数
# sheet的列
ncol = now_sheet.ncols                                  # 获得sheet的列数



N    =    now_sheet.col_values(0)                
N_matrix = list(filter(None, N[1:]))             #第一列除了第一行所有的内容

vx = now_sheet.col_values(1)

vx_matrix =  list(filter(None, vx[1:]))


#----------------------------------------------------------------------#    
fig, axe = plt.subplots(1, 1, figsize=(8,5))            #设置子图，子图1*1个，大小为5*5

markersize = 8                                          #设置数据点标记的大小
linewidth = 2
markevery =1
alpha =0.9
p_1 = dict(marker='o',color = 'b',linestyle = '--',markevery=markevery,markerfacecolor='none',markersize=markersize,linewidth=linewidth,alpha=alpha)   
p_11 = dict(color = 'b',linestyle = '--',linewidth=linewidth,alpha=alpha)



axe.plot(N_matrix, vx_matrix,**p_1,label='Velocity in X direction')


axe.set_ylim(-0.5, 0.5)
axe.set_xlim(-0.5, 20.5)
setup(axe,r'$\rm Nbins $',r'Velocity')
axe.legend(loc='best', frameon=False, \
              labelspacing=0.3,fontsize='x-large')
#axe.legend(bbox_to_anchor=(1.10, 1), \
              #loc='upper left', borderaxespad=0,fontsize='xx-large')




