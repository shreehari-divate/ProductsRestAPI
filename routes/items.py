from flask import Flask
from flask_smorest import Api, Blueprint,abort
from marshmallow import Schema, fields
from flask.views import MethodView
from pymongo import MongoClient
from schemas import *
from db.mongodb import db
from bson import ObjectId
from flask_jwt_extended import jwt_required,get_jwt_identity

#blueprint
item_blp = Blueprint("items","items",url_prefix="/items")  

items_collection = db.items

@item_blp.route("/get")
class ItemsGet(MethodView):
    
    @jwt_required()
    @item_blp.response(200,ItemGetSchema(many=True))
    def get(self):
        user_id = get_jwt_identity() 
        results=items_collection.find({})
        output=[]
        for item in results:
            output.append({
                "id":str(item["_id"]),
                "name":item["name"],
                "price":item["price"]
            })
        return output
        # return [{"name":k,"price":p}for k,p in current_items.items()]


@item_blp.route("/post")
class ItemsPost(MethodView):

    @jwt_required()
    @item_blp.arguments(ItemSchema)
    @item_blp.response(201,ItemSchema)
    def post(self,data):
        if items_collection.find_one({"name":data["name"]}):
            abort(400,message=f"{data['name']} already exists")
        items_collection.insert_one(data)
           
        # if data["name"] in current_items:
        #     abort(400,message=f"{data['name']} already exists")
        # current_items[data["name"]]=data["price"]
        return data
    
@item_blp.route("/put/<id>")
class ItemPut(MethodView):

    @jwt_required()
    @item_blp.arguments(updateSchema)
    @item_blp.response(201,updateSchema)
    def put(self,data,id):
        
        try:
            obj_id = ObjectId(id)
        
        except Exception as e:
            abort(400, message="Invalid ID format")     

        item = items_collection.find_one({"_id":obj_id})
        if not item:
            abort(404,message="Item not found")

        new_name = data.get("updated_name",item["name"])    
        new_price = data.get("updated_price",item["price"])

        items_collection.update_one(
            {"_id":obj_id},
            {
                "$set":{
                    "name":new_name,
                    "price":new_price
                }
            }
        )    

        return {
            "id":id,
            "name": new_name,
            "price": new_price
        }   
    
@item_blp.route("/delete")
class ItemDelete(MethodView):

    @jwt_required()
    @item_blp.arguments(deleteSchema)
    @item_blp.response(204,ItemSchema)    
    def delete(self,data):

        try:
            obj_id = ObjectId(data["id"])
        except Exception as e:
            abort(400,message="Id invalid")    
        
        if not items_collection.find_one({"_id":obj_id}):
            abort(404,message=f"{data['id']} not found")
        items_collection.delete_one({"_id":obj_id})    
        return "Item removed"
