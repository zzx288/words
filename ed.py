#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os
import codecs

def find_words(words):
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
        if(words[i+1] in unused_words or words[i+1] in unused_english):
            continue
        if words[i:i+2] in split_words:
            split_words[words[i:i+2]][0]+=1
            split_words[words[i:i+2]][1]=float(split_words[words[i:i+2]][0])/float(len_deal)
        else:
            split_words[words[i:i+2]]=[1,1/float(len_deal)]
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
    words = read_file('F:\\cs')
    '''
    test = codecs.open('F:\\760.xml', 'r',encoding='utf-8')
    words = test.read()
    test.close()
    '''
    print ("splitting......")
    split=find_words(words)
    ci = codecs.open('F:\\result.txt','a',encoding = 'utf-8')
    for  key in split.keys():
        ci.write('('+key[0]+','+key[1]+','+str(split[key][1])+')\r\n')
    ci.close
    print("ok")
