from fastapi import APIRouter

from search import es, products_index_name

api_router = APIRouter()


@api_router.get("/product/{product_id}")
async def get_product_by_id(product_id: int):
    query = {
        "query": {
            "match": {
                "ProductId": product_id
            }
        }
    }

    result = await es.search(products_index_name, body=query)
    # print(result)
    hits = result["hits"]["hits"]
    if not hits:
        return f"No product with id {product_id}"
    response = hits[0]["_source"]
    return response


@api_router.get("/products_search/{search}")
async def get_product_by_id(search: str):
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

    result = await es.search(products_index_name, body=query)
    # print(result)
    hits = result["hits"]["hits"]
    if not hits:
        return f"No products found for {search}"
    response = [product["_source"] for product in hits]
    return response
