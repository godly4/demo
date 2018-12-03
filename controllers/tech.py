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

columnMap = {"Y":"技术合同成交额(亿元)","X1":"专利申请数","X2":"专利授权数","x3":"地方财政科技拨款(万元)","x4":"地方财政教育拨款(万元)",\
"x5":"R&D经费支出(万元)","x6":"实际利用外商直接投资额(万美元)","x7":"常住人口(万人)","x8":"R&D研究人员数"}

class RegressData:
    def GET(self):
        data = ['2013', '2014', '2015', '2016']
        return json.dumps(data)

class RegressColumn:
    def POST(self):
        data = web.input()
        dirName = "shp"
        path = os.getcwd() + "/static/files/" + dirName + "/"+ "olsdata" + ".dbf"
        db = pysal.open(path, "r")
        heads = db.header
        ret = []
        for i in range(len(heads)):
            if heads[i].startswith('Y') or heads[i].startswith('y') \
                or heads[i].startswith('x') or heads[i].startswith('X'):
                ret.append(heads[i]+"_"+columnMap[heads[i]].decode("utf8"))
        return json.dumps(ret)

class RegressAnalysis:
    def POST(self):
        data = web.input()
        name = data.name
        colX = data.X
        colY = data.Y
        # start execute
        path = os.getcwd() + "/static/files/shp/"+ "olsdata" + ".dbf"
        f = pysal.open(path, "r")
        y = np.array(f.by_col[colY]).astype(np.float)
        y.shape = (len(f.by_col[colY]), 1)
        X = []
        #加载地址
        district = []
        district.append(f.by_col["gdcode"])
        for elem in colX.split(','):
            X.append(f.by_col[elem])
        #print X
        X = np.array(X).T
        X = X.astype(np.float)
        #print X
        #取对数,符合柯布—道格拉斯生产函数格式
        logY = np.log(y)
        logX = np.log(X)
        ols = pysal.spreg.ols.OLS(logY, logX)
        #print y
        betas = ols.betas
        retDict = {}
        result = "logY = "
        #参数列表
        factors = []
        for i in range(len(colX.split(','))):
            result += "(" + str(betas[i+1][0]) + ")" + " * " + "logX" + str(i+1) + " + "
            factors.append(betas[i+1][0])
        result = result[:-2]
        if str(betas[0][0])[0] == "-":
            result += " - " + str(betas[0][0])[1:]
        else:
            result += " + " + str(betas[0][0])
        factors.append(betas[0][0])
        retDict["result"] = result
        retDict["table"] = {}
        retDict["betas"] = factors
        #读取编号
        with open("/home/project/demo/controllers/map.csv","r") as f:
            data = f.read()
        dataSplit = data.split('\n')
        for i in range(len(X)):
            tmp = []
            tmp.append(y[i][0])
            for j in range(len(X[i])):
                tmp.append(X[i][j])
            for d in dataSplit:
                if district[0][i] == d.split(" ")[0]: 
                    retDict["table"][d.split(" ")[1]] = tmp
                    break
        print retDict 
        return json.dumps(retDict)
        
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
