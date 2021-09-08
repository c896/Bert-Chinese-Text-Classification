from jieba import lcut,analyse
import re
from tqdm import tqdm #, trange
import pandas as pd
import string
from datetime import timedelta
import time
# from sklearn.utils import shuffle
# from sklearn.model_selection import train_test_split
# import matplotlib.pyplot as plt
# import multiprocessing
# import warnings

analyse.set_stop_words('./stopwords/cg_stopwords.txt')
# warnings.filterwarnings("ignore")
# plt.rcParams['font.sans-serif']='SimHei'
# plt.rcParams['axes.unicode_minus']=False

#世界国际历史有歧义
classdict = {'财经':0,'股票':0,'房产':1,'教育':2,'科技':3,'数码': 3,'科普': 3,'军事':4,'汽车':5,'体育':6,'足球': 6,'综合体育最新':6,\
            '体育焦点':6,'游戏':7,'娱乐':8,'其它':9,'其他':9,'社会':9,'健康':9,'法制':9,'世界':9,'国际':9,'文化':9,'历史':9,'时尚':9,'情感':9,\
                '旅游':9,'健康':9,'美食':9,'宠物':9,'星座':9,'动漫':9}
iddict={0:'财经',1:'房产',2:'教育',3:'科技',4:'军事',5:'汽车',6:'体育',7:'游戏',8:'娱乐',9:'其他'}        

def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(time_dif),microseconds=(time_dif-int(time_dif))*10**6)
    #return timedelta(seconds=int(time_dif))

class Linedata(object):
    def __init__(self):
        # self.textinput = textinput
        # self.path_txt = path_txt
        # self.news_path=news_path
        self.classdict = {'财经':0,'房产':1,'教育':2,'科技':3,'军事':4,'汽车':5,'体育':6,'游戏':7,'娱乐':8,'其他':9}

    def stopwordslist(self,filepath):
        stopwords = [line.strip() for line in open(filepath,encoding='UTF-8').readlines()]
        return stopwords

    def chuli(self,stopwords,textinput):
        # textinput=self.textinput
        #------------------------------------------加载停用词-----------------------------------------------------#
        # strip() 方法用于移除字符串头尾指定的字符(默认为空格或换行符)或字符序列
        # stopwords=set(self.stopwordslist('cg_stopwords.txt'))
        # # vocab=set(self.stopwordslist('vocab.txt'))
        # stopwords=list(stopwords)

        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')
        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        textinput = textinput.strip()
        #--------------------------------标题处理----------------------------------------#
        try:
            title,text = textinput.split('\t')
            title_  = lcut(title)
            title_  = [w for w in title_ if (w not in stopwords or w in punc) and not re.match('^[0-9|.]*$',w)]
                    # print(title_)
            newtitle = "".join(title_)
        except:
            text_  = analyse.extract_tags(textinput,32)
            text_ = [w for w in text_ if not re.match('^[0-9|.]*$',w)]
                    # print(title_)
            output= "".join(text_) +'\t'+'9'
            print("转换后:{}".format(output[:-2]))
            return output
        #--------------------------------内容处理----------------------------------------#
        # text = [w for w in text if w in vocab] 
        # text = "".join(text)
        text_ = analyse.extract_tags(text,32)
        text_ = [w for w in text_ if w not in title_ and not re.match('^[0-9|.]*$',w)] #'^[a-z|A-Z|0-9|.]*$'  \w 匹配字母或数字或下划线或汉字 等价于 '[^A-Za-z0-9_]'。
        newtext = "".join(text_)
        output = newtitle +' '+ newtext +'\t'+'9'
        # print(newtitle)
        # print(newtext)
        print("转换后:{}".format(output[:-2]))
        return output


class Excel_preddata(object):
    def __init__(self):
        # self.textinput = textinput
        self.classdict = {'财经':0,'房产':1,'教育':2,'科技':3,'军事':4,'汽车':5,'体育':6,'游戏':7,'娱乐':8,'其他':9}
#------------------------读取文件-------------------------#
    def read_excel(self,path):
        data_xls = pd.ExcelFile(path)
        df =pd.read_excel(path,sheet_name=0,usecols=[2,3])
        print(data_xls.sheet_names)
        # for idx in range(1,len(data_xls.sheet_names)-1):
        #     # print(idx)
        #     df_ =pd.read_excel(path,sheet_name=idx,usecols=[0,1,2])
        #     df_=df_.drop(index=0)
        #     df = pd.concat([df, df_], axis=0)
        return df,data_xls.sheet_names

    def stopwordslist(self,filepath):
        stopwords = [line.strip() for line in open(filepath,encoding='UTF-8').readlines()]
        return stopwords

    def chuli(self,stopwords,news_path):
        flag = 0
        if news_path.endswith('.xlsx'):
            path_txt = news_path.split('.xlsx')[0] + '.txt'
        elif news_path.endswith('.xls'):
            path_txt = news_path.split('.xls')[0] + '.txt'
        else:
            flag = 1
            print('输入文件格式不符,请重新输入')
        if flag == 1:
            return None
        with open(path_txt,'w+', encoding='UTF-8') as f:
                f.write('')

        start_time = time.time()
        df,sheet_names= self.read_excel(news_path)
        #------------------------------------------加载停用词-----------------------------------------------------#
        # strip() 方法用于移除字符串头尾指定的字符(默认为空格或换行符)或字符序列
        # stopwords=set(self.stopwordslist('cg_stopwords.txt'))
        # # vocab=set(self.stopwordslist('vocab.txt'))
        # stopwords=list(stopwords)
        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')
        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        #--------------------------------标题处理----------------------------------------#
        with open(path_txt,'a+', encoding='UTF-8') as f:
            print('数据预处理中。。。')
            with tqdm(df.values) as t:
                for content in t: #可改成多进程处理
                    title = content[0]
                    text = content[1]
                    # label = content[1]
                    title_  = lcut(title.strip())
                    title_  = [w for w in title_ if (w not in stopwords or w in punc) and not re.match('^[0-9|.]*$',w)]
                    # print(title_)
                    newtitle = "".join(title_)
            #--------------------------------内容处理----------------------------------------#
                    try:
                        text_ = analyse.extract_tags(text,32)
                        text_ = [w for w in text_ if w not in title_ and not re.match('^[0-9|.]*$',w)] #'^[a-z|A-Z|0-9|.]*$'  \w 匹配字母或数字或下划线或汉字 等价于 '[^A-Za-z0-9_]'。
                        newtext = "".join(text_)
                        title_text = " ".join([newtitle,newtext])
                        newcontent = title_text +'\t'+'9'+'\n'
                    except:
                        newcontent = newtitle +'\t'+'9'+'\n'
                    # print(newtitle)
                    # print(newtext)
                    
                    f.write(newcontent)
            time_dif = get_time_dif(start_time)
            print('数据预处理完成')
            print("Preprocess Time usage:", time_dif)
        return path_txt,sheet_names


class Excel_testdata(object):
    def __init__(self):
        # self.textinput = textinput
        self.classdict = {'财经':0,'房产':1,'教育':2,'科技':3,'军事':4,'汽车':5,'体育':6,'游戏':7,'娱乐':8,'其他':9}
#------------------------读取文件-------------------------#
    def read_excel(self,path):
        data_xls = pd.ExcelFile(path)
        df =pd.read_excel(path,sheet_name=0,usecols=[0,1,2])
        print(data_xls.sheet_names)
        for idx in range(1,len(data_xls.sheet_names)-1):
            # print(idx)
            df_ =pd.read_excel(path,sheet_name=idx,usecols=[0,1,2])
            df_=df_.drop(index=0)
            df = pd.concat([df, df_], axis=0)
        return df

    def stopwordslist(self,filepath):
        stopwords = [line.strip() for line in open(filepath,encoding='UTF-8').readlines()]
        return stopwords

    def chuli(self,stopwords,news_path):
        flag = 0
        if news_path.endswith('.xlsx'):
            path_txt = news_path.split('.xlsx')[0] + '.txt'
        elif news_path.endswith('.xls'):
            path_txt = news_path.split('.xls')[0] + '.txt'
        else:
            flag = 1
            print('输入文件格式不符,请重新输入')
        if flag == 1:
            return None
        with open(path_txt,'w+', encoding='UTF-8') as f:
                f.write('')
        start_time = time.time()
        df = self.read_excel(news_path)
        # df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        # plt.title('数据分布')
        # # plt.show()
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #------------------------------------------加载停用词-----------------------------------------------------#
        # strip() 方法用于移除字符串头尾指定的字符(默认为空格或换行符)或字符序列
        # stopwords=set(self.stopwordslist('cg_stopwords.txt'))
        # # vocab=set(self.stopwordslist('vocab.txt'))
        # stopwords=list(stopwords)

        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')
        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        #--------------------------------标题处理----------------------------------------#
        with open(path_txt,'a+', encoding='UTF-8') as f:
            print('数据预处理中。。。')
            with tqdm(df.values) as t:
                for content in t:
                    title = content[2]
                    text = content[0]
                    # label = content[1]
                    title_  = lcut(title.strip())
                    title_  = [w for w in title_ if (w not in stopwords or w in punc) and not re.match('^[0-9|.]*$',w)]
                    # print(title_)
                    newtitle = "".join(title_)
            #--------------------------------内容处理----------------------------------------#
                    try:
                        # text = [w for w in text if w in vocab] 
                        # text = "".join(text)
                        text_ = analyse.extract_tags(text,32)
                        text_ = [w for w in text_ if w not in title_ and not re.match('^[0-9|.]*$',w)] #'^[a-z|A-Z|0-9|.]*$'  \w 匹配字母或数字或下划线或汉字 等价于 '[^A-Za-z0-9_]'。
                        newtext = "".join(text_)
                        title_text = " ".join([newtitle,newtext])
                        newcontent = title_text +'\t'+ str(classdict[content[1]])+'\n'
                    except:
                        newcontent = newtitle +'\t'+ str(classdict[content[1]])+'\n'
                    # print(newtitle)
                    # print(newtext)
                    
                    f.write(newcontent)
            time_dif = get_time_dif(start_time)
            print('数据预处理完成')
            print("Preprocess Time usage:", time_dif)
                # time.sleep(0.01)
        return path_txt

# if __name__=='__main__':
#     path_test = 'test.txt'
#     news_test  = r'./new_test.xlsx'
#     Excel_testdata(path_test,news_test).chuli()