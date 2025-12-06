from marshmallow import Schema, fields


#schema get
class ItemGetSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    price = fields.Int()

#schema post
class ItemSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Int(required=True)

#schema for put
class updateSchema(Schema):
    updated_name = fields.Str(required=False)
    updated_price = fields.Int(required=False)


#schema for delete
class deleteSchema(Schema):
    id = fields.Str(required=True)


#get orders schema
class OrderGetSchema(Schema):
    order_id = fields.Str()
    item_id = fields.Str()
    product_name = fields.Str()
    quantity = fields.Int()
    price = fields.Int()
    total_amount = fields.Float()

#post orders schema
class OrderSchema(Schema):
    product_id = fields.Str(required=True)
    quantity = fields.Int(required=True)


#put order schema
class UpdateOrderSchema(Schema):
    order_id = fields.Str(required=True)
    update_quantity = fields.Int(required=True)


#delete order schema
class DeleteOrderSchema(Schema):
    order_id = fields.Str(required=True)
    


#user schema
class UserSchema(Schema):
    user_id = fields.Str()
    username = fields.Str(required=True)
    password = fields.Str(required=True)    

#user get schema
class GetUser(Schema):
    user_id = fields.Str()
    username = fields.Str()  

#user creation
class CreateUser(Schema):
    # user_id = fields.Str()
    username = fields.Str(required=True)
    password = fields.Str(required=True)   

#delete user
class DeleteUserSchema(Schema):
    userid = fields.Str(required=True)

#update password
class UpdatePasswordSchema(Schema):
    userid = fields.Str(required=True)  
    current_password = fields.Str(required=True)
    updated_password = fields.Str(required=True)

#create token
class CreateAccessTokenSchema(Schema):
    userid = fields.Str(required=True)
    password = fields.Str(required=True)
    