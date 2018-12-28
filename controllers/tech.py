#coding: utf-8

import os
import re
#import dbf
import web
import uuid
import math
import time
import json
import pysal
import numpy as np
import shutil
import subprocess
import urllib2
import collections
from dbfpy.dbf import Dbf
from config.setting import render
from collections import defaultdict
#from match import match, fileMatch 

columnMap = {"Y":"技术合同成交额(亿元)","X1":"专利申请数","X2":"专利授权数","x3":"地方财政科技拨款(万元)","x4":"地方财政教育拨款(万元)",\
"x5":"R&D经费支出(万元)","x6":"实际利用外商直接投资额(万美元)","x7":"常住人口(万人)","x8":"R&D研究人员数"}

class SynergyData:
    def GET(self):
        data = {"company":["京津冀企业数据"],"industry":["京津冀科研机构数据"]}
        return json.dumps(data)

class RegressData:
    def GET(self):
        data = ['2016']
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
        data = ['北京市高新技术企业']
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

class Synergy:
    def POST(self):
        data = web.input()
        company = data.company
        industry = data.industry
        codeSet = []
        #北京、天津统计到区--全部六位代码
        #河北统计到地级市--统计前四位代码
        #企业合并数据
        #cFile = "/home/project/demo/controllers/" + company + ".csv"
        cFile = "/home/project/demo/static/files/高新技术企业-电子信息技术-京津冀geocode.csv" 
        cResult = {}
        cMin = 99999999
        cMax = 0
        f = open(cFile, "r")
        line = f.readline()
        while line:
            lineSplit = line.split(',')
            if len(lineSplit) >= 2 and len(lineSplit[-2]) == 6:
                gdcode = str(lineSplit[-2])
                if gdcode[:2] == "13":
                    gdcode = gdcode[:4] + "00"
                codeSet.append(gdcode)
                cResult[gdcode] = cResult.get(gdcode, 0)
                cResult[gdcode] = cResult[gdcode] + 1
            line = f.readline()
        f.close()
        for gdcode in codeSet:
            if cResult[gdcode] > cMax:
                cMax = cResult[gdcode]
            if cResult[gdcode] < cMin:
                cMin = cResult[gdcode]
        #科研机构合并数据
        #iFile = "/home/project/demo/controllers/" + industry + ".csv"
        iFile = "/home/project/demo/static/files/科研院所-电子信息技术-京津冀geocode.csv"
        iResult = {}
        iMin = 999999999
        iMax = 0
        f = open(iFile, "r")
        line = f.readline()
        while line:
            lineSplit = line.split(',')
            if len(lineSplit) >= 2 and len(lineSplit[-2]) == 6:
                gdcode = str(lineSplit[-2])
                if gdcode[:2] == "13":
                    gdcode = gdcode[:4] + "00"
                codeSet.append(gdcode)
                iResult[gdcode] = iResult.get(gdcode, 0)
                iResult[gdcode] = iResult[gdcode] + 1
            line = f.readline()
        f.close()
        for gdcode in codeSet:
            if gdcode in iResult and iResult[gdcode] > iMax:
                iMax = iResult[gdcode]
            if gdcode in iResult and iResult[gdcode] < iMin:
                iMin = iResult[gdcode]
        codeSet = set(codeSet)
        codeSet = sorted(codeSet)
        #测试数据
        retDict = {}
        retDict["table"] = collections.OrderedDict()
        f = open("/home/project/demo/controllers/map.csv", "r")
        line = f.readline()
        dd = {}
        while line:
            lineSplit = line.split()
            dd[lineSplit[0]] = lineSplit[1]
            line = f.readline()
        f.close()
        for gdcode in codeSet:
            if gdcode == "gdcode":
                continue
            district = dd.get(gdcode) 
            retDict["table"][district] = retDict["table"].get(district,[])
            cValue = cResult.get(gdcode, cMin)
            iValue = iResult.get(gdcode, iMin)
            cTmp = (cValue - cMin) * 1.0 / (cMax - cMin)
            iTmp = (iValue - iMin) * 1.0 / (iMax - iMin)
            print "{},{},{}".format(gdcode, iTmp, cTmp)
            tValue = 0.8 * iTmp + 0.2 * cTmp
            retDict["table"][district].append(cResult.get(gdcode,0))
            retDict["table"][district].append(iResult.get(gdcode,0))
            CRet = round(2 * math.sqrt((cTmp * iTmp / ((cTmp + iTmp) * (cTmp + iTmp)))), 2)
            retDict["table"][district].append(CRet)
            DRet = round(math.sqrt(CRet * tValue), 2)
            retDict["table"][district].append(DRet)
            if DRet >= 0 and DRet <= 0.2:
                retDict["table"][district].append("低度协调")
            elif DRet > 0.2 and DRet <= 0.5:
                retDict["table"][district].append("中度协调")
            else:
                retDict["table"][district].append("高度协调")
        return json.dumps(retDict)

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
        area1 = {}
        #河北省-石家庄:1301
        result2 = {}
        people2 = {}
        area2 = {}
        #石家庄-长安区:130102
        result3 = {}
        people3 = {} 
        area3 = {}
        #先统计出各个地方的人数
        with open("/home/project/demo/controllers/people.csv", "r") as f:
            line = f.readline()
            while line:
                lineSplit = line.split(',')
                code3 = line.split(',')[-4].strip()
                code2 = code3[:4] + "00"
                code1 = code3[:2] + "0000"
                people = int(line.split(',')[-2].strip())
                area  = int(line.split(',')[-2].strip())/float(line.split(',')[-1].strip())
                people1[code1] = people1.get(code1, 0)
                people1[code1] = people1[code1] + people
                area1[code1]    = area1.get(code1, 0)
                area1[code1]   = area1[code1] + area
                people2[code2] = people2.get(code2, 0)
                people2[code2] = people2[code2] + people
                area2[code2]   = area2.get(code2, 0)
                area2[code2]   = area2[code2] + area
                people3[code3] = people3.get(code3, 0)
                people3[code3] = people3[code3] + people
                area3[code3]   = area3.get(code3, 0)
                area3[code3]   = area3[code3] + area
                line = f.readline()

        #统计公司个数 
        with open("/home/project/demo/controllers/"+resource+".csv", "r") as f:
            line = f.readline()
            while line:
                if line.strip() == "":
                    break
                code3 = line.split(',')[-2].strip()
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
                #面积效率
                elif action == "area":
                    print result1.get(code1)
                    result1[code1] = result1.get(code1, 0)
                    result1[code1] = result1[code1] + 10000.0/area1[code1]
                    result2[code2] = result2.get(code2, 0)
                    result2[code2] = result2[code2] + 10000.0/area2[code2]
                    result3[code3] = result3.get(code3, 0)
                    result3[code3] = result3[code3] + 10000.0/area3[code3]
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

class RegressUpload:
    def POST(self):
        x = web.input(myfile={})
        name = str(uuid.uuid1())
        fileName = "/home/project/demo/controllers/"+name+".csv"
        if 'myfile' in x: # to check if the file-object is created
            content = x.myfile.file.read() # writes the uploaded file to the newly created file.
            f = open(fileName, "w")
            f.write(content)
            f.close()
        return name
