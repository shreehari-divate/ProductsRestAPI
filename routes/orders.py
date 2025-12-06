from flask import Flask
from flask_smorest import Api, Blueprint,abort
from marshmallow import Schema, fields
from flask.views import MethodView
from pymongo import MongoClient
from schemas import *
from db.mongodb import db
from routes.items import items_collection
from bson import ObjectId
from routes.items import items_collection
from flask_jwt_extended import jwt_required,get_jwt_identity

#blueprint
orders_blp = Blueprint("orders","orders",url_prefix="/orders")

orders_collection = db.orders
# orders_collection.delete_many({})

def order_id_generator():
    last_order = orders_collection.find_one(
        sort = [("order_id",-1)]
    )

    if not last_order:
        return "ORD0001"
    last_id = int(last_order["order_id"][3:])
    new_id = last_id+1

    return f"ORD{new_id}"


@orders_blp.route("/create_order")
class OrderCreate(MethodView):

    @jwt_required()
    @orders_blp.arguments(OrderSchema)
    @orders_blp.response(201,OrderSchema)
    def post(self,data):
        item = items_collection.find_one({"_id":ObjectId(data["product_id"])})

        if not item:
            abort(400,message="item not found")

        item_price = item["price"]
        total_price = item_price*data["quantity"]
        item_name = item["name"]

        order_id = order_id_generator()

        order = {
            "order_id":order_id,
            "item_id":str(item["_id"]),
            "item_name":item_name,
            "quantity":data["quantity"],
            "price":item_price,
            "total_amount":total_price
        }    

        orders_collection.insert_one(order)

        return order
    
@orders_blp.route("/get_order")
class GetOrder(MethodView):

    @jwt_required()
    @orders_blp.response(200,OrderGetSchema(many=True))
    def get(self):

        orders = orders_collection.find({})
        output=[]
        if not orders:
            abort(404,message="No orders")


        for order in orders:
            items = items_collection.find_one({"_id":ObjectId(order["item_id"])})   
            if not items:
                abort(404,message="No items found")
            output.append({
            "order_id":order["order_id"],
            "item_id": order["item_id"],
            "product_name":items["name"],
            "price":items["price"],
            "quantity":order["quantity"],
            "total_amount":order["total_amount"]
            })
        return output


@orders_blp.route("/delete_order")
class DeleteOrder(MethodView):

    @jwt_required()
    @orders_blp.arguments(DeleteOrderSchema)
    @orders_blp.response(200)
    def delete(self,order_id):
        if not orders_collection.find_one(order_id):
            abort(404,message="Order not present")
        orders_collection.delete_one(order_id)
        return f"{order_id} removed"
    
@orders_blp.route("/update_order")
class UpdateOrder(MethodView):

    @jwt_required() 
    @orders_blp.arguments(UpdateOrderSchema)
    @orders_blp.response(201)
    def put(self,data):

        # order = orders_collection.find_one({data["order_id"]})
        # if not orders_collection.find_one({data["order_id"]}):
        #     abort(404,message="Order not present")
        # new_quantity = data["update_quantity"]
        # orders_collection.update_one({
        #     "quantity":new_quantity
        #     "total_amount":new_quantity*
        # })    

        order = orders_collection.find_one({"order_id":data["order_id"]})
        if not order:
            abort(404,message="Order not present")
        new_quantity = data["update_quantity"]
        total_amount = order["price"]*new_quantity
        orders_collection.update_one(
            {"order_id":data["order_id"]}, #filtering
            {"$set":{            
                "quantity":new_quantity,
                "total_amount":total_amount
                }}

        )  

        return {"Order Id":data["order_id"],"Updated Quantity":data["update_quantity"],"Total amount":total_amount}
        
