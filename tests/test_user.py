from api import user


def test_user(set_user_info):
    user_info = set_user_info
    assert '_id' in user_info
    assert 'username' in user_info
    assert 'email' in user_info
    assert user_info['username'] == "cat1"
    assert user_info['email'] == "cat1@cat.com"
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
