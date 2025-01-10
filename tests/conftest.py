import os
import uuid
import json
from datetime import datetime, timedelta
import jwt
import pytest
from dotenv import load_dotenv
from api import app, user, celery_app, text2image
from .random_object_id_generate.generate_id import random_object_id

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

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
    access_token = jwt.encode({
        'user_id': str(uuid.uuid4()),
        'exp': datetime.utcnow() + timedelta(minutes=25)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return access_token

@pytest.fixture
def get_user_info(get_access_token):
    try:
        # Decode jwt token by using secret key
        access_token = get_access_token
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        user_info = {"pk": payload['user_id'], 'email': 'cat1@cat.com'}
        return json.dumps(user_info)
    except jwt.ExpiredSignatureError:
        return f"token expired {401}"
    except jwt.InvalidTokenError:
        return f"token expired {401}"

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
        'mimeType': 'image/png',
        "user_id": user_["_id"],
    }
    image_ids = []
    check_data_already_in = text2image.find_one({"image_name": custom_data.get("image-xyz"),
                                                  "user": custom_data.get("user_id")
                                                   })
    if not check_data_already_in:
        image_id = text2image.insert_one(custom_data)
        image_ids.append(image_id.inserted_id)
    else:
        image_ids.append(check_data_already_in['_id'])
    return image_ids[0]