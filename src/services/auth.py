from functools import wraps

from flask_jwt_extended import verify_jwt_in_request


def auth_verify(api):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except:
                return api.abort(403, 'Invalid token')
            
            return fn(*args, **kwargs)

        return decorator

    return wrapper