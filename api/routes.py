from api import app, text2image
from flask import request, jsonify
from bson.objectid import ObjectId
from api import tasks


@app.route("/generate-image", methods=['POST'])
def post_generate_image():
    try:
        text_inputed = request.json.get("text")
        result = tasks.task_generate.delay(text_inputed)
        return jsonify({"msg":"success","result_id": result.id}),200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400


@app.route("/all-images", methods=['GET'])
def get_generated_images():
    try:
        data = []
        images = text2image.find({})
        if text2image.count_documents({}) == 0:
            return jsonify({"msg": "Data is not found."}),404
        for image in images:
            dict_items = {
                "id": str(image['_id']),
                "image_data": str(image['image_data']),
                "image_name": str(image['image_name']),
            }
            data.append(dict_items)
        return jsonify(data),200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400

        


@app.route("/image/<id>/", methods=['GET'])
def get_single_generated_images(id):
    try:
        data = []
        image = text2image.find_one({'_id': ObjectId(str(id))})
        if image is None:
            return jsonify({"msg": f"Data {id} is not found."}),404
        dict_items = {
            "id": str(image['_id']),
            "image_data": str(image['image_data']),
            "image_name": str(image['image_name']),
            }
        data.append(dict_items)
        return jsonify(data),200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400


@app.route("/image/delete/<id>/", methods=['POST'])
def delete_single_generated_images(id):
    try:
        if text2image.find_one({'_id': ObjectId(str(id))}) is None:
            return jsonify({"msg": f"Data {id} is not found."}),404
        text2image.delete_one({'_id': ObjectId(str(id))})
        return jsonify({"msg": "Deleted successfuly."}),204
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400