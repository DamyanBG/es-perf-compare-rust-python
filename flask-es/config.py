from os import environ

from dotenv import load_dotenv

load_dotenv()

API_KEY = environ["API_KEY"]
API_KEY_ID = environ["API_KEY_ID"]
ES_HOST = environ["ES_HOST"]
CLOUD_ID = f"{environ["CLOUD_ID"]}"
