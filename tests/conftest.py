import uuid
import json
import pytest
from bson.objectid import ObjectId
from api import app, user, cache, celery_app,text2image
from .random_object_id_generate.generate_id import random_object_id

@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def celery_app_test():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield celery_app

@pytest.fixture
def get_access_token():
    access_token = cache.get("test_user_key")
    token = access_token.decode().replace("'", '"')
    if token:
        return token
    return

@pytest.fixture
def get_user_info(get_access_token):
    user_info = cache.get("test_user_info")
    info = user_info.decode().replace("'", '"')
    if info:
        return info
    return

@pytest.fixture
def set_user_info(get_user_info):
    user_ = json.loads(get_user_info)
    id_ = uuid.UUID(user_.get("pk"))
    username = user_.get("email").split("@")[0]
    email = user_.get("email")
    inserted = user.insert_one({"_id": id_, "username": username, "email": email})
    user_detail = user.find_one({"_id": inserted.inserted_id})
    return user_detail



@pytest.fixture
def create_generated_image_manually(set_user_info):
    id_ = random_object_id()
    user_ = set_user_info
    custom_data ={
        "_id": id_,
        "image_name": "image-xyz",
        "image_data": "74123849661A86iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAIAAAB7GkOtAAEAAElEQVR4nET92ZIc25IliK",
        "user_id": user_["_id"]
    }
    image_ids = []
    check_data_already_in = text2image.find_one({"category_name": custom_data.get("category_name"),
                                                  "user": custom_data.get("user")
                                                   })
    if not check_data_already_in:
        image_id = text2image.insert_one(custom_data)
        image_ids.append(image_id.inserted_id)
    else:
        image_ids.append(check_data_already_in['_id'])
    return image_ids[0]