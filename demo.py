import web

urls = (
    '/index', 'controllers.index.Index',
    '/classify', 'controllers.index.Parse',
    '/upload', 'controllers.index.Upload',
    '/column', 'controllers.index.Column',
    '/calculate', 'controllers.index.Calc',
    '/reg', 'controllers.index.Reg',
    '/regress', 'controllers.index.Regress',
    '/spatialLocal', 'controllers.index.SpatialLocal',
    '/spatialGlobal', 'controllers.index.SpatialGlobal',
    '/getisLocal', 'controllers.index.GetisLocal',
    '/netAnalysis', 'controllers.index.NetAnalysis',
    '/entropy', 'controllers.index.Entropy',
    '/lentropy', 'controllers.index.Lentropy',
    '/spIndex', 'controllers.index.SpIndex',
    '/calc_entropy', 'controllers.index.CalcEntropy',
    '/calc_lentropy', 'controllers.index.CalcLentropy',
    '/calc_sp', 'controllers.index.CalcSp',
    '/regressData', 'controllers.tech.RegressData',
    '/regressColumn', 'controllers.tech.RegressColumn',
    '/regressAnalysis', 'controllers.tech.RegressAnalysis',
    '/resourceList', 'controllers.tech.ResourceList',
    '/resourceType', 'controllers.tech.ResourceType',
    '/aggregation', 'controllers.tech.Aggregation',
)

render = web.template.render("templates/")

app = web.application(urls, globals())
application = app.wsgifunc()
