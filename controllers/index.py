import web
import json
from config.setting import render
from match import match 

class Index:
    def GET(self):
        i = web.input()
        name = None
        if i.has_key("name"):
            name = i.name
        return render.demo(name)

class Parse:
    def POST(self):
        i = web.input()
        result = match(i.data)
        print result
        return json.dumps(result)
