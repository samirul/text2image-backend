"""
    Imported required libraries
    Added flask and celery on __init__ files so they will run before anything else
    also can be imported as package.
"""

import os
from urllib.parse import quote_plus
from huggingface_hub import login
from flask import Flask
from flask_caching import Cache
from dotenv import load_dotenv
from pymongo import MongoClient
from .celery_task.celery_ import celery_init_app

# Added environment variable
load_dotenv()

# Logging Hugging face
login(token=os.environ.get("HUGGING_KEY"))


app = Flask(__name__)

# Adding env for fash_caching
app.config['CACHE_TYPE'] = os.environ.get('CACHE_TYPE')
app.config['CACHE_REDIS_HOST'] = os.environ.get('CACHE_REDIS_HOST')
app.config['CACHE_REDIS_PASSWORD'] = os.environ.get('CACHE_REDIS_PASSWORD')
app.config['CACHE_REDIS_PORT'] = os.environ.get('CACHE_REDIS_PORT')
app.config['CACHE_REDIS_DB'] = os.environ.get('CACHE_REDIS_DB')
app.config["CACHE_DEFAULT_TIMEOUT"] = os.environ.get('CACHE_DEFAULT_TIMEOUT')

# Initialize Flask-Caching with Redis
cache = Cache(app=app)
cache.init_app(app)

# Added info to celery
app.config.from_mapping(
    CELERY={
        "broker_url": os.environ.get('CELERY_BROKER'),
        "result_backend": os.environ.get('CELERY_BACKEND'),
        "task_ignore_result": True,
    }
)
# Created celery app
celery_app = celery_init_app(app)

# Added flask secret key in env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Added mongoclient 
username = quote_plus(os.environ.get("MONGO_DB_USER_NAME"))
password = quote_plus(os.environ.get("MONGO_DB_PASSWORD"))
host = os.environ.get("MONGO_DB_HOST_NAME")
auth_source = os.environ.get("MONGO_DB_AUTH_SOURCE")
port = int(os.environ.get("MONGO_CUSTOM_DB_PORT"))
url = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
client = MongoClient(url, connect=False, uuidRepresentation="standard")

# Creating mongo database
db = client.text2image_flask_database

# text2image collection
text2image = db.text2image
user = db.user


from api import routes