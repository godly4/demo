#coding: utf-8

import os
import re
#import dbf
import web
import math
import json
import pysal
import numpy as np
import shutil
import subprocess
from dbfpy.dbf import Dbf
from config.setting import render
from collections import defaultdict
#from match import match, fileMatch 

def getFileList(dirName='shp'):
    pwd = os.getcwd()
    shpDir = pwd + "/static/files/" + dirName
    fileList = os.listdir(shpDir)
    dbfList = []
    for f in fileList:
        if os.path.splitext(f)[1] == '.dbf':
            dbfList.append(os.path.splitext(f)[0])

    return dbfList

class Index:
    def GET(self):
        dbfList = getFileList()
        return render.index(dbfList)

class SpatialLocal:
    def GET(self):
        dbfList = getFileList()
        return render.spatialLocal(dbfList)

class GetisLocal:
    def GET(self):
        dbfList = getFileList()
        return render.getisLocal(dbfList)

class Reg:
    def GET(self):
        dbfList = getFileList()
        return render.regress(dbfList)

class SpatialGlobal:
    def GET(self):
        dbfList = getFileList()
        return render.spatialGlobal(dbfList)

class NetAnalysis:
    def GET(self):
        return render.netAnalysis()

class Entropy:
    def GET(self):
        dbfList = getFileList("xzpj/xxs")
        return render.entropy(dbfList)

class Lentropy:
    def GET(self):
        dbfList = getFileList("xzpj/qws")
        return render.lentropy(dbfList)

class SpIndex:
    def GET(self):
        dbfList = getFileList("xzpj/sp")
        return render.spIndex(dbfList)

class Parse:
    def POST(self):
        i = web.input()
        result = match(i.data)
        print result
        return json.dumps(result)

class Upload:
    def POST(self):
        i = web.input()
        result = fileMatch(i.data)
        return json.dumps(result)

class Column:
    def POST(self):
        i = web.input()
        dirName = "shp"
        if i.has_key('dirName'):
            dirName = i.dirName
        path = os.getcwd() + "/static/files/" + dirName + "/"+ i.name + ".dbf"
        db = pysal.open(path, "r")
        return json.dumps(db.header)

def delete(db, col):
    try:
        db.delete_fields(col)
    except:
        pass

class Regress:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        colY = i.colY.encode('utf-8')
        colX = i.colX.encode('utf-8')
        print colX
        # start execute
        path = os.getcwd() + "/static/files/shp/"+ shp + ".dbf"
        f = pysal.open(path, "r")
        y = np.array(f.by_col[colY]).astype(np.float)
        y.shape = (len(f.by_col[colY]), 1)
        X = []
        for elem in colX.split(','):
            X.append(f.by_col[elem])
        X = np.array(X).T
        X = X.astype(np.float)
        ols = pysal.spreg.ols.OLS(y, X)
        print ols.summary
        return json.dumps(ols.summary)

def getValue(lists, target):
    min = 99999999
    max = -99999999
    sum = 0.0
    for l in lists:
        if l < min:
            min = l
        if l > max:
            max = l
        sum = sum + l
    if target == "min":
        return min
    elif target == "max":
        return max
    else:
        return sum

class CalcEntropy:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        col = i.col
        path = os.getcwd() + "/static/files/xzpj/xxs/" + shp + ".dbf"
        f = pysal.open(path, "r")
        colData = {}
        #唯一值A
        dictA = {}
        minA = {}
        maxA = {}
        for c in col.split(','):
            colData[c] = f.by_col[c]
            minA[c] = getValue(colData[c], "min")
            maxA[c] = getValue(colData[c], "max")
        for c in colData.keys():
            dictA[c] = minA[c] / maxA[c] * 1.0
        #新指标
        newData = defaultdict(list)
        for c in colData.keys():
            for i in range(len(colData[c])):
                colData[c][i] = ((colData[c][i] - minA[c]) / (maxA[c] - minA[c]) * 1.0) * (1 - dictA[c]) + dictA[c]
                newData[c].append(colData[c][i])
        #唯一值B
        dictB = {}
        for c in colData.keys():
            dictB[c] = getValue(colData[c], "sum")
        #新标准指标C
        for c in colData.keys():
            for i in range(len(colData[c])):
                colData[c][i] = colData[c][i] * 1.0 / dictB[c]
                colData[c][i] = colData[c][i] * math.log(colData[c][i])
        # 数据K
        k = 1 / math.log(len(colData[colData.keys()[0]]))
        # hj
        dictHj = {}
        sumHj = 0
        for c in colData.keys():
            tmp = -1 * k * getValue(colData[c], "sum")
            dictHj[c] = 1 - tmp
            sumHj = sumHj + dictHj[c]
        # wj
        dictWj = {}
        for c in colData.keys():
            dictWj[c] = dictHj[c] / sumHj * 1.0
        # 新的e
        for c in colData.keys():
            for i in range(len(colData[c])):
                colData[c][i] = dictWj[c] * newData[c][i]
        # 生成新列
        newList = []
        for i in range(len(colData[colData.keys()[0]])):
            tmp = 0
            for c in colData.keys():
                tmp = tmp + colData[c][i]
            newList.append(tmp)
        print newList
        dbf =  Dbf(path, True) 
        dbfNew = Dbf("resultEntropy.dbf", new=True) 
        #add field
        for fldName in dbf.fieldNames:
            dbfNew.addField(
                (fldName, "C", 15)
            )
        dbfNew.addField(
            ("xxs", "C", 15),
        )
        #add data
        index = 0
        for rec in dbf:
            newRec = dbfNew.newRecord()
            for fldName in dbf.fieldNames:
                newRec[fldName] = rec[fldName]
            newRec["xxs"] = newList[index]
            index += 1
            newRec.store()
        dbf.close()
        dbfNew.close() 
        # 传输至118机器
        cmd = "scp resultEntropy.dbf Administrator@118.190.61.45:/C:/gisdata/" + shp + "/" + shp + ".dbf"
        subprocess.call(cmd, shell=True)
        os.remove("resultEntropy.dbf")
        return json.dumps("OK")

class Calc:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        col = i.col.encode('utf-8')
        # FOR download, mkdir 
        cmd = "rm -rf static/files/"+shp
        subprocess.call(cmd, shell=True)
        cmd = "rm -rf static/files/"+shp+".zip"
        subprocess.call(cmd, shell=True)
        os.chdir("static/files/")
        os.mkdir(shp)
        os.chdir(shp)
        cmd = "find ../shp/ -name "+shp+".* -exec cp {} . \;"
        subprocess.call(cmd,shell=True) 
        os.chdir("../../..")
        # start execute
        path = os.getcwd() + "/static/files/shp/"+ shp + ".dbf"
        print path
        f = pysal.open(path, "r")
        y = np.array(f.by_col[col]).astype(np.float)
        #w = pysal.open(pysal.examples.get_path("stl.gal")).read()
        w = pysal.open(os.getcwd() + "/static/files/shp/"+ shp + ".gal").read()
        np.random.seed(12345)
        # 计算全局Moran值
        mi = pysal.Moran(y, w, two_tailed=False)
        # 计算局部Moran值
        lm = pysal.Moran_Local(y, w, permutations=9999) 
        # 计算局部Getis值
        lg = pysal.esda.getisord.G_Local(y, w, permutations=9999) 
        result = "Moran I值：{0}，P值：{1}，Z值：{2}".format(mi.I, mi.p_norm, mi.z_norm)
        lm_cl = lm.q
        lm_I = lm.Is
        lm_P = lm.p_sim
        lm_Z = lm.z_sim
        lg_P = lg.p_sim
        lg_Z = lg.z_sim
        print lm_cl, lm_I, lm_P, lm_Z, lg_P, lg_Z
        #table = dbf.from_csv(csvfile="result.csv",field_names=header.split(','),to_disk=True)
        dbf =  Dbf(path, True) 
        dbfNew = Dbf("result.dbf", new=True) 
        #add field
        for fldName in dbf.fieldNames:
            dbfNew.addField(
                (fldName, "C", 15)
            )
        dbfNew.addField(
            ("Moran_CL", "C", 15),
            ("Moran_I", "C", 15),
            ("Moran_P", "C", 15),
            ("Moran_Z", "C", 15),
            ("Getis_P", "C", 15),
            ("Getis_Z", "C", 15),
        )
        #add data
        index = 0
        for rec in dbf:
            newRec = dbfNew.newRecord()
            for fldName in dbf.fieldNames:
                newRec[fldName] = rec[fldName]
            newRec["Moran_CL"] = lm_cl[index]
            newRec["Moran_I"] = lm_I[index]
            newRec["Moran_P"] = lm_P[index]
            newRec["Moran_Z"] = lm_Z[index]
            newRec["Getis_P"] = lg_P[index]
            newRec["Getis_Z"] = lg_Z[index]
            index += 1
            newRec.store()
        dbf.close()
        dbfNew.close() 
        # 传输至118机器
        cmd = "scp result.dbf Administrator@118.190.61.45:/C:/gisdata/" + shp + "/" + shp + ".dbf"
        subprocess.call(cmd, shell=True)
        # 开启压缩
        cmd = "mv -f result.dbf static/files/"+shp+"/"+shp+".dbf"
        subprocess.call(cmd, shell=True)
        shutil.make_archive("static/files/"+shp, "zip", root_dir="static/files/"+shp)
        return json.dumps(result)

class CalcLentropy:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        colX = i.colX
        colY = i.colY
        path = os.getcwd() + "/static/files/xzpj/qws/" + shp + ".dbf"
        f = pysal.open(path, "r")
        yX = np.array(f.by_col[colX]).astype(np.float)
        yY = np.array(f.by_col[colY]).astype(np.float)
        print yX, yY
        sumX = 0
        sumY = 0
        for i in range(len(yX)):
            sumX += yX[i]
            sumY += yY[i]
        fenMu = sumX * 1.0 / sumY 
        # 生成新列
        newList = []
        for i in range(len(yX)):
            tmp = yX[i] * 1.0 / yY[i]
            tmp = tmp / fenMu
            newList.append(tmp)
        print newList
        dbf =  Dbf(path, True) 
        dbfNew = Dbf("resultLentropy.dbf", new=True) 
        #add field
        for fldName in dbf.fieldNames:
            dbfNew.addField(
                (fldName, "C", 15)
            )
        dbfNew.addField(
            ("qws", "C", 15),
        )
        #add data
        index = 0
        for rec in dbf:
            newRec = dbfNew.newRecord()
            for fldName in dbf.fieldNames:
                newRec[fldName] = rec[fldName]
            newRec["qws"] = newList[index]
            index += 1
            newRec.store()
        dbf.close()
        dbfNew.close() 
        # 传输至118机器
        cmd = "scp resultLentropy.dbf Administrator@118.190.61.45:/C:/gisdata/" + shp + "/" + shp + ".dbf"
        subprocess.call(cmd, shell=True)
        os.remove("resultLentropy.dbf")
        return json.dumps("OK")


class CalcSp:
    def POST(self):
        dictDis = defaultdict(dict)
        yN = []
        with open("/home/project/demo/controllers/city.csv", "r") as f:
            line = f.readline().strip()
            while line:
                yN.append(line.strip())
                line = f.readline().strip()
        with open("/home/project/demo/controllers/distance.csv", "r") as f:
            line = f.readline().strip()
            while line:
                lineSplit = line.split(',')
                dis = lineSplit[-3]
                start = lineSplit[-2]
                end = lineSplit[-1]
                dictDis[start][end] = dis
                line = f.readline().strip()
        #print dictDis
        # 初始化距离矩阵
        i = web.input()
        shp = i.shp.encode('utf-8')
        col = i.col
        path = os.getcwd() + "/static/files/xzpj/sp/" + shp + ".dbf"
        f = pysal.open(path, "r")
        RDs = np.array(f.by_col[col]).astype(np.float)
        sumAll = 0.0
        for i in range(len(RDs)):
            sumAll = sumAll + RDs[i]
        percent = {}
        for i in range(len(RDs)):
            percent[yN[i]] = (RDs[i] * 1.0 / sumAll) * 1.0
        sp = 0
        for fi in range(len(RDs) - 1):
            for sec in range(fi+1, len(RDs)):
                start = yN[fi]
                end = yN[sec]
                perStart = (float)(percent[start])
                perEnd = (float) (percent[end])
                distance = (float)(dictDis[start][end])
                print start, end, dictDis[start][end]
                print perStart, perEnd
                sp = sp + (perStart * perEnd * distance)

        print sp
        return json.dumps(sp)
