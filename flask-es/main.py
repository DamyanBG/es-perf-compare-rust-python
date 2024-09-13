from flask import Flask
from flask_restful import Api

from resources.routes import routes


app = Flask(__name__)
api = Api(app)
[api.add_resource(*r) for r in routes]