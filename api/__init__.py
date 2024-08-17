import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'text2img.db')
app.config['SECRET_KEY'] = '605e4f092eb4936a59989f99'
db = SQLAlchemy(app)

from api import routes