from locust import HttpUser, TaskSet, task, between
import polars as pl
import time


class UserBehavior(TaskSet):
    def on_start(self):
        self.token = None
        self.product_ids = self.load_product_ids()

    def load_product_ids(self):
        df = pl.read_csv("fashion.csv")
        product_ids = df.select(pl.col("ProductId").unique()).to_series().to_list()
        return product_ids

    @task
    def get_product_by_id(self):
        with self.client.rename_request("/product/[id]"):
            time.sleep(0.5)
            # for i in range(10):
            #     self.client.get("/blog?id=%i" % i)
            for product_id in self.product_ids:
                self.client.get(f"/product/{product_id}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"
