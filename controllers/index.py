import web
import json
from config.setting import render
from match import match, fileMatch 

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

class Upload:
    def POST(self):
        i = web.input()
        result = fileMatch(i.data)
        return json.dumps(result)
