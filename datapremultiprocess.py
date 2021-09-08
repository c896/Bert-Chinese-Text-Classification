# import jieba
from jieba import lcut,analyse
# import jieba.analyse as analyse
import re
from tqdm import tqdm #, trange
import pandas as pd
# from sklearn.utils import shuffle
# from sklearn.model_selection import train_test_split
# import matplotlib.pyplot as plt
# import warnings
import multiprocessing
import string
import time
# import frozen

multiprocessing.freeze_support()
analyse.set_stop_words('./stopwords/cg_stopwords.txt')

# warnings.filterwarnings("ignore")
# plt.rcParams['font.sans-serif']='SimHei'
# plt.rcParams['axes.unicode_minus']=False

# classdict = {'财经':0,'股票':0,'房产':1,'教育':2,'科技':3,'军事':4,'汽车':5,'体育':6,'综合体育最新':6,'体育焦点':6,\
#                 '游戏':7,'娱乐':8,'其它':9,'社会':9,'健康':9,'法制':9}
#世界国际历史有歧义
classdict = {'财经':0,'股票':0,'房产':1,'教育':2,'科技':3,'数码': 3,'科普': 3,'军事':4,'汽车':5,'体育':6,'足球': 6,'综合体育最新':6,\
            '体育焦点':6,'游戏':7,'娱乐':8,'其它':9,'其他':9,'社会':9,'健康':9,'法制':9,'世界':9,'国际':9,'文化':9,'历史':9,'时尚':9,'情感':9,\
                '旅游':9,'健康':9,'美食':9,'宠物':9,'星座':9,'动漫':9}
iddict={0:'财经',1:'房产',2:'教育',3:'科技',4:'军事',5:'汽车',6:'体育',7:'游戏',8:'娱乐',9:'其他'}        

class Linedata(object):
    def __init__(self):
        # self.textinput = textinput
        # self.path_txt = path_txt
        # self.news_path=news_path
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
        #-------------------clean words whos length<2 and with only numbers and characters-------------------#
                # title_1 = jieba.lcut(title.strip())
                # title_1 = [w for w in title_1 if len(w)>1 and not re.match('^[0-9|.]*$',w)]
                # title  = [w for w in title if  w in vocab] 
                # title = "".join(title)

        #--------------------------------内容处理----------------------------------------#
        # text = [w for w in text if w in vocab]   \w 匹配字母或数字或下划线或汉字 等价于 '[^A-Za-z0-9_]'。
        # text = "".join(text)
        text_ = analyse.extract_tags(text,32)
        text_ = [w for w in text_ if w not in title_ and not re.match('^[0-9|.]*$',w)] #'^[a-z|A-Z|0-9|.]*$' 
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
        df,sheet_names= self.read_excel(news_path)
        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')

        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        #--------------------------------标题处理----------------------------------------#
        with open(path_txt,'a+', encoding='UTF-8') as f:
            for content in tqdm(df.values): #可改成多进程处理
                title = content[0]
                text = content[1]
                # label = content[1]
        #-------------------clean words whos length<2 and with only numbers and characters-------------------#
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
                    newcontent = title_text +'\t'+'9'+'\n'
                except:
                    newcontent = newtitle +'\t'+'9'+'\n'
                # print(newtitle)
                # print(newtext)
                
                f.write(newcontent)
                time.sleep(0.01)
        return path_txt,sheet_names

    def worker(self, q1, q2, b1,stopwords,punc):
        """
        定义处理线程
        """
        while True:
            content = q1.get() 
            if len(content)==0:
                b1.wait() # 阻塞进程，等待其他进程执行完毕
                break
            title = content[0]
            text = content[1]
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
                newcontent = title_text +'\t'+'9'+'\n'
            except:
                newcontent = newtitle +'\t'+'9'+'\n'  
            q2.put(newcontent)
        print("Worker finished!")

    def feed(self, q1, q2, b1, num, df):
        """
        定义生产者
        """
        # for f_name in tqdm.tqdm_gui(file_paths): #终端进度条展示
        for content in tqdm(df.values):# 每次提供一些数据 
            q1.put(content) 
        for itr in range(num):
            q1.put([])          # 在输入结束后输入结束标志（空列表）
        b1.wait() # 阻塞，等待所有处理完成后向输出进程输入终止命令
        q2.put([]) # 输入空白以终止进程
        print("Feed finished")

    def output(self, q2, path_txt):
        """
        定义输出单元
        """
        count = 0
        # newcontent=[]
        while True:
            a = q2.get()
            if len(a)==0:
                break
            # newcontent.append(a)
            with open(path_txt,'a+', encoding='UTF-8') as f:
                f.write(a)
            count += 1
        print("Output finished", "N input", count)

    def multi_chuli(self,stopwords,news_path):
        """
        主程序
        最好使用类进行封装
        """
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
        df,sheet_names= self.read_excel(news_path)
        # df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        # plt.title('数据分布')
        # # plt.show()
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')

        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        n_process = 8 # 定义进程数量
        # multiprocessing.freeze_support()
        q1 = multiprocessing.Queue(50) # 定义队列
        q2 = multiprocessing.Queue(50) 
        barrier = multiprocessing.Barrier(n_process+1) # 用于进程同步，同步指令还可以使用过Manager、Pipe等，注意阻塞造成的死锁问题。
        mp1 = multiprocessing.Process(target=self.feed, args=(q1, q2, barrier, n_process, df)) #加载df下所有行
        mp1.start()#多进程读取文件路径
        wks = []
        # mydict=multiprocessing.Manager().dict()   #主进程与子进程共享这个字典
        stopwords=multiprocessing.Manager().list(stopwords)   #主进程与子进程共享这个List
        punc=multiprocessing.Manager().list(punc)
        # num = multiprocessing.Value('d', 1.0)  # 共享数字
        # arr = multiprocessing.Array('i', range(10))  # 共享数组
        for p in range(n_process): #取决于cpu的核心数
            w1 = multiprocessing.Process(target=self.worker, args=(q1, q2, barrier, stopwords, punc)) #多进程读取所有行，并进行分词
            w1.start() 
            wks.append(w1)
        mp2 = multiprocessing.Process(target=self.output, args=(q2, path_txt)) #多进程地把读取的文件数据并存储为txt
        mp2.start()
        
        #设置进程顺序
        mp1.join()
        for w in wks:
            w.join() 
        mp2.join()

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

    def content_process(self,df,stopwords,punc):
        for content in tqdm(df.values):
            title = content[2]
            text = content[0]
            # label = content[1]
        #-------------------clean words whos length<2 and with only numbers and characters-------------------#    
            title_  = lcut(title.strip())
            title_  = [w for w in title_ if (w not in stopwords or w in punc) and not re.match('^[0-9|.]*$',w)]
            # print(title_)
            newtitle = "".join(title_)
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
            
        return newcontent

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
        df = self.read_excel(news_path)
        # df["channelName"].value_counts().plot.pie(subplots=True, figsize=(4, 4), autopct='%0.1f%%')
        # plt.title('数据分布')
        # # plt.show()
        # plt.draw()
        # plt.pause(2)  #显示秒数
        # plt.close()
        #---------------------------------基于TF-IDF算法的关键词抽取------------------------------------------#
        # analyse.set_stop_words('cg_stopwords.txt')

        # import zhon.hanzi
        # punc = string.punctuation + '；：，、？！‘’“”《》￥%' #zhon.hanzi.punctuation
        punc = string.punctuation + '《》￥%'
        #--------------------------------标题处理----------------------------------------#
        newcontent = self.content_process(df,stopwords,punc)    
        with open(path_txt,'a+', encoding='UTF-8') as f:
            for line in newcontent:                   
                f.write(line)
                time.sleep(0.01)
        return path_txt

    def worker(self, q1, q2, b1,stopwords,punc):
        """
        定义处理线程
        """
        while True:
            content = q1.get() 
            if len(content)==0:
                b1.wait() # 阻塞进程，等待其他进程执行完毕
                break
            title = content[2]
            text = content[0]
            title_  = lcut(title.strip())
            title_  = [w for w in title_ if (w not in stopwords or w in punc) and not re.match('^[0-9|.]*$',w)]
            # print(title_)
            newtitle = "".join(title_)
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
            q2.put(newcontent)
        print("Worker finished!")

    def feed(self, q1, q2, b1, num, df):
        """
        定义生产者
        """
        # for f_name in tqdm.tqdm_gui(file_paths): #终端进度条展示
        for content in tqdm(df.values):# 每次提供一些数据 
            q1.put(content) 
        for itr in range(num):
            q1.put([])          # 在输入结束后输入结束标志（空列表）
        b1.wait() # 阻塞，等待所有处理完成后向输出进程输入终止命令
        q2.put([]) # 输入空白以终止进程
        print("Feed finished")

    def output(self, q2, path_txt):
        """
        定义输出单元
        """
        count = 0
        # newcontent=[]
        while True:
            a = q2.get()
            if len(a)==0:
                break
            # newcontent.append(a)
            with open(path_txt,'a+', encoding='UTF-8') as f:
                f.write(a)
            count += 1
        print("Output finished", "N input", count)

    def multi_chuli(self,stopwords,news_path):
        """
        主程序
        最好使用类进行封装
        """
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
        n_process = 8 # 定义进程数量
        # multiprocessing.freeze_support()
        q1 = multiprocessing.Queue(50) # 定义队列
        q2 = multiprocessing.Queue(50) 
        barrier = multiprocessing.Barrier(n_process+1) # 用于进程同步，同步指令还可以使用过Manager、Pipe等，注意阻塞造成的死锁问题。
        mp1 = multiprocessing.Process(target=self.feed, args=(q1, q2, barrier, n_process, df)) #加载df下所有行
        mp1.start()#多进程读取文件路径
        wks = []
        # mydict=multiprocessing.Manager().dict()   #主进程与子进程共享这个字典
        stopwords=multiprocessing.Manager().list(stopwords)   #主进程与子进程共享这个List
        punc=multiprocessing.Manager().list(punc)
        # num = multiprocessing.Value('d', 1.0)  # 共享数字
        # arr = multiprocessing.Array('i', range(10))  # 共享数组
        for p in range(n_process): #取决于cpu的核心数
            w1 = multiprocessing.Process(target=self.worker, args=(q1, q2, barrier, stopwords, punc)) #多进程读取所有行，并进行分词
            w1.start() 
            wks.append(w1)
        mp2 = multiprocessing.Process(target=self.output, args=(q2, path_txt)) #多进程地把读取的文件数据并存储为txt
        mp2.start()
        
        #设置进程顺序
        mp1.join()
        for w in wks:
            w.join() 
        mp2.join()

        return path_txt