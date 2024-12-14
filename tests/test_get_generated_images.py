import json
from api import user, text2image

def test_get_generated_image(client, get_access_token, set_user_info, create_generated_image_manually):
    access_token = get_access_token
    user_id = set_user_info

    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Sending POST request
    response = client.get('/all-images/', headers=headers, json={})

     # Assert response
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'id' in parsed_data['data'][0]
    assert 'image_data' in parsed_data['data'][0]
    assert 'image_name' in parsed_data['data'][0]
    assert 'user_id' in parsed_data['data'][0]
    assert parsed_data['data'][0]['image_name'] == 'image-xyz'
    assert parsed_data['data'][0]['user_id'] == str(user_id['_id'])
    assert response.status_code == 200
    text2image.delete_many({"user_id": user_id['_id']})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_get_generated_image_failed_for_no_auth(client, get_access_token, set_user_info, create_generated_image_manually):
    user_id = set_user_info

    # Sending POST request
    response = client.get('/all-images/', headers=None, json={})

    # Assert response
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    text2image.delete_many({"user_id": user_id['_id']})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_get_generated_image_failed_for_wrong_access_token(client, get_access_token, set_user_info, create_generated_image_manually):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_id = set_user_info

    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Sending POST request
    response = client.get('/all-images/', headers=headers, json={})

    # Assert response
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    text2image.delete_many({"user_id": user_id['_id']})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})   
