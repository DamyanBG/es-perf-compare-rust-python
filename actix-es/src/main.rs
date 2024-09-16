use std::{env, error::Error};

use dotenv::dotenv;

use actix_web::{get, web::{self, Data}, App, HttpResponse, HttpServer, Responder};
use elasticsearch::{auth::Credentials, http::{response::Response, transport::Transport}, Elasticsearch, GetParts, SearchParts};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

struct Config {
    api_key: String,
    api_key_id: String,
    cloud_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Product {
    ProductId: u32,
    Gender: String,
    SubCategory: String,
    ProductType: String,
    Colour: String,
    ProductTitle: String,
    Usage: String,
    ImageUrl: String,
    Price: f64,
}

struct ElSearch {
    client: Elasticsearch,
}

impl ElSearch {
    fn new_from_cloudhost(config: &Config) -> Self {
        let api_key = &config.api_key;
        let api_key_id = &config.api_key_id;
        let cloud_id = &config.cloud_id;

        let credentials = Credentials::ApiKey(api_key_id.to_string(), api_key.to_string());
        let transport = Transport::cloud(cloud_id, credentials).unwrap();

        let es_client = Elasticsearch::new(transport);

        ElSearch {
            client: es_client
        }
    }

    fn new_localhost() -> Self {
        let transport = Transport::single_node("http://localhost:9200").unwrap();

        let es_client = Elasticsearch::new(transport);

        ElSearch {
            client: es_client
        }
    }

    async fn add_document(&self, index_name: &str, body: &Value) -> Result<Response, Box<dyn Error>> {
        let response = self.client
            .index(elasticsearch::IndexParts::Index(index_name))
            .body(body)
            .send()
            .await?;
        Ok(response)
    }

    async fn query_all(&self, index_name: &str) -> Result<Response, Box<dyn Error>> {
        let query_body = json!({
            "query": {
                "match_all": {}
            }
        });

        let response = self.client
            .search(SearchParts::Index(&[index_name]))
            .body(query_body)
            .send()
            .await?;

        Ok(response)
    }

    async fn search(&self, index_name: &str, query_body: &Value) -> Result<Response, Box<dyn Error>> {
        let response = self.client
            .search(SearchParts::Index(&[index_name]))
            .body(query_body)
            .send()
            .await?;
        Ok(response)
    }

    async fn query_by_doc_id(&self, index_name: &str, id: &str) -> Result<Response, Box<dyn Error>> {
        let response = self.client
            .get(GetParts::IndexId(index_name, id))
            .send()
            .await?;

        Ok(response)
    }
}

#[get("/product/{id}")]
async fn get_product(es: web::Data<ElSearch>, id: web::Path<String>) -> impl Responder {
    let product_id = id.as_str();
    let query = json!({
        "query": {
            "match": {
                "ProductId": product_id
            }
        }
    });
    let response = es.search("products02", &query).await.unwrap();
    
    
    let resp_body = response.json::<Value>().await.unwrap();
    let hits = resp_body["hits"]["hits"].as_array().unwrap();
    let product: Product = serde_json::from_value(hits[0]["_source"].clone()).unwrap();

    HttpResponse::Ok().json(product)
}

#[get("/products_search/{search}")]
async fn get_search_products(es: web::Data<ElSearch>, search: web::Path<String>) -> impl Responder {
    let search_str = search.as_str();
    let query = json!({
        "query": {
            "match": {
                "ProductTitle": search_str
            }
        },
        "size": 2000
    });
    let response = es.search("products02", &query).await.unwrap();
    
    
    let resp_body = response.json::<Value>().await.unwrap();
 
    let mut products = Vec::new();
    for hit in resp_body["hits"]["hits"].as_array().unwrap() {

        let product: Product = serde_json::from_value(hit["_source"].clone()).unwrap();
        products.push(product);
    }

    HttpResponse::Ok().json(products)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();

    let cloud_id = env::var("CLOUD_ID").unwrap();
    let api_key = env::var("API_KEY").unwrap();
    let api_key_id = env::var("API_KEY_ID").unwrap();

    let config = Config {
        api_key,
        api_key_id,
        cloud_id
    };

    let es = ElSearch::new_from_cloudhost(&config);

    let app_data = Data::new(es);

    HttpServer::new(move || {
        App::new()
            .app_data(app_data.clone())
            .service(get_product)
            .service(get_search_products)
    })
    .bind(("127.0.0.1", 8080))?
    // .workers(4)
    .run()
    .await
}
