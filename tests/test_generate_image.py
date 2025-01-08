from api import user, text2image
from api.tasks import generate


def test_generate_image(client, get_access_token, set_user_info, celery_app_test):
    access_token = get_access_token
    user_id = set_user_info

    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Sending POST request
    response = client.post('/generate-image/', headers=headers, json={"text": "horse smiling"})

    print(response)

     # Assert response
    assert 'msg' in response.json
    assert 'result_id' in response.json
    assert 'result_status' in response.json
    assert response.json['msg'] == 'Success'
    assert response.json['result_status'] == 'SUCCESS'
    assert response.status_code == 200
    text2image.delete_many({"user_id": user_id['_id']})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_generate_image_failed_for_no_auth(client, get_access_token, set_user_info, celery_app_test):
    access_token = get_access_token

    # Sending POST request
    response = client.post('/generate-image/', headers=None, json={"text": "horse smiling"})

     # Assert response
    assert 'msg' not in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert 'error' in response.json
    assert response.json['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_generate_image_failed_for_wrong_access_token(client, get_access_token, set_user_info, celery_app_test):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'

    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Sending POST request
    response = client.post('/generate-image/', headers=headers, json={"text": "horse smiling"})

     # Assert response
    assert 'msg' not in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert 'error' in response.json
    assert response.json['error'] == 'Invalid token'
    assert response.status_code == 401
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_celery_task_running(set_user_info):
    user_id = set_user_info
    text = "horse smiling"
    payload = {"user_id": str(user_id["_id"])}
    assert str(generate.delay(text=text, payload=payload).get()) == "{'current': 100, 'total': 100, 'status': 'Task completed!'}"
    text2image.delete_many({"user_id": user_id['_id']})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_celery_if_failed_wrong_type_id(set_user_info):
    user_id = set_user_info
    text = "horse smiling"
    payload = {"user_id": int(user_id["_id"])}
    assert str(generate.delay(text=text, payload=payload).get()) == "'int' object has no attribute 'replace'"
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_celery_if_no_text_being_send(set_user_info):
    user_id = set_user_info
    text = ""
    payload = {"user_id": int(user_id["_id"])}
    assert str(generate.delay(text=text, payload=payload).get()) == "No text is found."
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_celery_if_no_payload_being_send(set_user_info):
    user_id = set_user_info
    text = "horse smiling"
    payload = {}
    assert str(generate.delay(text=text, payload=payload).get()) == "User is not logged in, not user information has been found."
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})




    