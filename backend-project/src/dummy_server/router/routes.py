from flask_restful import Api
import dummy_server.resources as res

API = "/api/v1/"  # optional string


def add_routes(app):
    api = Api(app)

    api.add_resource(res.template_data.TemplateResource, API + "template_data")
    api.add_resource(res.template_data.GraphResource, API + "graph_data")
    api.add_resource(res.template_data.GlyphResource, API + "glyph_data")

    return api
