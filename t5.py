#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import math
import os
import codecs
import gc

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
                    split_words[words[i:i+j]][0]+=1
                    split_words[words[i:i+j]][1]=float(split_words[words[i:i+j]][0])/float(len_deal)
                    if(words[i-1] not in unused_words and words[i-1] not in unused_english):
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

        if(i%10000==0):
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

def find_nh(words_dic):
    test = codecs.open('F:\\nh.txt', 'a',encoding='utf-8')
    for key in words_dic.keys():
        if(len(key)>1):
            left_p=words_dic[key][1]/(words_dic[key[:1]][1]*words_dic[key[1:]][1])
            right_p=words_dic[key][1]/(words_dic[key[:-1]][1]*words_dic[key[-1:]][1])
            if(left_p<right_p):
                words_dic[key][2]=left_p
            else:
                words_dic[key][2]=right_p
            test.write('key: '+key+'\tleft_p: '+str(left_p)+'\tright_p: '+str(right_p)+'\n')
    test.close

def calc_free(word_dic):
    ci = codecs.open('F:\\free.txt','a',encoding = 'utf-8')
    for key in word_dic.keys():
        front_free = 0
        end_free = 0
        su = word_dic[key][0]
        for front in word_dic[key][4].keys():
            tmp = word_dic[key][4][front]/su
            front_free -= math.log(tmp)*tmp        
        for end in word_dic[key][5]:
            tmp = word_dic[key][5][end]/su
            end_free -= math.log(tmp)*tmp
            
        if(front_free < end_free):
            word_dic[key][3]=front_free
        else:
            word_dic[key][3]=end_free
        ci.write('key: '+key+'\tfr_free: '+str(front_free)+'\tb_free: '+str(end_free)+'\n')
    ci.close()
    return word_dic

def find_filter(split_new,key_freq=10,key_len=2,key_nh=50,free=0.5):
    key_words={}
    for key in split_new.keys():
        #print split_new[key][5]
        if( len(key)>=key_len 
            and split_new[key][0]>key_freq 
            and split_new[key][2]>key_nh 
            and split_new[key][3]>free
            ):
            key_words[key]=[split_new[key][0],
                            split_new[key][1],
                            split_new[key][2],
                            split_new[key][2]*split_new[key][3],
                            split_new[key][3]
                            ]
   
    return key_words

if __name__ == '__main__':
    words = read_file('F:\\民事案件例子')
    '''
    test = codecs.open('F:\\民事案件例子\\102-done.xml', 'r',encoding='utf-8')
    words = test.read()
    test.close()
    '''
    word_len=int(input("word_len"))   
    print ("splitting......")
    split=find_words(words,word_len)
    ci = codecs.open('F:\\split.txt','a',encoding = 'utf-8')
    for  key in split.keys():
        ci.write('key: '+key+'\tcount: '+str(split[key][0])+'\tfreq: '+str(split[key][1])+\
                 '\tfront: '+str(split[key][4])+'\tback: '+str(split[key][5])+'\n')
    ci.close()
    print('ok')
    del(words)
    gc.collect()
    print ("凝聚程度...")
    find_nh(split)
    print ("自由程度....")
    calc_free(split)
    ci = codecs.open('F:\\result.txt','a',encoding = 'utf-8')
    for  key in split.keys():
        ci.write('key: '+key+'\tcount: '+str(split[key][0])+'\tnh: '+str(split[key][2])+\
                 '\tfree: '+str(split[key][3])+'\n')
    ci.close()
    while True:
        freq=input("输入词语频率")
        nh=input("输入凝聚程度")
        free=input("输入自由程度")   
        split_new=find_filter(split,int(freq),2,int(nh),float(free))
        final_res=sorted(split_new.items(),key=lambda split_new:split_new[1][0])  
        i=1
        ci = codecs.open('F:\\finall_re.txt','a',encoding = 'utf-8')
        for item in final_res:
            print ("Key : " + item[0] + "\tTimes :" \
            + str(item[1][0])  + "\t\tNG:" \
            + str(item[1][2]) + "\tMut :" \
            + str(item[1][3]) + "\tFree: " \
            + str(item[1][4]))
            i+=1
            ci.write('key:'+item[0]+'\tcount: '+str(item[1][0])+'\tnh: '+str(item[1][2])+\
                 '\tfree '+str(item[1][4])+'\n')
        ci.close()

    
    
    
    
    
