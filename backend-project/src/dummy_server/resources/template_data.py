import os
import json
from flask_restful import Resource


class TemplateResource(Resource):
    """dataset resource."""
    data_root = os.path.join(".", "data")

    def get(self):
        path_name = os.path.join(self.data_root, "articles/template", "articles_with_links.json")

        with open(path_name, encoding='utf-8') as fp:
            article2links = json.load(fp)

        return article2links

class GraphResource(Resource):
    """dataset resource."""
    data_root = os.path.join(".", "data")

    def get(self):
        path_name = os.path.join(self.data_root, "articles/template", "link_graphs.json")

        with open(path_name, encoding='utf-8') as fp:
            link_graphs = json.load(fp)

        return link_graphs

class GlyphResource(Resource):
    """dataset resource."""
    data_root = os.path.join(".", "data")

    def get(self):
        path_name = os.path.join(self.data_root, "articles/template", "claims_positions.json")

        with open(path_name, encoding='utf-8') as fp:
            link_graphs = json.load(fp)

        return link_graphs
