import functools
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

class Role:
    @staticmethod
    def role_required(role):
        def decorator(f):
            @functools.wraps(f)  # ✅ this is the fix
            def decorated(*args, **kwargs):
                identity = get_jwt_identity()
                if identity['role'] != role:
                    return jsonify({"message": "Unauthorized"}), 403
                return f(*args, **kwargs)
            return decorated
        return decorator




'''from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response

class Role:
    def role_required(required_role):
        def wrapper(fn):
            @jwt_required()
            def decorated(*args, **kwargs):
                user = get_jwt_identity()
                if user["role"] != required_role:
                    return make_response("Unauthorized Access", 403)
                return fn(*args, **kwargs)
            return decorated
        return wrapper'''