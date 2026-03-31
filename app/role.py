from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
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
        return wrapper