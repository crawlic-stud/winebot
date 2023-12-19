import mongoengine as db


class Product(db.Document):
    meta = {"collection": "products"}
    name = db.StringField(max_length=256)
    description = db.StringField()
    image_id = db.StringField(max_length=256)
    price = db.IntField()


class Event(db.Document):
    meta = {"collection": "events"}
    name = db.StringField(max_length=256)
    description = db.StringField()
    image_id = db.StringField(max_length=256)
    date = db.DateTimeField(required=False)


class User(db.Document):
    meta = {"collection": "users"}
    user_id = db.IntField()
    username = db.StringField(max_length=256)
    first_name = db.StringField(max_length=256)
    last_name = db.StringField(max_length=256)
    last_active = db.DateTimeField()


class Admin(db.Document):
    meta = {"collection": "admins"}
    user_id = db.IntField()


class UserStat(db.Document):
    meta = {"collection": "userstats"}
    d = db.StringField()
    users = db.ListField(field=db.IntField())
