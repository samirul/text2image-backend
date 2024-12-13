import json
from collections import OrderedDict
from flask import request, jsonify, Response
from bson.objectid import ObjectId
from jwt_token.jwt_token_verify import jwt_login_required
from api import tasks
from api import app, text2image
from api.producers import publish


@app.route("/generate-image", methods=['POST'])
@jwt_login_required
def post_generate_image(payload):
    try:
        text_inputed = request.json.get("text")
        if not text_inputed:
            response_data = json.dumps({"msg": "No text is found, add a text."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        result = tasks.task_generate.delay(text=text_inputed,payload=payload)
        return jsonify({"msg":"success","result_id": result.id, "result_status": result.status}),200
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/all-images", methods=['GET'])
@jwt_login_required
def get_generated_images(payload):
    try:
        data = []
        images = text2image.find({"user_id": payload['user_id']})
        if text2image.count_documents({}) == 0:
            response_data = json.dumps({"msg": "Data is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        for image in images:
            dict_items = OrderedDict([
                ("id", str(image['_id'])),
                ("image_data", str(image['image_data'])),
                ("image_name", str(image['image_name'])),
            ]) 
            data.append(dict_items)
        response_data = json.dumps({"data": data}, indent=4)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/image/<ids>/", methods=['GET'])
@jwt_login_required
def get_single_generated_images(ids, payload):
    try:
        data = []
        image = text2image.find_one({'_id': ObjectId(str(ids)), "user_id": payload['user_id']})
        if image is None:
            response_data = json.dumps({"msg": f"Data {ids} is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        dict_items = OrderedDict([
            ("id", str(image['_id'])),
            ("image_data", str(image['image_data'])),
            ("image_name", str(image['image_name'])),
            ])
        data.append(dict_items)
        response_data = json.dumps({"data": data}, indent=4)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/image/delete/<ids>/", methods=['DELETE'])
@jwt_login_required
def delete_single_generated_images(ids, payload):
    try:
        if text2image.find_one({'_id': ObjectId(str(ids)), 'user_id': payload['user_id']}) is None:
            response_data = json.dumps({"msg": f"Data {ids} is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        text2image.delete_one({'_id': ObjectId(str(ids))})
        publish("image_data_Delete_from_flask", ids)
        return Response({}, status=204, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')