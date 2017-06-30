#!/usr/bin/env python
#coding: utf-8
#author: dlgao

import os
import jieba
from gensim.models import word2vec
from gensim import models

classADict = {}
classBDict = {}
classCDict = {}
classDDict = {}
stopwordset = set()

def getClassDict(name):
    lastId = ""
    with open(name,"r") as f:
        line = f.readline().strip()
        while line:
            lineSplit = line.split(',')
            id = str(lineSplit[0])
            if id:
                desc = str(lineSplit[1]).strip()
                #大编号A,B..
                if len(id) == 1:
                    lastId = id
                    classADict[id] = desc
                elif len(id) == 2:
                    classBDict[lastId] = classBDict.get(lastId, {})
                    classBDict[lastId][id] = desc
                elif len(id) == 3:
                    classCDict[id] = desc
                elif len(id) == 4:
                    classDDict[id] = desc
                else:
                    print("Wrong: " + id)
            line = f.readline().strip()

def getMatchResult(param1, param2):
    paramList1 = jieba.cut(param1, cut_all=False)
    paramList2 = jieba.cut(param2, cut_all=False)
    result = 0
    for word1 in paramList1:
        if word1 in stopwordset:
            continue
        for word2 in paramList2:
            if word2 in stopwordset:
                continue
            try:
                result += model.similarity(word1, word2)
            except:
                continue

    return result

def getAll(id):
    if str(id) == "0":
        return ""
    ret = ""
    ret += "{0}({1}),".format(id, classDDict[id])
    idc = id[:-1]
    if idc in classCDict.keys():
        ret += "{0}({1}),".format(idc, classCDict[idc])
    else:
        ret += "无(无),"
    idb = id[:-2]
    ida = ""
    sign = False
    for key,value in classBDict.items():
        for k,v in value.items():
            if k == idb:
                ida = key
                ret += "{0}({1}),".format(idb, classBDict[ida][idb])
                sign = True
                break
    if not sign:
        ret += "无(无),"

    if ida:
        ret += "{0}({1})".format(ida, classADict[ida])
    else:
        ret += "无(无)"

    return ret

def match(param):
    max = 0
    maxId = 0
    for key,value in classDDict.items():
        sim = getMatchResult(value, param)
        if sim > max:
            max = sim
            maxId = key
    
    return getAll(maxId)

def fileMatch(param):
    pwd = os.getcwd()
    fw = open(pwd+"/static/files/result.csv", "w")
    param = param.replace('\r\n','\n').split('\n')
    while param:
        line = param.pop()
        biz = line.split(',')[-16]
        name = biz.split(';')[0].split('；')[0].split('。')[0].split('、')[0].split('：')[0].split('（')[0].split('(')[0].split('，')[0]
        max = 0
        maxId = 0
        for key,value in classDDict.items():
            sim = getMatchResult(value, name)
            if sim > max:
                max = sim
                maxId = key

        fw.write(line + getAll(maxId) + '\n')

    fw.close()
    return "result.csv"    

with open('controllers/jieba_dict/stopwords.txt','r') as sw:
    for line in sw:
        stopwordset.add(line.strip('\n'))
getClassDict("controllers/classify.csv")
jieba.set_dictionary('controllers/jieba_dict/dict.txt.big')
model = models.Word2Vec.load('controllers/med250.model.bin')
#match("计算机", model)
