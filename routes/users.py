from flask import Flask
from flask_smorest import Api, Blueprint,abort
from marshmallow import Schema, fields
from flask.views import MethodView
from pymongo import MongoClient
from schemas import *
from db.mongodb import db
from bson import ObjectId
import bcrypt
import re
from flask_jwt_extended import create_access_token

#blueprint
users_blp = Blueprint("user","users",url_prefix="/user")

users_collection = db.users

#get user
@users_blp.route("/present_users")
class PresentUsers(MethodView):

    @users_blp.response(200,GetUser(many=True))
    def get(self):

        users = users_collection.find({})

        output = []

        for user in users:
            output.append({
                "user_id":str(user["_id"]),
                "username":user["username"]
            })

        return output  


#create user
@users_blp.route("/create_users")
class CreateUsers(MethodView):
    @users_blp.arguments(CreateUser)
    @users_blp.response(200,CreateUser)
    def post(self,data):

        # user = users_collection.find_one({"_id":ObjectId(data["user_id"])})

        if users_collection.find_one({"username":data["username"]}):
            abort(400,message="Username already exists")
        
        #check the password has minimum of 4 charachters and consists atleat one numerical character
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#!%^&*/';.,<>:?])[A-Za-z\d$!@*%^&?]{4,}$"
        if not re.match(password_pattern,data["password"]):
            abort(400,message="Password should have minimum of 4 character with atlest 1 special,uppercase,lowercase and numerical character")

        #hash the current password
        hashd_pw = bcrypt.hashpw(data["password"].encode('utf-8'),bcrypt.gensalt())
        data["password"] = hashd_pw.decode('utf-8')

        users_collection.insert_one(data)

        return data    

#delete the user
@users_blp.route("/delete_user")
class DeleteUser(MethodView):
    
    @users_blp.arguments(DeleteUserSchema)
    @users_blp.response(200)
    def delete(self,data):

        user_id = ObjectId(data["userid"])

        if not users_collection.find_one({"_id":user_id}):
            abort(404,message="User not found")

        users_collection.delete_one({"_id":user_id})

        return "User Deleted"
    

#update user password
@users_blp.route("/update_password")
class UpdatePassword(MethodView):

    @users_blp.arguments(UpdatePasswordSchema)
    @users_blp.response(201)
    def put(self,data):

        user_id = ObjectId(data["userid"])

        user = users_collection.find_one({"_id":user_id})
        if not user:
            abort(404,message="User not found")
        
        if not bcrypt.checkpw(data["current_password"].encode("utf-8"),user["password"].encode("utf-8")):
        # if not users_collection.find_one({"password":data["current_password"]}):
            abort(404,message="Password does not match")

        updated_hashed_pw = bcrypt.hashpw(data["updated_password"].encode("utf-8"),bcrypt.gensalt()).decode("utf-8")
        users_collection.update_one(
            {
                "_id":user_id
            },
            {
                "$set":{
                    "password":updated_hashed_pw
                }
            }
        )   

        return "Password Updated Successfully"
    


@users_blp.route("/create_token")
class CreateToken(MethodView):

    @users_blp.arguments(CreateAccessTokenSchema)
    @users_blp.response(201)
    def post(self,data):

        user_id = ObjectId(data["userid"])
        user = users_collection.find_one({"_id":user_id})

        if not user:
            abort(404,message="User not found")

        if not bcrypt.checkpw(data["password"].encode("utf-8"),user["password"].encode("utf-8")):
            abort(400,message="Inccorect paswword")

        token = create_access_token(identity=str(user["_id"]))

        return token    

