import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request
from errors import APIError

# The secret key signs the tokens. Only the server knows it.
SECRET_KEY = "web-services-course-project-2026-secret-key"
ALGORITHM = "HS256"

# The only user that can log in (hardcoded for this project)
USERNAME = "admin"
PASSWORD = "test123456"

# How long an access token lives (short, so you can show the expiry in the video)
ACCESS_TOKEN_MINUTES = 2


def create_access_token(username):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,                                       # who the token belongs to
        "type": "access",                                      # kind of token
        "iat": now,                                            # issued at
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),  # expires at
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(route_function):
    """Put this above a route to make it refuse requests without a valid token."""
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise APIError("Missing token: send 'Authorization: Bearer <token>'", 401)

        token = header[len("Bearer "):].strip()
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise APIError("Token has expired", 401)
        except jwt.InvalidTokenError:
            raise APIError("Invalid token", 401)

        if payload.get("type") != "access":
            raise APIError("Invalid token type", 401)

        return route_function(*args, **kwargs)
    return wrapper