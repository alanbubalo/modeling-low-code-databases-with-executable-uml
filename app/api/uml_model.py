"""Module for creating CRUD operations on UML models"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app import db
from app.api import api
from app.models import IDPair, UMLModel
from app.baserow_init import (
    create_baserow_database,
    update_baserow_database,
    delete_baserow_database
)
from app.api.id_pair import model_found, delete_id_pair_in_model, create_id_pair_in_model


def refresh_list_id_pairs_in_model(user_id: int, model_id: int, id_pairs_input: list) -> tuple:
    """Refresh list of ID pairs in the given model"""
    if not model_found(user_id, model_id) is None:
        return jsonify(msg="Model not found"), 404

    id_pairs_database = IDPair.query.filter_by(uml_model_id=model_id).all()
    for pair in id_pairs_database:
        if not delete_id_pair_in_model(pair):
            return jsonify(msg="Integrity error"), 400

    for pair in id_pairs_input:
        # Check if pair already exists
        same_pair = IDPair.query.filter_by(and_(**pair, uml_model_id=model_id)).first()
        if same_pair is not None:
            return jsonify(msg="Pair already exists"), 400
        create_id_pair_in_model(pair, model_id)

    return "", 200


@api.get('/models')
@jwt_required()
def get_models():
    """Get all models"""
    models = UMLModel.query.filter_by(user_id=get_jwt_identity()).all()
    return jsonify(data=[model.to_dict() for model in models]), 200


@api.get('/models/<model_id>')
@jwt_required()
def get_model_by_id(model_id):
    """Get model by id"""
    model = UMLModel.query.filter_by(id=model_id, user_id=get_jwt_identity()).first()
    if not model:
        return jsonify(msg="Model not found"), 404
    return jsonify(data=model.to_dict()), 200


@api.post('/models')
@jwt_required()
def post_model():
    """Create a new one"""
    body = request.json
    body['user_id'] = get_jwt_identity()
    model_dict = {
        'user_id': get_jwt_identity(),
        'database_url': body['database_url'],
        'baserow_token': body['baserow_token'],
        'group_id': body['group_id'],
        'filename': body['filename'],
        'database_id': 0,
        'database_name': body['database_name'],
    }
    model = UMLModel(**model_dict)
    try:
        print(1)
        id_pairs = IDPair.query.filter_by(uml_model_id=model.id).all()
        print(2)
        id_pairs = [pair.to_dict() for pair in id_pairs]
        print(3)
        id_pairs, database_id = create_baserow_database(
            get_jwt_identity(),
            model.group_id,
            model.baserow_token,
            model.database_name,
            model.filename,
            id_pairs
        )
        response = refresh_list_id_pairs_in_model(get_jwt_identity(), model.id, id_pairs)
        if response[1] != 200:
            return response[0]

        model.database_id = database_id
        db.session.add(model)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Integrity error"), 200
    return jsonify(data=model.to_dict()), 200


@api.patch('/models/<model_id>')
@jwt_required()
def patch_model(model_id):
    """Get all models or create a new one"""
    body = request.json
    body['user_id'] = get_jwt_identity()
    model = UMLModel.query.get_or_404(id=model_id, user_id=get_jwt_identity()).first()
    try:
        db.session.update(model, body)
        db.session.commit()
        id_pairs = IDPair.query.filter_by(uml_model_id=model.id).all()
        id_pairs = [pair.to_dict() for pair in id_pairs]
        id_pairs = update_baserow_database(
            get_jwt_identity(),
            model.group_id,
            model.baserow_token,
            model.database_name,
            model.filename,
            id_pairs
        )
        response = refresh_list_id_pairs_in_model(get_jwt_identity(), model.id, id_pairs)
        if response[1] != 200:
            return response[0]
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Unable to update model"), 400
    return jsonify(msg="Model updated"), 200


@api.patch('/change-token/model/<model_id>')
@jwt_required()
def change_token(model_id):
    """Change Baserow token"""
    token = request.json.get('token')
    old_model = UMLModel.query.get_or_404(id=model_id, user_id=get_jwt_identity()).first()
    new_model = UMLModel.query.get_or_404(id=model_id, user_id=get_jwt_identity()).first()
    new_model.token = token
    try:
        db.session.update(old_model, new_model)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Unable to update model"), 400
    return jsonify(msg="Model updated"), 200


@api.delete('/models/<model_id>')
@jwt_required()
def delete_model(model_id):
    """Delete a model by ID"""
    model = UMLModel.query.get_or_404(id=model_id, user_id=get_jwt_identity()).first()
    try:
        db.session.delete(model)
        db.session.commit()
        delete_baserow_database(
            model.group_id,
            model.baserow_token,
            model.database_id
        )
        response = refresh_list_id_pairs_in_model(get_jwt_identity(), model.id, [])
        if response[1] != 200:
            return response[0]
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Unable to delete model"), 400
    return "", 204
