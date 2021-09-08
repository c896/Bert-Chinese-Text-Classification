# coding: UTF-8
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn import metrics
from tqdm import tqdm
import time
from utils import get_time_dif
# from pytorch_pretrained.optimization import BertAdam


# 权重初始化，默认xavier
def init_network(model, method='xavier', exclude='embedding', seed=123):
    for name, w in model.named_parameters():
        if exclude not in name:
            if len(w.size()) < 2:
                continue
            if 'weight' in name:
                if method == 'xavier':
                    nn.init.xavier_normal_(w)
                elif method == 'kaiming':
                    nn.init.kaiming_normal_(w)
                else:
                    nn.init.normal_(w)
            elif 'bias' in name:
                nn.init.constant_(w, 0)
            else:
                pass

'''
def train(config, model, train_iter, dev_iter, test_iter):
    start_time = time.time()
    model.train()
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}]
    # optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    optimizer = BertAdam(optimizer_grouped_parameters,
                         lr=config.learning_rate,
                         warmup=0.05,
                         t_total=len(train_iter) * config.num_epochs)
    total_batch = 0  # 记录进行到多少batch
    dev_best_loss = float('inf')
    last_improve = 0  # 记录上次验证集loss下降的batch数
    flag = False  # 记录是否很久没有效果提升
    model.train()
    for epoch in range(config.num_epochs):
        print('Epoch [{}/{}]'.format(epoch + 1, config.num_epochs))
        for i, (trains, labels) in enumerate(train_iter):
            outputs = model(trains) #[128,10]
            model.zero_grad()
            loss = F.cross_entropy(outputs, labels) #交叉熵 如果你的概率是通过softmax公式得到的，那么cross entropy就是softmax loss
            loss.backward() #反向传播
            optimizer.step() #更新参数
            if total_batch % 100 == 0:
                # 每多少轮输出在训练集和验证集上的效果
                true = labels.data.cpu()
                predic = torch.max(outputs.data, 1)[1].cpu()
                train_acc = metrics.accuracy_score(true, predic) #准确率
                dev_acc, dev_loss = evaluate(config, model, dev_iter)
                if dev_loss < dev_best_loss:
                    dev_best_loss = dev_loss
                    torch.save(model.state_dict(), config.save_path)
                    improve = '*'
                    last_improve = total_batch
                else:
                    improve = ''
                time_dif = get_time_dif(start_time)
                msg = 'Iter: {0:>6},  Train Loss: {1:>5.2},  Train Acc: {2:>6.2%},  Val Loss: {3:>5.2},  Val Acc: {4:>6.2%},  Time: {5} {6}'
                print(msg.format(total_batch, loss.item(), train_acc, dev_loss, dev_acc, time_dif, improve))
                model.train()
            total_batch += 1
            if total_batch - last_improve > config.require_improvement:
                # 验证集loss超过1000batch没下降，结束训练
                print("No optimization for a long time, auto-stopping...")
                flag = True
                break
        if flag:
            break
    test(config, model, test_iter)
'''

def predict_line(config, model, test_iter):
    # test
    model.load_state_dict(torch.load(config.save_path,map_location='cpu'))
    model.eval()
    start_time = time.time()
    result = predict_input(model, test_iter)
    print("Test Result:", result)
    time_dif = get_time_dif(start_time)
    print("Predict Time usage:", time_dif)
    return result

def predict_txt(config, model, test_iter):
    # test
    model.load_state_dict(torch.load(config.save_path,map_location='cpu'))
    model.eval()
    start_time = time.time()
    predict_list,result_list = predict(model, test_iter)
    time_dif = get_time_dif(start_time)
    print("Predict Time usage:", time_dif)
    return predict_list,result_list,time_dif

def test(config, model, test_iter):
    # test
    model.load_state_dict(torch.load(config.save_path,map_location='cpu'))
    model.eval()
    start_time = time.time()
    test_acc, test_loss, test_report, test_confusion = evaluate(config, model, test_iter, test=True)
    msg = 'Test Loss: {0:>5.2},  Test Acc: {1:>6.2%}'
    print(msg.format(test_loss, test_acc))
    print("Precision, Recall and F1-Score...")
    print(test_report)
    print("Confusion Matrix...")
    print(test_confusion)
    time_dif = get_time_dif(start_time)
    print("Test Time usage:", time_dif)

#-------------------------------测试-----------------------------------------------#
def evaluate(config, model, data_iter, test=False):
    model.eval()
    loss_total = 0
    predict_all = np.array([], dtype=int)
    labels_all = np.array([], dtype=int)
    with torch.no_grad():
        for texts, labels in data_iter:
            outputs = model(texts)
            loss = F.cross_entropy(outputs, labels)
            loss_total += loss
            labels = labels.data.cpu().numpy()
            predic = torch.max(outputs.data, 1)[1].cpu().numpy()#每行的最大值的索引 torch.max(input, dim) dim=1是每行的最大值
#             tt = torch.max(outputs.data, 1)[0].cpu().numpy() #每行的最大值
# #-------------------------------置信度0.15-----------------------------------#
#             i = 0
#             for t in tt:
#                 if t<0.15:
#                     predic[i]= 9
#                 i += 1
            # predic = torch.max(outputs.data, 1)[1].cpu().numpy()
            labels_all = np.append(labels_all, labels)
            predict_all = np.append(predict_all, predic)

    acc = metrics.accuracy_score(labels_all, predict_all)
    if test:
        predict_list = np.unique(predict_all)
        labels_list = np.unique(labels_all)
        biaozhun= np.arange(10)
        del_index=[]
        a=[x for x in predict_list if x not in labels_list] #找出不同的
        if len(a)==0 and predict_list.size<10:
            for idx in biaozhun:
                if idx not in labels_list:
                    del_index.append(idx)
            config.class_list=[i for num,i in enumerate(config.class_list) if num not in del_index]
        report = metrics.classification_report(labels_all, predict_all, target_names=config.class_list, digits=4)
        confusion = metrics.confusion_matrix(labels_all, predict_all)
        return acc, loss_total / len(data_iter), report, confusion
    return acc, loss_total / len(data_iter)

#-----------------------------单行文本预测-----------------------------------#
def predict_input(model, data_iter):
    model.eval()
    result_list=[]
    iddict={0:'财经',1:'房产',2:'教育',3:'科技',4:'军事',5:'汽车',6:'体育',7:'游戏',8:'娱乐',9:'其他'}  
    with torch.no_grad():
        for texts, labels in data_iter:
            outputs = model(texts)
            t = outputs.data.cpu().numpy()
            t=t[0].tolist()
#-------------------------------置信度0.85-----------------------------------#
            score=max(t)
            # score_=abs(t[8])
            if score<0.85:
                predic=9
            # elif score_>2.5: # and score<5:
            #     predic=8
            else:
                # predic = torch.max(outputs.data, 1)[1].cpu().numpy()
                predic = int(torch.max(outputs.data, 1)[1].cpu().numpy())
            result = iddict[predic]
            result_list.append(result)
    return result_list
    # return acc, loss_total / len(data_iter)

#-----------------------------txt多行文本预测-----------------------------------#
def predict(model, data_iter):
    model.eval()
    predict_all = np.array([], dtype=int)
    result_list=[]
    iddict={0:'财经',1:'房产',2:'教育',3:'科技',4:'军事',5:'汽车',6:'体育',7:'游戏',8:'娱乐',9:'其他'} 
    print('开始预测,请等待')
    with torch.no_grad():
        with tqdm(data_iter) as t:
            for texts, _ in t:
                outputs = model(texts)
                predic = torch.max(outputs.data, 1)[1].cpu().numpy()#每行的最大值的索引 torch.max(input, dim) dim=1是每行的最大值
                tt = torch.max(outputs.data, 1)[0].cpu().numpy() #每行的最大值      
    #-------------------------------置信度0.85-----------------------------------#
                i = 0
                for t in tt:
                    if t<0.85:
                        predic[i]= 9
                    # elif i==8 and abs(t)>2.5:# and tt[9]<5:
                    #     predic[i]= 8
                    i += 1
                for p in predic:
                    result = iddict[p]
                    result_list.append(result)
                predict_all = np.append(predict_all, predic)

    return predict_all,result_list