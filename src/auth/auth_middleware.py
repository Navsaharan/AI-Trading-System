from functools import wraps
from flask import request, jsonify
from .firebase_config import verify_token

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        user_id = verify_token(token.split('Bearer ')[1])
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(user_id, *args, **kwargs)
    return decorated
