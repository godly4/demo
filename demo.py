import web

urls = (
    '/', 'controllers.index.Index',
    '/classify', 'controllers.index.Parse',
    '/upload', 'controllers.index.Upload',
    '/column', 'controllers.index.Column',
    '/calculate', 'controllers.index.Calc',
)

render = web.template.render("templates/")

app = web.application(urls, globals())
application = app.wsgifunc()
