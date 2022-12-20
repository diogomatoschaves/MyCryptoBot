import json
import os
from datetime import datetime, timedelta

import django
import redis
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
import pytz
from flask import Blueprint, jsonify, request
from flask_jwt_extended import unset_jwt_cookies, create_access_token, get_jwt, get_jwt_identity, jwt_required

from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

cache = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))

User = get_user_model()

user_management = Blueprint('user_management', __name__)


@user_management.after_request
@handle_db_connection_error
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(pytz.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                cache.set("bearer_token", f"Bearer {access_token}")
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@user_management.post('/token')
@handle_db_connection_error
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    try:
        user = User.objects.get(username=username)

        if not check_password(password, user.password):
            raise User.DoesNotExist
    except User.DoesNotExist:
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=username)

    cache.set("bearer_token", f"Bearer {access_token}")

    response = {"access_token": access_token}

    return response


@user_management.post("/logout")
@handle_db_connection_error
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
