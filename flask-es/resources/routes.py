from resources.es_resources import ProductById, ProductsSearch

routes = (
    (ProductById, "/product/<int:product_id>"),
    (ProductsSearch, "/products_search/<string:search>"),
)
