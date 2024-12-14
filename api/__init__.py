import os
from flask import Flask
from flask_caching import Cache
from dotenv import load_dotenv
from pymongo import MongoClient
from .celery_task.celery_ import celery_init_app

# Added environment variable
load_dotenv()

app = Flask(__name__)

# Adding env for fash_caching
app.config['CACHE_TYPE'] = os.environ.get('CACHE_TYPE')
app.config['CACHE_REDIS_HOST'] = os.environ.get('CACHE_REDIS_HOST')
app.config['CACHE_REDIS_PORT'] = os.environ.get('CACHE_REDIS_PORT')
app.config['CACHE_REDIS_DB'] = os.environ.get('CACHE_REDIS_DB')
app.config["CACHE_DEFAULT_TIMEOUT"] = os.environ.get('CACHE_DEFAULT_TIMEOUT')

# Initialize Flask-Caching with Redis
cache = Cache(app=app)
cache.init_app(app)

# Added info to celery
app.config.from_mapping(
    CELERY={
        "broker_url": "redis://localhost",
        "result_backend": "redis://localhost",
        "task_ignore_result": True,
    }
)
# Created celery app
celery_app = celery_init_app(app)

# Added flask secret key in env
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Added mongoclient 
client = MongoClient('localhost', 27017, uuidRepresentation="standard")

# Creating mongo database
db = client.text2image_flask_database

# text2image collection
text2image = db.text2image
user = db.user


from api import routes