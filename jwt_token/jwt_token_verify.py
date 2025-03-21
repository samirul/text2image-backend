"""
    Function decorator for checking jwt access token so user who logged in can access information.
"""

import os
from functools import wraps
import jwt
from flask import jsonify, request

SECRET_KEY = os.environ.get('SECRET_KEY')

def jwt_login_required(func):
    """custom function for getting jwt access token from other apps so we can
       check if the user has logged on has permission to access app or not
       if jwt access token avalible then yes and the user has access until
       access token expire.

    Args:
        func (args, kwags): getting access_tokens with bearer from django youtools.

    Returns:
        args, kwargs: decorator returns args and kwags with payload for authentication.
    """
    @wraps(func)
    def jwt_check_token(*args, **kwargs):
        # Get the Authrization header
        header = request.headers.get('Authorization')
        # Checking for if header and header token type Bearer avalible or not
        if not header or not header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header is missing or invalid'}), 401
        token = header.split(' ')[1]
        try:
            # Decode jwt token by using secret key
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        kwargs['payload'] = payload
        
        return func(*args, **kwargs) # return valid payload
    return jwt_check_token
    