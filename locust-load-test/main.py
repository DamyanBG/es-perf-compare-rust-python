from locust import HttpUser, TaskSet, task, between
import polars as pl
import random
from itertools import filterfalse


class UserBehavior(TaskSet):
    def on_start(self):
        self.token = None
        self.product_ids = self.load_product_ids()
        self.unique_words = self.load_product_words()

    def load_product_ids(self):
        df = pl.read_csv("fashion.csv")
        product_ids = df.select(pl.col("ProductId").unique()).to_series().to_list()
        return product_ids
    
    def load_product_words(self):
        df = pl.read_csv("fashion.csv")
        titles = df['ProductTitle']

        unique_words = set()
        for title in titles:
            words = title.split()
            filtered_words = list(filterfalse(lambda x: "/" in x, words))
            unique_words.update(filtered_words)
        
        return tuple(unique_words)

    @task
    def get_product_by_id(self):
        with self.client.rename_request("/product/[id]"):
            product_id = random.choice(self.product_ids)
            
            self.client.get(f"/product/{product_id}")

    @task
    def get_producsts_search(self):
        with self.client.rename_request("/products_search/[search]"):
            search_word = random.choice(self.unique_words)
            
            self.client.get(f"/products_search/{search_word}")
            

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"
