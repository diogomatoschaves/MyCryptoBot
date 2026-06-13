import os
from datetime import datetime, timedelta

import django
import redis
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
import pytz
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt, get_jwt_identity, verify_jwt_in_request,
    jwt_required, set_access_cookies, unset_jwt_cookies,
)
from flask_jwt_extended.exceptions import NoAuthorizationError, CSRFError
from jwt import DecodeError, ExpiredSignatureError

from shared.utils.settings import settings
from shared.utils.decorators import general_app_error
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


cache = redis.from_url(settings.redis_url)

User = get_user_model()

user_management = Blueprint('user_management', __name__)


@user_management.after_app_request
@handle_db_connection_error
def refresh_expiring_jwts(response):
    try:
        verify_jwt_in_request(optional=True)

        exp_timestamp = get_jwt()["exp"]

        now = datetime.now(pytz.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError, NoAuthorizationError, CSRFError, DecodeError, ExpiredSignatureError):
        # no valid JWT (or a state-changing request without a CSRF token) -
        # skip the sliding refresh and return the original response
        return response


MAX_LOGIN_ATTEMPTS = 10
LOGIN_ATTEMPTS_WINDOW_SECONDS = 300


@user_management.post('/token')
@general_app_error
@handle_db_connection_error
def create_token():
    # simple fixed-window rate limit to slow down password brute-forcing
    attempts_key = f"login_attempts {request.remote_addr}"
    attempts = cache.incr(attempts_key)
    if attempts == 1:
        cache.expire(attempts_key, LOGIN_ATTEMPTS_WINDOW_SECONDS)
    if attempts > MAX_LOGIN_ATTEMPTS:
        return jsonify({"msg": "Too many login attempts. Try again later."}), 429

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    try:
        user = User.objects.get(username=username)

        if not check_password(password, user.password):
            raise User.DoesNotExist
    except User.DoesNotExist:
        return jsonify({"msg": "Wrong email or password"}), 401

    access_token = create_access_token(identity=username)

    cache.delete(attempts_key)

    # the JWT is delivered as an httpOnly cookie (set_access_cookies also sets
    # the readable CSRF cookie); it is never exposed to JS
    response = jsonify({"login": True, "username": username})
    set_access_cookies(response, access_token)

    return response


@user_management.post('/logout')
def logout():
    response = jsonify({"logout": True})
    unset_jwt_cookies(response)
    return response


@user_management.get('/me')
@jwt_required()
def me():
    return jsonify({"username": get_jwt_identity()})
