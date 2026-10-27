import os
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request
from errors import APIError

# The secret key signs the tokens. Only the server knows it.
SECRET_KEY = os.environ.get("SECRET_KEY", "web-services-course-project-2026-secret-key")
ALGORITHM = "HS256"

# The only user that can log in
USERNAME = os.environ.get("API_USERNAME", "admin")
PASSWORD = os.environ.get("API_PASSWORD", "test123456")

# Token lifetimes
ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", "2"))
REFRESH_TOKEN_MINUTES = int(os.environ.get("REFRESH_TOKEN_MINUTES", "10"))

# Server-side storage of the refresh tokens that were issued
# Format: { "the token string": expiry datetime }
refresh_tokens = {}


def create_access_token(username):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username):
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=REFRESH_TOKEN_MINUTES)
    payload = {
        "sub": username,
        "type": "refresh",
        "jti": str(uuid.uuid4()),   # unique id, so two logins never give the same token
        "iat": now,
        "exp": expires,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_tokens[token] = expires     # remember it on the server
    return token


def verify_refresh_token(token):
    """Returns the username if the refresh token is valid, otherwise raises a 401."""
    # 1. The server must have issued it (and it must not have been removed)
    if token not in refresh_tokens:
        raise APIError("Unknown or revoked refresh token", 401)

    # 2. The signature and the expiry must be valid
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        refresh_tokens.pop(token, None)     # clean it out of the dictionary
        raise APIError("Refresh token has expired, please log in again", 401)
    except jwt.InvalidTokenError:
        raise APIError("Invalid refresh token", 401)

    # 3. It must really be a refresh token
    if payload.get("type") != "refresh":
        raise APIError("Invalid token type", 401)

    return payload["sub"]


def token_required(route_function):
    """Put this above a route to make it refuse requests without a valid access token."""
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