"""Module for creating CRUD operations on ID pairs"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app.api import api
from app.models import IDPair, UMLModel
from app import db


def model_found(user_id: int, model_id: int) -> bool:
    """Check if the model exists for the specified user"""
    model = UMLModel.query.filter_by(user_id=user_id, id=model_id).first()
    return model is not None


def delete_id_pair_in_model(pair: IDPair) -> bool:
    """Delete ID pair"""
    try:
        db.session.delete(pair)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return False
    return True


def create_id_pair_in_model(pair: dict, model_id: int) -> IDPair:
    """Create ID pair in model"""
    new_pair = IDPair(**pair, uml_model_id=model_id)
    db.session.add(new_pair)
    db.commit()
    return new_pair

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
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    pair = IDPair.query.get_or_404(_id)
    return jsonify(data=pair.to_dict()), 200


@api.get('/id_pairs/model/<int:model_id>')
@jwt_required()
def list_id_pairs_in_model(model_id: int):
    """Get a list of ID pairs in the given model"""
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    id_pairs = IDPair.query.filter_by(uml_model_id=model_id).all()
    return jsonify(data=[pair.to_dict() for pair in id_pairs]), 200


@api.post('/id_pairs/model/<int:model_id>')
@jwt_required()
def add_id_pair(model_id: int):
    """Add new id pair"""
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    pair = {
        'class_id': request.json.get("class_id"),
        'table_id': request.json.get("table_id"),
    }

    same_pair = IDPair.query.filter_by(**pair, uml_model_id=model_id).first()
    if same_pair is not None:
        return jsonify(msg="Pair already exists"), 400

    new_pair = create_id_pair_in_model(pair, model_id)
    return jsonify(data=new_pair.to_dict()), 201


@api.delete('/id_pairs/model/<int:model_id>/<int:pair_id>')
@jwt_required()
def delete_id_pair(model_id: int, pair_id: int):
    """Route for deleting a pair"""
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    pair: IDPair = IDPair.query.get_or_404(pair_id)
    if not delete_id_pair_in_model(pair):
        return jsonify(msg="Integrity error"), 400
    return "", 204


@api.get('/table_id/model/<int:model_id>/<class_id>')
@jwt_required()
def get_table_id(model_id: int, class_id: str):
    """Get table ID from Baserow that is connected to the class with given ID"""
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    found_id_pair = IDPair.query.filter_by(
        class_id=class_id,
        uml_model_id=model_id
    ).first()

    if found_id_pair is None:
        return jsonify(msg="Id pair not found"), 404
    return jsonify(data=found_id_pair.table_id), 200


@api.get('/class_id/model/<int:model_id>/<int:table_id>')
@jwt_required()
def get_class_id(model_id: int, table_id: int):
    """Get class ID from UML class diagram that is connected to the table with given ID"""
    if not model_found(get_jwt_identity(), model_id) is None:
        return jsonify(msg="Model not found"), 404

    found_id_pair = IDPair.query.filter_by(
        table_id=table_id,
        uml_model_id=model_id
    ).first()

    if found_id_pair is None:
        return jsonify(msg="Id pair not found"), 404
    return jsonify(data=found_id_pair.class_id), 200
