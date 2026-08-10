from functools import wraps
from flask import jsonify
from flask_login import current_user


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Warning - Authentication required"}), 401
            if not current_user.is_active:
                return jsonify({"error": "Your account is inactive or blacklisted"}), 403
            if current_user.role not in roles:
                return jsonify({"error": "Forbidden: Incorrect role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator