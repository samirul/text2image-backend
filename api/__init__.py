from flask import Flask
from .celery_task.celery_ import celery_init_app
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_mapping(
    CELERY={
        "broker_url": "redis://localhost",
        "result_backend": "redis://localhost",
        "task_ignore_result": True,
    }
)
celery_app = celery_init_app(app)
app.config['SECRET_KEY'] = '605e4f092eb4936a59989f99'

client = MongoClient('localhost', 27017)
# MongoDB database
db = client.text2image_flask_database
# text2image collection
text2image = db.text2image


from api import routes