from flask import Flask
from flask_smorest import Api, Blueprint,abort
from marshmallow import Schema, fields
from flask.views import MethodView
from pymongo import MongoClient
from routes.items import item_blp
from routes.orders import orders_blp
from routes.users import users_blp
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv)

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017")
db = client["items_db"]
# items_collection = db["items"]  #table
# order_collection = db["orders"]

app.config["JWT_SECRET_KEY"] = os.getenv("SECRETKEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["API_SPEC_OPTIONS"] = {
    "security":[{"bearerAuth":[]}]
}
app.config["API_TITLE"] = "Product Api"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

app.config["OPENAPI_SECURITY_SCHEMES"]={
    "bearerAuth":{
        "type":"http",
        "scheme":"bearer",
        "bearerFormat":"JWT"
    }
}
api = Api(app)
api.spec.components.security_scheme(
    "bearerAuth",{
        "type":"http",
        "scheme":"bearer",
        "bearerFormat":"JWT"
    }
)
api.security=[{"bearerAuth":[]}]
jwt = JWTManager(app)

api.register_blueprint(item_blp)
api.register_blueprint(orders_blp)
api.register_blueprint(users_blp)


if __name__ == "__main__":
    app.run(debug=True)