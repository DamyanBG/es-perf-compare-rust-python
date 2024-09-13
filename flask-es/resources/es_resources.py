from flask_restful import Resource

from search import es, products_index_name


class ProductById(Resource):
    def get(self, product_id):
        query = {"query": {"match": {"ProductId": product_id}}}

        result = es.search(products_index_name, body=query)
        # print(result)
        hits = result["hits"]["hits"]
        if not hits:
            return f"No product with id {product_id}"
        response = hits[0]["_source"]
        print(response)
        return response


class ProductsSearch(Resource):
    def get(self, search):
        query = {
            "query": {
                "match": {
                    "ProductTitle": search
                }
            },
            "size": 2000
        }
        # query = {
        #     "query": {
        #         "wildcard": {
        #             "ProductTitle": f"*{search}*"
        #         }
        #     }
        # }

        result = es.search(products_index_name, body=query)
        # print(result)
        hits = result["hits"]["hits"]
        if not hits:
            return f"No products found for {search}"
        response = [product["_source"] for product in hits]
        print(response)
        return response
