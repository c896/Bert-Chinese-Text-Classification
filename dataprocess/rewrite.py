import os
# import jieba
# import jieba.analyse as analyse
# from sklearn.utils import shuffle
# import re
from tqdm import tqdm #, trange
# import numpy as np
import pandas as pd
import xlwt,xlrd
from xlutils.copy import copy
import time

class Rewrite_excel(object):
    def __init__(self,df,path):
        self.df = df
        self.path =path
        self.newclass = {'财经':1,'房产':2,'教育':3,'科技':4,'军事':5,'汽车':6,'体育':7,'游戏':8,'娱乐':9,'其他':10,'其它':10}

    def chose_sheet(self,excel,temp,flag):  #,sheetnum
        newclass = self.newclass
        path = self.path
        # global worksheet
        if flag == 0:#不存在该文件
            worksheet_ = excel.add_sheet(temp)  
            worksheet_.write(0, 0, label='content')
            worksheet_.write(0, 1, label='channelName')
            worksheet_.write(0, 2, label='title')
            nrows = 1
        else: #若存在该文件
            readbook = xlrd.open_workbook(path)
            excel = copy(readbook)
            # if newclass[temp] == sheetnum+1:           
            try:
                # sheet = readbook.sheet_by_index(1)#索引的方式，从0开始
                sheet = readbook.sheet_by_name(temp)#名字的方式
                nrows = sheet.nrows#行 # ncols = sheet.ncols#列           
                worksheet_=excel.get_sheet(temp)#获得当前sheet
            except:#若不存在该sheet 则add
                worksheet_ = excel.add_sheet(temp)  
                worksheet_.write(0, 0, label='content')
                worksheet_.write(0, 1, label='channelName')
                worksheet_.write(0, 2, label='title')
                nrows = 1                
            #     pass
                # worksheet_ = excel.add_sheet(temp)
                # worksheet_.write(0, 0, label='content')
                # worksheet_.write(0, 1, label='channelName')
                # worksheet_.write(0, 2, label='title')
                # nrows = 1  
        return excel,worksheet_,nrows

    def write_excel(self,max_num):
        df = self.df
        path = self.path
        # classdict = {'财经':0,'股票':0,'房产':1,'教育':2,'科技':3,'数码': 3,'科普': 3,'军事':4,'汽车':5,'体育':6,'足球': 6,'综合体育最新':6,\
        #     '体育焦点':6,'游戏':7,'娱乐':8,'其它':9,'其他':9,'社会':9,'健康':9,'法制':9,'世界':9,'国际':9,'文化':9,'历史':9,'时尚':9,'情感':9,\
        #         '旅游':9,'健康':9,'美食':9,'宠物':9,'星座':9,'动漫':9} 
        newclass = {'财经':0,'房产':1,'教育':2,'科技':3,'军事':4,'汽车':5,'体育':6,'游戏':7,'娱乐':8,'其他':9,'其它':9}
        classinformation = df['channelName'].unique()
        print('划分后所有分类{}'.format(classinformation))
        for temp_class in classinformation:
            # temp_data = df[df['channelName'].isin([classdict])]
            temp_data = df[df['channelName'].isin([temp_class])]
            exec("df%s = temp_data"%newclass[temp_class])

        sheetnum = 0
        flag =0
        if os.path.isfile(path):
            # readbook = xlrd.open_workbook(path)
            # excel = copy(readbook)
            flag = 1
        # else:
        excel = xlwt.Workbook(encoding = 'utf-8')
        print("重写文件:{}".format(path))
        for temp in tqdm(classinformation):
            dfName='df'+str(newclass[temp])
            dfData = eval(dfName)
            w=1
            # global worksheet
            for content in dfData.values:
                if w==1:
                    excel,worksheet,nrows = self.chose_sheet(excel,temp,flag) #,sheetnum
                if not pd.isnull(content[0]):#非空值
                    worksheet.write(nrows, 0, label=content[0])
                worksheet.write(nrows, 1, label=content[1])
                worksheet.write(nrows, 2, label=content[2])
                nrows += 1
                w=0
                if nrows>=max_num+1:
                    excel.save(path)
                    break
            sheetnum += 1
            # if nrows<max_num+1:
            excel.save(path) # 保存并覆盖文件
            time.sleep(0.02)

        print('done')