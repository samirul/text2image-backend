import string
import secrets
from bson.objectid import ObjectId

def random_object_id():
    alphabet = 'abcdef' + string.digits
    _id = ObjectId("".join(secrets.choice(alphabet) for _ in range(24)))
    return _id
