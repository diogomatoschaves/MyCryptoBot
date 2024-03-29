import json
import os
from datetime import datetime, timedelta

import django
import redis
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
import pytz
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, verify_jwt_in_request, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import DecodeError, ExpiredSignatureError

from shared.utils.config_parser import get_config
from shared.utils.decorators import general_app_error
from shared.utils.decorators import handle_db_connection_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

config_vars = get_config()

cache = redis.from_url(os.getenv('REDIS_URL', config_vars.redis_url))

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
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                cache.set("bearer_token", f"Bearer {access_token}")
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError, NoAuthorizationError, DecodeError, ExpiredSignatureError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@user_management.post('/token')
@general_app_error
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
