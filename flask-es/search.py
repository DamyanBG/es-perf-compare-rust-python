from pprint import pprint

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from config import CLOUD_ID, API_KEY, ES_HOST, API_KEY_ID

ELASTIC_HOST = "http://localhost:9200"

products_index_name = "products02"

products_mapping = {
    "mappings": {
        "properties": {
            "ProductId": {"type": "long"},
            "Gender": {"type": "keyword"},
            "SubCategory": {"type": "keyword"},
            "ProductType": {"type": "keyword"},
            "Colour": {"type": "keyword"},
            "Usage": {"type": "keyword"},
            "ProductTitle": {"type": "text", "analyzer": "standard"},
            "ImageUrl": {"type": "keyword"},
            "Price": {"type": "float"},
        }
    }
}



mapping = {
    "mappings": {
        "properties": {
            "pin": {"properties": {"location": {"type": "geo_point"}}},
        }
    }
}


class Search:
    _connected: bool = True

    def __init__(self) -> None:
        try:
            # self.es = Elasticsearch(ELASTIC_HOST)
            self.es = Elasticsearch(cloud_id=CLOUD_ID, api_key=(API_KEY, API_KEY_ID))
            client_info = self.es.info()
            print("Connected to Elasticsearch!")
            pprint(client_info.body)
        except ConnectionError:
            self._connected = False
            print("Can't connect")

    def create_index(self):
        self.es.indices.delete(index="real_estate_homes", ignore_unavailable=True)
        self.es.indices.create(index="real_estate_homes", body=mapping)

    def insert_document(self, document):
        return self.es.index(index="real_estate_homes", body=document)

    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({"index": {"_index": "real_estate_homes"}})
            operations.append(document)
        return self.es.bulk(operations=operations)

    def search(self, index_name: str, **query_args):
        if self._connected:
            return self.es.search(index=index_name, **query_args)
        return None


es = Search()