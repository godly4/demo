import web

urls = (
    '/index', 'controllers.index.Index',
    '/classify', 'controllers.index.Parse',
    '/upload', 'controllers.index.Upload',
    '/column', 'controllers.index.Column',
    '/calculate', 'controllers.index.Calc',
    '/regress', 'controllers.index.Regress',
    '/spatialLocal', 'controllers.index.SpatialLocal',
)

render = web.template.render("templates/")

app = web.application(urls, globals())
application = app.wsgifunc()
