from api import app, text2image
from flask import request, jsonify
from bson.objectid import ObjectId
from api import tasks
from jwt_token.jwt_token_verify import jwt_login_required


@app.route("/generate-image", methods=['POST'])
@jwt_login_required
def post_generate_image(payload):
    try:
        text_inputed = request.json.get("text")
        result = tasks.task_generate.delay(text=text_inputed,payload=payload)
        return jsonify({"msg":"success","result_id": result.id}),200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400


@app.route("/all-images", methods=['GET'])
@jwt_login_required
def get_generated_images(payload):
    try:
        data = []
        images = text2image.find({"user_id": payload['user_id']})
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

        


@app.route("/image/<ids>/", methods=['GET'])
@jwt_login_required
def get_single_generated_images(ids, payload):
    try:
        data = []
        image = text2image.find_one({'_id': ObjectId(str(ids)), "user_id": payload['user_id']})
        if image is None:
            return jsonify({"msg": f"Data {ids} is not found."}),404
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


@app.route("/image/delete/<ids>/", methods=['POST'])
@jwt_login_required
def delete_single_generated_images(ids, payload):
    try:
        if text2image.find_one({'_id': ObjectId(str(ids)), 'user_id': payload['user_id']}) is None:
            return jsonify({"msg": f"Data {ids} is not found."}),404
        text2image.delete_one({'_id': ObjectId(str(ids))})
        return jsonify({}),204
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request."}),400