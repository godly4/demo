#coding: utf-8

import os
import re
import web
import json
import pysal
import numpy as np
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

class Calc:
    def POST(self):
        i = web.input()
        shp = i.shp.encode('utf-8')
        col = i.col.encode('utf-8')
        path = os.getcwd() + "/static/files/shp/"+ shp + ".dbf"
        f = pysal.open(path, "r")
        y = np.array(f.by_col[col])
        w = pysal.open(pysal.examples.get_path("stl.gal")).read()
        mi = pysal.Moran(y, w, two_tailed=False)
        return json.dumps("%.3f"%mi.I, "%.5f"%mi.p_norm, "%.5f"%mi.z_norm)
