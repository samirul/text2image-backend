from api import user

user.delete_many({"username": "cat1", "email": "cat1@cat.com"})