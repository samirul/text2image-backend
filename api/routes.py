from api import app, text2image
from flask import request, jsonify
from bson.objectid import ObjectId
from api import tasks


@app.route("/generate-image", methods=['POST'])
def post_generate_image():
    text_inputed = request.json.get("text")
    result = tasks.task_generate.delay(text_inputed)
    return jsonify({"result_id": result.id})


@app.route("/all-images", methods=['GET'])
def get_generated_images():
    data = []
    images = text2image.find({})
    for image in images:
        dict_items = {
            "id": str(image['_id']),
            "image_data": str(image['image_data']),
            "image_name": str(image['image_name']),
        }
        data.append(dict_items)
    return jsonify(data)


@app.route("/image/<id>/", methods=['GET'])
def get_single_generated_images(id):
    data = []
    image = text2image.find_one({'_id': ObjectId(str(id))})
    print(image)
    dict_items = {
        "id": str(image['_id']),
        "image_data": str(image['image_data']),
        "image_name": str(image['image_name']),
        }
    data.append(dict_items)
    return jsonify(data)


@app.route("/image/delete/<id>/", methods=['POST'])
def delete_single_generated_images(id):
    text2image.delete_one({'_id': ObjectId(str(id))})
    return jsonify({"msg": "Deleted successfuly."})