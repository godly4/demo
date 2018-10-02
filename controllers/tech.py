#coding: utf-8

import os
import re
#import dbf
import web
import math
import time
import json
import pysal
import numpy as np
import shutil
import subprocess
import urllib2
from dbfpy.dbf import Dbf
from config.setting import render
from collections import defaultdict
#from match import match, fileMatch 

class RegressData:
    def GET(self):
        data = ['2013', '2014', '2015', '2016']
        return json.dumps(data)

class RegressColumn:
    def POST(self):
        data = web.input()
        column = ['地区','论文','获奖','科研院所','大学','企业研发机构','研发经费','国家补助']
        return json.dumps(column)

class RegressAnalysis:
    def POST(self):
        data = web.input()
        name = data.name
        X = name.X
        Y = name.Y
        
class ResourceList:
    def GET(self):
        data = ['高新技术企业']
        return json.dumps(data)

class ResourceType:
    def POST(self):
        data = web.input()
        name = data.name
        #with open("/home/project/demo/controllers/company.csv", "r") as f:
        #    line = f.readline()
        #    lineSplit = line.split('^_^')
        #    index = lineSplit.index('学校属性')
        #    indexStat = lineSplit.index('高校名称')
        #    statList = lineSplit[indexStat+1:-1]
        #    typeList = set()
        #    while line:
        #        line = f.readline()
        #        lineSplit = line.split('^_^')
        #        if len(lineSplit) > index:
        #            typeList.add(lineSplit[index])
        #    f.close()
        #    return json.dumps({"typeList":list(typeList),"statList":statList})
        return json.dumps({"typeList":[],"statList":[]})

def takeSecond(elem):
    return elem["value"]

def process(result):
    ret = []
    with open("/home/project/demo/controllers/map.csv","r") as f:
        data = f.read()
    dataSplit = data.split('\n')
    for k,v in result.items():
        for d in dataSplit:
            if k == d.split(" ")[0]:
                retDict = {}
                retDict["name"] = d.split(" ")[1]
                retDict["value"] = v
                ret.append(retDict)

    ret.sort(key=takeSecond,reverse=True)
    return ret

class Aggregation:
    def GET(self):
        data = web.input()
        year = data.year
        resource = data.resource
        resourceType = data.resourceType.encode('utf-8')
        action = data.action
        column = data.column.encode('utf-8')
        zoom = float(data.zoom)
        #河北省:13
        result1 = {}
        #河北省-石家庄:1301
        result2 = {}
        #石家庄-长安区:130102
        result3 = {}
        with open("/home/project/demo/controllers/school.csv", "r") as f:
            line = f.readline()
            lineSplit = line.split('^_^')
            index = lineSplit.index('学校属性')
            try:
                indexColumn = lineSplit.index(column)
            except:
                indexColumn = 1
            while line:
                line = f.readline()
                if line.strip() == "":
                    break
                code3 = line.split('^_^')[5]
                code2 = code3[:4] + "00"
                code1 = code3[:2] + "0000"
                lineType = line.split('^_^')[index]
                try:
                    lineColumn = int(line.split('^_^')[indexColumn])
                except:
                    lineColumn = 0
                if resourceType == lineType:
                    #计数
                    if action == "sum": 
                        result1[code1] = result1.get(code1, 0)
                        result1[code1] = result1[code1] + 1
                        result2[code2] = result2.get(code2, 0)
                        result2[code2] = result2[code2] + 1
                        result3[code3] = result3.get(code3, 0)
                        result3[code3] = result3[code3] + 1
                    #统计
                    elif action == "stat":
                        result1[code1] = result1.get(code1, 0)
                        result1[code1] = result1[code1] + int(lineColumn)
                        result2[code2] = result2.get(code2, 0)
                        result2[code2] = result2[code2] + int(lineColumn)
                        result3[code3] = result3.get(code3, 0)
                        result3[code3] = result3[code3] + int(lineColumn)
        result = []
        #北京市、河北省
        if zoom < 8:
            print result1
            result = process(result1)    
        elif zoom >= 8 and zoom < 11:
            print result3
            result = process(result3) 
        else:
            print result3
            result = process(result3)    
        return json.dumps(result)

class Test:
    def GET(self):
        print "start"
        time.sleep(20)
        print "end"
