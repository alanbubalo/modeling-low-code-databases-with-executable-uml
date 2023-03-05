"""Module for creating CRUD operations on users"""
from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token
)
from sqlalchemy.exc import IntegrityError
from app.api import api
from app.models import User
from app import db


@api.get('/users')
@jwt_required()
def get_users():
    """Get all users."""
    users = User.query.all()
    return jsonify(data=[user.to_dict() for user in users]), 200


@api.post('/users')
def post_user():
    """Add a new user."""
    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')
    confirm = request.json.get('confirm')

    # Validate password
    if len(password) < 8:
        return jsonify(msg="Password must be at least 8 characters"), 400
    if confirm != password:
        return jsonify(msg="Passwords must match"), 400

    # Find user by email
    user_with_email = User.query.filter_by(email=email).first()
    if user_with_email is not None:
        return jsonify(msg="User already registered"), 400

    # Create new user
    new_user = User(name=name, email=email)
    new_user.password = password
    try:
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        return jsonify(data={
            "user": new_user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }), 201
    except IntegrityError:
        db.session.rollback()
    return jsonify(msg="Integrity error"), 400


# @api.get('/users/<int:user_id>')
@api.get('/users/me')
@jwt_required()
def get_user_by_id():
    """Get current user or user with given id."""
    user = User.query.get_or_404(get_jwt_identity())
    return jsonify(data=user.to_dict()), 200


# @api.patch('/users/<int:user_id>')
@api.patch('/users/me')
@jwt_required()
def patch_user():
    """Change user password and/or name."""
    name = request.json.get('name')
    password = request.json.get('password')
    confirm = request.json.get('confirm')

    # Change and validate name and password
    user = User.query.get_or_404(get_jwt_identity())
    if password is not None:
        if len(password) < 8:
            return jsonify(msg="Password must be at least 8 characters"), 400
        if confirm != password:
            return jsonify(msg="Passwords must match"), 400
        user.password = password
    if name is not None:
        user.name = name

    db.session.commit()
    return jsonify(data=user.to_dict()), 200
