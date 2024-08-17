from api import app, db
from flask import request, jsonify


@app.route("/")
def home():
    return jsonify({"Hello": "Hello"})