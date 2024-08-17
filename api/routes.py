from api import app, db
from flask import request, jsonify
from api import tasks

@app.route("/")
def home():
    result = tasks.task_generate.delay("cat in space")
    return jsonify({"result_id": result.id})