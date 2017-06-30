import web

urls = (
    '/', 'controllers.index.Index',
    '/classify', 'controllers.index.Parse',
)

render = web.template.render("templates/")

app = web.application(urls, globals())
application = app.wsgifunc()
