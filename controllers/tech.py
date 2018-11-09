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
        data = ['北京市高新技术企业', '京津冀国家高新技术企业']
        return json.dumps(data)

class ResourceType:
    def POST(self):
        data = web.input()
        name = data.name
        if name.encode("utf-8") == "北京市高新技术企业":
            with open("/home/project/demo/controllers/"+name+".csv", "r") as f:
                line = f.readline()
                statList = []
                typeList = set()
                while line:
                    lineSplit = line.split(',')
                    cType = lineSplit[2]
                    #长度过长
                    if len(cType) >= 60:
                        cType = cType[:33] + "..."
                    typeList.add(cType)
                    line = f.readline()
                f.close()
                return json.dumps({"typeList":list(typeList),"statList":statList})
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
        people1 = {}
        #河北省-石家庄:1301
        result2 = {}
        people2 = {}
        #石家庄-长安区:130102
        result3 = {}
        people3 = {} 
        #先统计出各个地方的人数
        with open("/home/project/demo/controllers/people.csv", "r") as f:
            line = f.readline()
            while line:
                lineSplit = line.split(',')
                code3 = line.split(',')[-4].strip()
                code2 = code3[:4] + "00"
                code1 = code3[:2] + "0000"
                people = int(line.split(',')[-2].strip())
                people1[code1] = people1.get(code1, 0)
                people1[code1] = people1[code1] + people
                people2[code2] = people2.get(code2, 0)
                people2[code2] = people2[code2] + people
                people3[code3] = people3.get(code3, 0)
                people3[code3] = people3[code3] + people
                line = f.readline()

        #统计公司个数 
        with open("/home/project/demo/controllers/"+resource+".csv", "r") as f:
            line = f.readline()
            while line:
                if line.strip() == "":
                    break
                if resource.encode("utf-8") == "北京市高新技术企业":
                    code3 = line.split(',')[-2].strip()
                else:
                    code3 = line.split(',')[-4].strip()
                code2 = code3[:4] + "00"
                code1 = code3[:2] + "0000"
                #计数
                if action == "sum": 
                    result1[code1] = result1.get(code1, 0)
                    result1[code1] = result1[code1] + 1
                    result2[code2] = result2.get(code2, 0)
                    result2[code2] = result2[code2] + 1
                    result3[code3] = result3.get(code3, 0)
                    result3[code3] = result3[code3] + 1
                #人均效率
                elif action == "aver":
                    result1[code1] = result1.get(code1, 0)
                    result1[code1] = result1[code1] + 10000.0/people1[code1]
                    result2[code2] = result2.get(code2, 0)
                    result2[code2] = result2[code2] + 10000.0/people2[code2]
                    result3[code3] = result3.get(code3, 0)
                    result3[code3] = result3[code3] + 10000.0/people3[code3]
                line = f.readline()
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
