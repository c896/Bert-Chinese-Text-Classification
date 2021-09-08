import os
# import jieba
# import jieba.analyse as analyse
from sklearn.utils import shuffle
# import re
from tqdm import tqdm #,trange
# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
# import xlwt,xlrd
from xlutils.copy import copy
from sklearn.model_selection import train_test_split
from rewrite import Rewrite_excel

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif']='SimHei'
plt.rcParams['axes.unicode_minus']=False

class Excel_process(object):

    # excel = xlwt.Workbook(encoding = 'utf-8')
    #---------------------------------------读取xlsx文件----------------------------------------#
    # path_txt = 'train.txt'
    # news_path = '训练数据样本.xlsx'  #合并
    def __init__(self,max_num=12000):
        # self.textinput = textinput
        self.max_num = max_num
        self.classdict = {'财经':0,'股票':0,'房产':1,'教育':2,'科普': 2,'科技':3,'数码': 3,'军事':4,'汽车':5,'体育':6,'足球': 6,'综合体育最新':6,\
                    '体育焦点':6,'游戏':7,'娱乐':8,'其它':9,'其他':9,'社会':9,'健康':9,'法制':9,'世界':9,'国际':9,'文化':9,'历史':9,'时尚':9,'情感':9,\
                        '旅游':9,'健康':9,'美食':9,'宠物':9,'星座':9,'动漫':9} 
        self.iddict={0:'财经',1:'房产',2:'教育',3:'科技',4:'军事',5:'汽车',6:'体育',7:'游戏',8:'娱乐',9:'其他'}

    def read_excel(self,path):
        data_xls = pd.ExcelFile(path)
        df =pd.read_excel(path,sheet_name=0,usecols=[0,1,2])
        print('当前所有分类{}'.format(data_xls.sheet_names))
        print('开始读取数据。。。')
        for idx in tqdm(range(1,len(data_xls.sheet_names))):
            # print(idx)
            df_ =pd.read_excel(path,sheet_name=idx,usecols=[0,1,2])
            df_=df_.drop(index=0)
            df = pd.concat([df, df_], axis=0)
        return df

    def reclass(self,ori_path_list,save_path):
        classdict=self.classdict
        iddict = self.iddict
        max_num = self.max_num
        df = self.read_excel(ori_path_list[0])
        if len(ori_path_list)>1:
            for ori_path in ori_path_list[1:]:
                df_ = self.read_excel(ori_path)
                df_ = df_.drop(index=0)
                df = pd.concat([df, df_], axis=0)
        # plt.ion()
        df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        plt.title('原始分布')
        plt.show()
        # plt.ioff()
        # plt.close()
        # plt.pause(6)# 间隔的秒数：6s
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #-------------------------------------------去重 -----------------------------------------------#
        df.drop_duplicates(subset='title', keep='first', inplace=True)
        # df=df.drop(index=(df.loc[(df[0]=='content')].index))
        print(df.shape)

        df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        plt.title('去重后')
        plt.show()
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #--------------------------------------重新划分分类--------------------------------------------------#
        #世界国际历史有歧义
        df.index = range(len(df)) #index重排

        # iddict[7]
        idx=0
        for content in df.values:    
            if classdict[content[1]]==6:
                # df.iloc[idx]['channelName'] = iddict[6] #
                df.loc[idx,'channelName'] = iddict[6]
                # print(idx)
                # print(iddict[6])
            elif classdict[content[1]]==0:
                df.loc[idx,'channelName'] = iddict[0]
            elif classdict[content[1]]==2:
                df.loc[idx,'channelName'] = iddict[2]
            elif classdict[content[1]]==3:
                df.loc[idx,'channelName'] = iddict[3]  
            elif classdict[content[1]]==9:
                df.loc[idx,'channelName'] = iddict[9]   
            idx += 1

        df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        plt.title('重新划分分类后')
        plt.show()
        # plt.draw()
        # # plt.pause(2)  #显示秒数
        # plt.close()
        #-------------------------------------重写-----------------------------------------------------#
        # save_path = r'./dataprocess/合并重新划分.xlsx'
        Rewrite_excel(df,save_path).write_excel(max_num) #每个分类最大1500

    def data_split(self,path):
        max_num = self.max_num
        #-------------------------------------划分数据集---------------------------------------------------#
        df = self.read_excel(path) #r'./dataprocess/合并重新划分.xlsx'
        df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        plt.title('数据分布')
        plt.show()
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #-------------------------------------打乱顺序----------------------------------------------------#
        df = shuffle(df) #打乱顺序
        df_train,df_test = train_test_split(df,test_size = 0.1)
        df_train,df_eval= train_test_split(df_train,test_size = 0.12)

        #-------------------------------------重写-----------------------------------------------------#
        # path1 = r'./dataprocess/output/new_train.xlsx'
        # path2 = r'./dataprocess/output/new_test.xlsx'
        # path3 = r'./dataprocess/output/new_eval.xlsx'
        output_dir ='./dataprocess/data/' 
        if path.endswith('.xlsx'):
            # output_dir = path.split('.xlsx')[0] + '/output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            path1=output_dir+'/train.xlsx'
            path2=output_dir+'/test.xlsx'
            path3=output_dir+'/dev.xlsx'

        elif path.endswith('.xls'):
            # output_dir = path.split('.xls')[0] + '/output'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            path1=output_dir+'/train.xls'
            path2=output_dir+'/test.xls'
            path3=output_dir+'/dev.xls'

        Rewrite_excel(df_train,path1).write_excel(max_num) #每个分类最大1500
        Rewrite_excel(df_test,path2).write_excel(max_num)
        Rewrite_excel(df_eval,path3).write_excel(max_num)
        print("重写完毕")


#-------------------------------------去重并重新划分数据集分类---------------------------------------------------#
# path_list=[
#     './dataprocess/data/杨贺超/1.xlsx',
#     './dataprocess/data/杨贺超/2.xlsx',
#     './dataprocess/data/杨贺超/3.xlsx',
#     './dataprocess/data/杨贺超/4.xlsx',
#     './dataprocess/data/杨贺超/5.xlsx',
#     './dataprocess/data/杨贺超/6.xlsx',
#     './dataprocess/data/杨贺超/7.xlsx',
#     './dataprocess/data/杨贺超/8.xlsx',
#     './dataprocess/data/杨贺超/9.xlsx',
#     './dataprocess/data/杨贺超/10.xlsx',
#     './dataprocess/data/杨贺超/qq_new (1).xlsx',
#     './dataprocess/data/杨贺超/qq_new (2).xlsx',
#     './dataprocess/data/杨贺超/qq_new (3).xlsx',
#     './dataprocess/data/杨贺超/qq_new (4).xlsx',
#     './dataprocess/data/杨贺超/qq_new (5).xlsx',
#     './dataprocess/data/杨贺超/qq_new (6).xlsx',
#     './dataprocess/data/杨贺超/qq_new (7).xlsx',
#     './dataprocess/data/杨贺超/qq_new (8).xlsx',
#     './dataprocess/data/杨贺超/qq_new (9).xlsx',
#     './dataprocess/data/杨贺超/qq_new (10).xlsx',
#     './dataprocess/data/杨贺超/qq_new (11).xlsx',
#     './dataprocess/data/杨贺超/qq_new (12).xlsx',
#     './dataprocess/data/杨贺超/qq_new (13).xlsx',
#     './dataprocess/data/杨贺超/qq_new (14).xlsx',
#     './dataprocess/data/杨贺超/qq_new (15).xlsx',
#     './dataprocess/data/杨贺超/qq_new (16).xlsx',
#     './dataprocess/data/杨贺超/qq_new (17).xlsx',
#     './dataprocess/data/杨贺超/qq_new (18).xlsx',
#     './dataprocess/data/杨贺超/qq_new (19).xlsx',
#     './dataprocess/data/杨贺超/qq_new (20).xlsx',
#     './dataprocess/data/杨贺超/qq_new (21).xlsx',
#     './dataprocess/data/杨贺超/qq_new (22).xlsx',
#     './dataprocess/data/杨贺超/qq_new (23).xlsx',
#     './dataprocess/data/杨贺超/qq_new (24).xlsx',
#     './dataprocess/data/杨贺超/qq_new (25).xlsx',
#     './dataprocess/data/杨贺超/qq_new (26).xlsx',]
# save_path = './dataprocess/data/杨贺超合并.xlsx'

# path_list=[    
#     './dataprocess/data/杨贺超合并.xlsx',
#     './dataprocess/data/7.6/合并-未划分.xlsx',
#     './dataprocess/data/7.8/qq_new7.9.xlsx',
#     './dataprocess/data/7.11/qq_new (1).xls',
#     './dataprocess/data/7.11/qq_new (2).xls',
#     './dataprocess/data/7.11/qq_new (3).xls',
#     './dataprocess/data/7.14/qq_new (1).xlsx',
#     './dataprocess/data/7.14/qq_new (2).xlsx',
#     './dataprocess/data/7.14/qq_new (3).xlsx',
#     './dataprocess/data/7.14/qq_new (4).xlsx',
#     './dataprocess/data/7.15/qq_new1.xlsx',
#     './dataprocess/data/7.15/qq_new2.xls',] 

# save_path = './dataprocess/data/合并7.15all.xlsx'
# Excel_process(30000).reclass(path_list,save_path)
# print("重新划分完毕")

#-------------------------------------去重并重新划分数据集分类---------------------------------------------------#
# path_list=['./dataprocess/data/合并7.15all.xlsx'] 

# save_path = './dataprocess/data/合并7.15.xlsx'
# Excel_process(3200).reclass(path_list,save_path) #每个分类最大3200
# print("重新划分完毕")

#-------------------------------------划分训练测试和验证集---------------------------------------------------#
save_path = './dataprocess/data/合并7.15.xlsx'
Excel_process(3200).data_split(save_path) #每个分类最大3200
