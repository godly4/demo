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
        data = ['学校']
        return json.dumps(data)

class ResourceType:
    def POST(self):
        data = web.input()
        name = data.name
        with open("/home/project/demo/controllers/school.csv", "r") as f:
            line = f.readline()
            lineSplit = line.split('^_^')
            index = lineSplit.index('学校属性')
            indexStat = lineSplit.index('高校名称')
            statList = lineSplit[indexStat+1:-1]
            typeList = set()
            while line:
                line = f.readline()
                lineSplit = line.split('^_^')
                if len(lineSplit) > index:
                    typeList.add(lineSplit[index])
            f.close()
            return json.dumps({"typeList":list(typeList),"statList":statList})
