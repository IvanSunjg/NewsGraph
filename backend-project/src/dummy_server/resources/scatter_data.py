import os
import pandas as pd

from flask_restful import Resource
from sklearn.cluster import KMeans


class DatasetResource(Resource):
    """dataset resource."""
    data_root = os.path.join(".", "data")

    def get(self, name):
        path_name = os.path.join(self.data_root, f"dataset_{name}.csv")
        data = pd.read_csv(path_name)

        # process the data, e.g. find the clusters
        kmeans = KMeans(n_clusters=2, n_init=10, random_state=0).fit(data)
        labels = kmeans.labels_.tolist()
        
        # Add cluster to data
        data["cluster"] = labels

        # Convert to dictionary
        return data.to_dict(orient="records")
