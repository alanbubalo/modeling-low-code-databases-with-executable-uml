"""Module for creating CRUD operations on ID pairs"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required #, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.api import api
from app.models import IDPair
from app.id_pairs_utils import model_found, find_class_id_for_table, find_table_id_for_class
from app.exc import NotFoundException
from app.id_pairs_utils import create_id_pair, delete_id_pair

# @api.get('/id_pairs')
# @jwt_required()
# def list_id_pairs():
#     """Get a list of ID pairs"""
#     id_pairs = IDPair.query.all()
#     return jsonify(data=[pair.to_dict() for pair in id_pairs]), 200


# @api.get('/id_pairs/<int:_id>')
# @jwt_required()
# def get_id_pair_by_id(_id):
#     """Get a pair by ID"""
#     pair = IDPair.query.get_or_404(id)
#     return jsonify(data=pair.to_dict()), 200


@api.get('/id_pairs/model/<int:model_id>/<int:_id>')
@jwt_required()
def get_id_pair_in_model(model_id: int, _id: int):
    """Get a list of ID pairs in the given model"""
    try:
        model_found(model_id)
    except NotFoundException as error:
        return jsonify(msg=error), 404

    pair = IDPair.query.get_or_404(_id)
    return jsonify(data=pair.to_dict()), 200


@api.get('/id_pairs/model/<int:model_id>')
@jwt_required()
def list_id_pairs_in_model(model_id: int):
    """Get a list of ID pairs in the given model"""
    try:
        model_found(model_id)
    except NotFoundException as error:
        return jsonify(msg=error), 404

    id_pairs = IDPair.query.filter_by(uml_model_id=model_id).all()
    return jsonify(data=[pair.to_dict() for pair in id_pairs]), 200


@api.post('/id_pairs/model/<int:model_id>')
@jwt_required()
def add_id_pair_in_model(model_id: int):
    """Add new id pair"""
    try:
        model_found(model_id)
    except NotFoundException as error:
        return jsonify(msg=error), 404

    pair = {
        'class_id': request.json.get("class_id"),
        'table_id': request.json.get("table_id"),
        'uml_model_id': model_id
    }

    same_pair = IDPair.query.filter_by(**pair, uml_model_id=model_id).first()
    if same_pair is not None:
        return jsonify(msg="Pair already exists"), 400

    new_pair = create_id_pair(**pair)
    return jsonify(data=new_pair.to_dict()), 201


@api.delete('/id_pairs/model/<int:model_id>/<int:pair_id>')
@jwt_required()
def delete_id_pair_in_model(model_id: int, pair_id: int):
    """Route for deleting a pair"""
    try:
        model_found(model_id)
        pair: IDPair = IDPair.query.get_or_404(pair_id)
        delete_id_pair(pair)
    except NotFoundException as error:
        return jsonify(msg=error), 404
    except IntegrityError as error:
        return jsonify(msg=error), 400

    return "", 204


@api.get('/table_id/model/<int:model_id>/<class_id>')
@jwt_required()
def get_table_id(model_id: int, class_id: str):
    """Get table ID from Baserow that is connected to the class with given ID"""
    try:
        model_found(model_id)
        table_id = find_table_id_for_class(model_id, class_id)
    except NotFoundException as error:
        return jsonify(msg=error), 404

    return jsonify(data=table_id), 200


@api.get('/class_id/model/<int:model_id>/<int:table_id>')
@jwt_required()
def get_class_id(model_id: int, table_id: int):
    """Get class ID from UML class diagram that is connected to the table with given ID"""
    try:
        model_found(model_id)
        class_id = find_class_id_for_table(model_id, table_id)
    except NotFoundException as error:
        return jsonify(msg=error), 404

    return jsonify(data=class_id), 200
