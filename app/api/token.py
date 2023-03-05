"""Module for creating a token"""
from datetime import datetime, timedelta, timezone
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    get_jwt
)
from app.api import api
from app.models import User


@api.after_request
def refresh_expiring_jwt(response):
    """Refreshing the token after expiring"""
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(hours=1))
        if target_timestamp > exp_timestamp:
            create_access_token(identity=get_jwt_identity())
            # set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@api.post("/token")
def create_token():
    """Create a new token"""
    email = request.json.get("email")
    password = request.json.get("password")

    # Get the user
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify(msg="User not found"), 404
    if not user.verify_password(password):
        return jsonify(msg="Invalid password"), 400

    # Create a new token with the user id inside
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(user_id=user.id, access_token=access_token, refresh_token=refresh_token), 200


@api.post("/token-refresh")
@jwt_required(refresh=True)
def token_refresh():
    """Refresh the access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify(user_id=user_id, access_token=access_token), 200


# @api.post("/token-verify")
# @jwt_required(refresh=True)
# def token_verify():
#     refresh_token = request.json.get('refresh_token')
#     identity = get_jwt_identity()
