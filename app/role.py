import functools
from flask_jwt_extended import get_jwt
from flask import jsonify

class Role:
    @staticmethod
    def role_required(role):
        def decorator(f):
            @functools.wraps(f)
            def decorated(*args, **kwargs):
                claims = get_jwt()
                if claims.get("role") != role:
                    return jsonify({"message": "Unauthorized"}), 403
                return f(*args, **kwargs)
            return decorated
        return decorator
