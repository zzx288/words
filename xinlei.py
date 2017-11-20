#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import math
import os
import codecs
import gc
from pymongo import MongoClient

def find_words(words,num=6):
    split_words={}
    count_all = 0
    unused_words = u" \t\r\n，。：；、“‘”【】『』|=+-——（）*&……%￥#@！~·《》？/?<>,.;:'\"[]{}_)(^$!`"
    unused_english = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in unused_words:
        count_all += words.count(i)
    for i in unused_english:
        count_all += words.count(i)
    lens = len(words)
    len_deal = lens-count_all
    for i in range(0,lens):
        if(words[i] in unused_words or words[i] in unused_english):
            continue
        for j in range(1,num+1):
            if(words[i+j-1] in unused_words or words[i+j-1] in unused_english):
                break
            if i+j < lens -num-2:
                if words[i:i+j] in split_words:
                    split_words[words[i:i+j]][0] += 1
                    split_words[words[i:i+j]][1] = float(split_words[words[i:i+j]][0])/float(len_deal)
                    if(words[i-1] not in unused_words and words[i-1] not in unused_english and words[i-1]):
                        if(words[i-1] in split_words[words[i:i+j]][4].keys()):
                            split_words[words[i:i+j]][4][words[i-1]] += 1
                        else:
                            split_words[words[i:i+j]][4][words[i-1]] = 1
                    if(words[i+j] not in unused_words and words[i+j] not in unused_english):
                        if(words[i+j] in split_words[words[i:i+j]][5].keys()):
                            split_words[words[i:i+j]][5][words[i+j]] += 1
                        else:                        
                            split_words[words[i:i+j]][5][words[i+j]] = 1
                else:
                    split_words[words[i:i+j]]=[1,1/float(len_deal),1,0,{},{}]
                    if(words[i-1] not in unused_words and words[i-1] not in unused_english):
                        split_words[words[i:i+j]][4][words[i-1]] = 1
                    if(words[i+j] not in unused_words and words[i+j] not in unused_english):
                        split_words[words[i:i+j]][5][words[i+j]] = 1
            print ("完成 :" + str(float(i)/float(len(words))*100) + " %")              
    return split_words
                
def read_file(a):
    words = ""
    i=0
    pathdir = os.listdir(a)
    for alldir in pathdir:
        test = codecs.open(a+"\\"+alldir, 'r',encoding='utf-8')
        words += test.read()
        test.close()
        i += 1
        print(i)
    return words

if __name__ == '__main__':
    #words = read_file('F:\\民事案件例子')
    test = codecs.open('F:\\民事案件例子\\102-done.xml', 'r',encoding='utf-8')
    words = test.read()
    test.close()
    word_len=int(input("word_len"))   
    print ("splitting......")
    split=find_words(words,word_len)
    del(words)
    gc.collect()
    client = MongoClient('localhost',27017)
    db = client.test_word
    collection = db.test_collection
    db_count = 0
    for i in split.keys():
        db_count += 1
        sig = {'str':str(i),'count':int(split[i][0]),'freq':float(split[i][1]),'nh':int(split[i][2]),\
               'free':float(split[i][3]),'fro':split[i][4],'back':split[i][5],'len':int(len(i))}
        collection.insert(sig)
        print('db-done-',db_count)
    print("ok")

    print ("凝聚程度...")
    len2 = collection.find({'len':{'$gt':1}},no_cursor_timeout = True)
    nh_count = 0
    #test = codecs.open('F:\\ch1.txt', 'a',encoding='utf-8')
    for temp in len2:
        nh_count +=1
        ci = temp['str']
        lef1 = collection.find_one({'str':ci[1:]})
        #print("lef1 ---done",j)
        lef2 = collection.find_one({'str':ci[:1]})
        #print("lef2 ---done",j)
        left_p=temp['freq']/(lef1['freq']*lef2['freq'])
        rgh1 = collection.find_one({'str':ci[:-1]})
        rgh2 = collection.find_one({'str':ci[-1:]})
        #print("rgh ---done",j)
        right_p=temp['freq']/(rgh1['freq']*rgh2['freq'])
        if(left_p<right_p):
            tem=left_p
        else:
            tem=right_p
        collection.update({'str':ci},{"$set":{'nh':tem}})
        #test.write(' key'+temp['str']+' left:'+lef1['str']+' :left'+lef2['str']+' right:'+rgh['str']+'nh '+str(tem)+'\n')
        print("nh-done-",nh_count)
    len2.close()
    #test.close()
    print('ok1')
    
    free_count = 0
    result = db.test_re
    allr = collection.find(no_cursor_timeout = True)
    for temp in allr:
        free_count += 1
        front_free=0
        end_free=0
        su = temp['count']
        fro_dic = temp['fro']
        back_dic = temp['back']
        for t1 in fro_dic.keys():
            tmp = fro_dic[t1]/su
            front_free -= math.log(tmp)*tmp
        for t2 in back_dic.keys():
            tmp = back_dic[t2]/su
            end_free -= math.log(tmp)*tmp
        if(front_free < end_free):
            tem = front_free
        else:
            tem = end_free
        if(temp['len']>1):
            r_w = {'str':temp['str'],'count':temp['count'],'freq':temp['freq'],'nh':temp['nh'],\
               'nhfr':tem*temp['nh'],'free':tem}
            result.insert(r_w)
        print("free-done-",free_count)
    allr.close()    
    print('ok2')   
    print(db_count,nh_count,free_count)        
    while True:
        freq=int(input("输入词语频率"))
        nh=int(input("输入凝聚程度"))
        free=float(input("输入自由程度"))  
        final_set = result.find({'count':{'$gt':freq},'nh':{'$gt':nh},'free':{'$gt':free}}).sort('count')
        for tmp in final_set:
            print(tmp)




    
    
    
    
    
    
