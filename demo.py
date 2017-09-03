import web

urls = (
    '/index', 'controllers.index.Index',
    '/classify', 'controllers.index.Parse',
    '/upload', 'controllers.index.Upload',
    '/column', 'controllers.index.Column',
    '/calculate', 'controllers.index.Calc',
    '/regress', 'controllers.index.Regress',
    '/spatialLocal', 'controllers.index.SpatialLocal',
    '/spatialGlobal', 'controllers.index.SpatialGlobal',
    '/getisLocal', 'controllers.index.GetisLocal',
    '/netAnalysis', 'controllers.index.NetAnalysis',
    '/entropy', 'controllers.index.Entropy',
    '/spIndex', 'controllers.index.SpIndex',
    '/calc_entropy', 'controllers.index.CalcEntropy',
)

render = web.template.render("templates/")

app = web.application(urls, globals())
application = app.wsgifunc()
