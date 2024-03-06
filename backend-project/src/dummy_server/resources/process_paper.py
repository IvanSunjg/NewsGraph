"""
Module Description: 
Process
"""

import os
import json
from flask_restful import Resource


class DataResource(Resource):
    """paper resource."""
    paper_root = os.path.join(".", "data/paper")

    def get(self, name):

        path_name = os.path.join(self.paper_root, f"{name}.json")
        data = json.load(path_name)

        return data.to_dict(orient="records")