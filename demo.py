# coding: UTF-8
import time
import torch
import numpy as np
from train_eval import test,predict_txt,predict_line
# from importlib import import_module
# import argparse
import os.path
import xlrd #,xlwt
from xlutils.copy import copy
from utils import build_dataset_test, build_dataset_input,build_iterator, get_time_dif
from datapreprocess import Linedata,Excel_preddata,Excel_testdata
# from datapremultiprocess import Linedata,Excel_preddata,Excel_testdata
import bert
import os,sys

this = os.path.abspath(os.path.dirname(__file__))
module = os.path.split(this)[0]
print(this,module)
sys.path.append(module)

# parser = argparse.ArgumentParser(description='Chinese Text Classification')
# parser.add_argument('--model', type=str, required=True, help='choose a model: Bert, ERNIE')
# args = parser.parse_args()
# args.model = 'bert'

def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath,encoding='UTF-8').readlines()]
    return stopwords
stopwords=set(stopwordslist('./stopwords/cg_stopwords.txt'))
stopwords=list(stopwords)

def write_excel(file_path,content,temp):  #,sheetnum
    readbook = xlrd.open_workbook(file_path)
    excel = copy(readbook)
    # sheet = readbook.sheet_by_index(1)#索引的方式，从0开始
    # sheet = excel.sheet_by_name(temp)#名字的方式
    # nrows = sheet.nrows#行 # ncols = sheet.ncols#列
    nrows = 1            
    worksheet=excel.get_sheet(temp)#获得当前sheet 
    for line in content:
        worksheet.write(nrows, 1, label=line)
        nrows += 1
    excel.save(file_path)
    print('done')

def oneline_predict(config,stopwords):
    while True: #单行文本测试
        title = input("输入新闻标题：")
        if len(title)<8:
            print("输入标题字数过少，请重新输入")
            continue
        # content = input("输入新闻内容：")
        content_=[]
        line=input("输入新闻内容(回车后按tab键和回车键结束输入)：")
        content_.append(line)
        while line!='\t':
            line=input()
            if line!='':
                content_.append(line)
        content=''.join(content_)
        if content:
            text = '\t'.join([title,content])
        else:
            text = title
        start_time = time.time()
        text = Linedata().chuli(stopwords,text)
        # y= method.predict(X)
        config.batch_size=1
        test_data = build_dataset_input(config,text)
        test_iter = build_iterator(test_data, config)
        # predict
        _ = predict_line(config, model, test_iter)
        time_dif = get_time_dif(start_time)
        print("Total Time usage:", time_dif)
        mode_1 = input("是否继续(请输入y或n):")
        if mode_1 == 'y':
            pass
        else:
            break
        # return result

def excel_predict(config,stopwords):
        # news_test = './dataprocess/new_test.xlsx'
    while True:
        print('输入数据较多时cpu处理用时会比较长,请耐心等待！')
        file_path  = input("输入测试excel文件路径：") #./初赛评审所用测试集.xlsx
        if os.path.isfile(file_path) and (file_path.endswith('.xlsx') or file_path.endswith('.xls')):
            test_path,sheet_names = Excel_preddata().chuli(stopwords,file_path) #multi_chuli多进程 chuli(stopwords,file_path)
            # test_path,sheet_names='./初赛评审所用测试集.txt',['类别', '说明']
        else:
            print('路径错误或文件格式错误，请重新输入')
            continue
        if test_path:
            config.test_path = test_path
        else:
            continue
        print("Loading data...")
        start_time = time.time()
        test_data = build_dataset_test(config)
        test_iter = build_iterator(test_data, config)
        time_dif = get_time_dif(start_time)
        print("Loading Time usage:", time_dif)
        # predict
        _,result_list,_= predict_txt(config,model,test_iter)
        #-------------------------结果写入excel-----------------------------#
        write_excel(file_path,result_list,sheet_names[0])

        mode_1 = input("是否继续(请输入y或n):")
        if mode_1 == 'y':
            pass
        else:
            break

def excel_test(config,stopwords):
        # news_test = './dataprocess/new_test.xlsx'
    while True:
        print('输入数据较多时cpu处理用时会比较长,请耐心等待！')
        file_path  = input("输入测试excel文件路径：")
        if os.path.isfile(file_path) and (file_path.endswith('.xlsx') or file_path.endswith('.xls')):
            test_path = Excel_testdata().chuli(stopwords,file_path) #multi_chuli多进程 chuli(stopwords,file_path)
        else:
            print('路径错误或文件格式错误，请重新输入')
            continue
        if test_path:
            config.test_path = test_path
        else:
            continue
        start_time = time.time()
        print("Loading data...")
        test_data = build_dataset_test(config)
        test_iter = build_iterator(test_data, config)
        time_dif = get_time_dif(start_time)
        print("Loading Time usage:", time_dif)
        # test
        print('请等待！')
        test(config, model, test_iter)
        mode_1 = input("是否继续(请输入y或n):")
        if mode_1 == 'y':
            pass
        else:
            break

def txt_test(config): #注：此处应输入已经处理好的txt文件数据
        # news_test = 'test.txt'
    while True:
        print('输入数据较多时cpu处理用时会比较长,请耐心等待！')
        #./THUCNews/data/test.txt  ./dataprocess/new_test.txt
        file_path  = input("输入测试txt文件路径：")
        if file_path.endswith('.txt') and os.path.isfile(file_path):
            config.test_path = file_path
        else:
            print('路径错误或文件格式错误，请重新输入！')
            continue
        start_time = time.time()
        print("Loading data...")
        test_data = build_dataset_test(config)
        test_iter = build_iterator(test_data, config)
        time_dif = get_time_dif(start_time)
        print("Loading Time usage:", time_dif)
        # test
        print('请等待！')
        test(config, model, test_iter)
        mode_1 = input("是否继续(请输入y或n):")
        if mode_1 == 'y':
            pass
        else:
            break

def run_test_predict(config,stopwords):
    while True:
        flag = 0
        flag_2 = 0
        mode=int(input("选择模式(0: 结束 1:逐行预测 2:excel文件预测 3:excel文件测试 4:txt文件测试(仅支持清洗后的数据)\n请输入数字0-4 ->:"))
        if mode == 1: #单行文本预测
            oneline_predict(config,stopwords)
            flag = 0
            while True:
                while True:
                    choice = int(input("选择模式(0: 结束 1:逐行预测 2:excel文件预测 3:excel文件测试 4:txt文件测试(仅支持清洗后的数据)\n请输入数字0-4 ->:"))
                    if choice==1:
                        oneline_predict(config,stopwords)
                    elif choice == 2:
                        excel_predict(config,stopwords)
                    elif choice == 3:
                        excel_test(config,stopwords)
                    elif choice == 4:
                        txt_test(config)
                    elif choice == 0:
                        flag = 1
                        break
                    else:
                        print('请重新输入!')
                if flag == 1:
                    print('感谢使用!')
                    break
                mode_1 = input("是否继续(请输入y或n):")
                if mode_1 == 'y':
                    pass
                else:
                    break
        elif mode==2:#输入xlsx或xls文件预测
            excel_predict(config,stopwords) 
            flag = 0
            while True:
                while True:
                    choice = int(input("选择模式(0: 结束 1:逐行预测 2:excel文件预测 3:excel文件测试 4:txt文件测试(仅支持清洗后的数据)\n请输入数字0-4 ->:"))
                    if choice==1:
                        oneline_predict(config,stopwords)
                    elif choice == 2:
                        excel_predict(config,stopwords)
                    elif choice == 3:
                        excel_test(config,stopwords)
                    elif choice == 4:
                        txt_test(config)
                    elif choice == 0:
                        flag = 1
                        break
                    else:
                        print('请重新输入!')
                if flag == 1:
                    print('感谢使用!')
                    break
                mode_1 = input("是否继续(请输入y或n):")
                if mode_1 == 'y':
                    pass
                else:
                    break
        elif mode==3:#输入xlsx或xls文件测试
            excel_test(config,stopwords) # ./dataprocess/训练数据样本.xlsx ./7.8/7.8.xlsx
            flag = 0
            while True:
                while True:
                    choice = int(input("选择模式(0: 结束 1:逐行预测 2:excel文件预测 3:excel文件测试 4:txt文件测试(仅支持清洗后的数据)\n请输入数字0-4 ->:"))
                    if choice==1:
                        oneline_predict(config,stopwords)
                    elif choice == 2:
                        excel_predict(config,stopwords)
                    elif choice == 3:
                        excel_test(config,stopwords)
                    elif choice == 4:
                        txt_test(config)
                    elif choice == 0:
                        flag = 1
                        break
                    else:
                        print('请重新输入!')
                if flag == 1:
                    print('感谢使用!')
                    break
                mode_1 = input("是否继续(请输入y或n):")
                if mode_1 == 'y':
                    pass
                else:
                    break
        elif mode==4: #输入txt文件测试
            txt_test(config) #./THUCNews/data/test.txt  ./dataprocess/new_test.txt
            flag = 0
            while True:
                while True:
                    choice = int(input("选择模式(0: 结束 1:逐行预测 2:excel文件预测 3:excel文件测试 4:txt文件测试(仅支持清洗后的数据)\n请输入数字0-4 ->:"))
                    if choice==1:
                        oneline_predict(config,stopwords)
                    elif choice == 2:
                        excel_predict(config,stopwords)
                    elif choice == 3:
                        excel_test(config,stopwords)
                    elif choice == 4:
                        txt_test(config)
                    elif choice == 0:
                        flag = 1
                        break
                    else:
                        print('请重新输入!')
                if flag == 1:
                    print('感谢使用!')
                    break
                mode_1 = input("是否继续(请输入y或n):")
                if mode_1 == 'y':
                    pass
                else:
                    break
        elif mode==0:
            flag_2 = 1
            print('感谢使用!')
            time.sleep(3)
        else:
            print('请重新输入!')
            continue

        if flag == 1 or flag_2 == 1:
            break

if __name__ == '__main__':
    dataset = 'THUCNews'  # 数据集

    # model_name = args.model  # bert
    # model_name = ''models.' + '
    # x = import_module('models.' + model_name) #'models.' + model_name
    config = bert.Config(dataset)
    np.random.seed(1)
    torch.manual_seed(1)
    # torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样
    model = bert.Model(config).to(config.device)
    run_test_predict(config,stopwords)
