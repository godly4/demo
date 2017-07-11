#coding: utf-8

import os
import re
#import dbf
import web
import json
import pysal
import numpy as np
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

class Calc:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        col = i.col.encode('utf-8')
        path = os.getcwd() + "/static/files/shp/"+ shp + ".dbf"
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
        #添加cl, i, p, z列
        #with dbf.Table(path) as db:
        #    dbf.export(db, 'tmp.csv')
        #header = ""
        #with open('tmp.csv', 'r') as f:
        #    with open("result.csv", "w") as fw:
        #        index = 0
        #        line = f.readline().strip()
        #        line = line + ',CL,I,P,Z'
        #        header = line.replace('"', '')
        #        #fw.write(header+'\n')
        #        line = f.readline().strip()
        #        while line:
        #            line = line + ',{0},{1},{2},{3}'.format(lm_cl[index], lm_I[index], lm_P[index], lm_Z[index])
        #            fw.write(line.replace('"', '')+'\n')
        #            index += 1
        #            line = f.readline().strip()
        #os.remove('tmp.csv')
        ##table = dbf.from_csv(csvfile="result.csv",to_disk=True,field_names=header.split(','))
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
        #db.delete_fields('cl')
        #db.delete_fields('i')
        #db.delete_fields('p')
        #db.delete_fields('z')
        #db.add_fields('CL N(128,3)')
        #db.add_fields('I N(128,3)')
        #db.add_fields('P N(128,3)')
        #db.add_fields('Z N(128,3)')
        #for record in db:
        #    record.CL = lm_cl[index]
        #    record.I = lm_I[index]
        #    record.P = lm_P[index]
        #    record.Z = lm_Z[index]
        #    index += 1
        #db.pack()
        return json.dumps(result)
