#coding: utf-8

import os
import re
#import dbf
import web
import json
import pysal
import numpy as np
import shutil
import subprocess
from dbfpy.dbf import Dbf
from config.setting import render
from match import match, fileMatch 

class Index:
    def GET(self):
        pwd = os.getcwd()
        shpDir = pwd + "/static/files/shp"
        fileList = os.listdir(shpDir)
        dbfList = []
        for f in fileList:
            if os.path.splitext(f)[1] == '.dbf':
                dbfList.append(os.path.splitext(f)[0])
        
        return render.demo(dbfList)

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
        path = os.getcwd() + "/static/files/shp/"+ i.name + ".dbf"
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
        y = np.array(f.by_col[colY])
        y.shape = (len(f.by_col[colY]), 1)
        X = []
        for elem in colX.split(','):
            X.append(f.by_col[elem])
        X = np.array(X).T
        ols = pysal.spreg.ols.OLS(y, X)
        print ols.summary
        return json.dumps(ols.summary)

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
        y = np.array(f.by_col[col])
        #w = pysal.open(pysal.examples.get_path("stl.gal")).read()
        w = pysal.open(os.getcwd() + "/static/files/shp/"+ shp + ".gal").read()
        np.random.seed(12345)
        mi = pysal.Moran(y, w, two_tailed=False)
        lm = pysal.Moran_Local(y, w, permutations=9999) 
        result = "Moran I值：{0}，P值：{1}，Z值：{2}".format(mi.I, mi.p_norm, mi.z_norm)
        lm_cl = lm.q
        lm_I = lm.Is
        lm_P = lm.p_sim
        lm_Z = lm.z_sim
        print lm_cl, lm_I, lm_P, lm_Z
        #table = dbf.from_csv(csvfile="result.csv",field_names=header.split(','),to_disk=True)
        dbf =  Dbf(path, True) 
        dbfNew = Dbf("result.dbf", new=True) 
        #add field
        for fldName in dbf.fieldNames:
            dbfNew.addField(
                (fldName, "C", 15)
            )
        dbfNew.addField(
            ("CL", "C", 15),
            ("I", "C", 15),
            ("P", "C", 15),
            ("Z", "C", 15)
        )
        #add data
        index = 0
        for rec in dbf:
            newRec = dbfNew.newRecord()
            for fldName in dbf.fieldNames:
                newRec[fldName] = rec[fldName]
            newRec["CL"] = lm_cl[index]
            newRec["I"] = lm_I[index]
            newRec["P"] = lm_P[index]
            newRec["Z"] = lm_Z[index]
            index += 1
            newRec.store()
        dbf.close()
        dbfNew.close() 
        # 开启压缩
        cmd = "mv -f result.dbf static/files/"+shp+"/"+shp+".dbf"
        subprocess.call(cmd, shell=True)
        shutil.make_archive("static/files/"+shp, "zip", root_dir="static/files/"+shp)
        return json.dumps(result)
