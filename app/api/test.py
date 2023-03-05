"""Test basic API call and protected API call with required token"""
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api


@api.get('/test')
def api_test():
    """Test API call"""
    return jsonify(test="Test works"), 200


@api.get("/test_protected")
@jwt_required()
def api_test_protected():
    """Test API call with JWT authorization"""
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
