"""
Module for creating CRUD operations on UML models.

"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app import db
from app.api import api
from app.models import IDPair, UMLModel
from app.baserow_init import (
    create_baserow_database,
    # update_baserow_database,
    delete_baserow_database
)
# from app.api.id_pair import model_found, delete_id_pair_in_model, create_id_pair_in_model
from app.exc import (
    NotFoundException,
    NotAuthorizedException,
    InvalidGroupException,
    InvalidDatabaseException,
    BadFieldException,
    DeletingDatabasesException
)
from app.id_pairs_utils import delete_id_pair, model_found

# def generate_db(model):
#     """Helper function to generate database"""
#     id_pairs = IDPair.query.filter_by(uml_model_id=model.id).all()
#     id_pairs = [pair.to_dict() for pair in id_pairs]
#     return create_baserow_database(
#         model.user_id,
#         model.group_id,
#         model.baserow_token,
#         model.database_name,
#         model.filename,
#         id_pairs
#     )


# def update_db(model):
#     """Helper function to update database"""
#     id_pairs = IDPair.query.filter_by(uml_model_id=model.id).all()
#     id_pairs = [pair.to_dict() for pair in id_pairs]
#     return update_baserow_database(
#         model.user_id,
#         model.group_id,
#         model.baserow_token,
#         model.database_id,
#         model.filename,
#         id_pairs
#     )


# def refresh_list_id_pairs_in_model(
#     user_id: int,
#     model_id: int,
#     id_pairs_input: list[dict]
# ) -> tuple | None:
#     """Refresh list of ID pairs in the given model"""
#     if not model_found(user_id, model_id):
#         return jsonify(msg="Model not found"), 404

#     id_pairs_database = IDPair.query.filter_by(uml_model_id=model_id).all()
#     for pair in id_pairs_database:
#         if not delete_id_pair_in_model(pair):
#             return jsonify(msg="Integrity error"), 400

#     for pair in id_pairs_input:
#         # Check if pair already exists
#         print("test1")
#         same_pair = IDPair.query.filter_by(**pair, uml_model_id=model_id).first()
#         print("test2")
#         if same_pair is not None:
#             return jsonify(msg="Pair already exists"), 400
#         print("test3")
#         pair['uml_model_id'] = model_id
#         create_id_pair_in_model(pair)
#         print("test4")
#     return None


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
    try:
        model = model_found(model_id)
    except NotFoundException:
        return jsonify(msg="Model not found"), 404

    return jsonify(data=model.to_dict()), 200


@api.post('/models')
@jwt_required()
def post_model():
    """Create a new one"""
    model_dict = {
        'user_id': get_jwt_identity(),
        'database_url': request.json.get('database_url', 'https://api.baserow.io'),
        'baserow_token': request.json.get('baserow_token'),
        'group_id': request.json.get('group_id'),
        'filename': request.json.get('filename'),
        'database_name': request.json.get('database_name'),
    }
    model = UMLModel(**model_dict)
    try:
        db.session.add(model)
        db.session.commit()

        database_id = create_baserow_database(model)

        print("Database created successfully:", database_id)
        # print("ID pairs:")
        # print(id_pairs)

        # Add database id after it was created
        model.database_id = database_id
        db.session.commit()
        # response = refresh_list_id_pairs_in_model(model.user_id, model.id, id_pairs)
        # if response:
        #     return response
    except NotAuthorizedException:
        db.session.rollback()
        return jsonify(msg="Unauthorized to connect to Baserow"), 403
    except InvalidGroupException:
        db.session.rollback()
        return jsonify(msg="Baserow group invalid"), 400
    except InvalidDatabaseException:
        db.session.rollback()
        return jsonify(msg="Baserow database invalid"), 400
    except BadFieldException:
        db.session.rollback()
        return jsonify(msg="Error while creating a field"), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Integrity error"), 400

    return jsonify(data=model.to_dict()), 201


@api.patch('/models/<model_id>')
@jwt_required()
def update_model(model_id):
    """Update model information"""
    try:
        model = model_found(model_id)
    except NotFoundException:
        return jsonify(msg="Model not found"), 404

    body = request.json
    if body.get('baserow_token') is not None:
        model.baserow_token = body.get('baserow_token')
    # if body.get('database_id') is not None:
    #     model.database_id = body.get('database_id')
    # if body.get('database_name') is not None:
    #     model.database_name = body.get('database_name')
    # if body.get('database_url') is not None:
    #     model.database_url = body.get('database_url')
    # if body.get('filename') is not None:
    #     model.filename = body.get('filename')
    # if body.get('group_id') is not None:
    #     model.group_id = body.get('group_id')
    try:
        db.session.add(model)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(msg="Unable to update model"), 400

    return jsonify(data=model.to_dict()), 200


# @api.patch('models/<model_id>')
# @jwt_required()
# def upgrade_model(model_id):
#     """Upgrade a model"""
#     model = UMLModel.query.filter_by(id=model_id, user_id=get_jwt_identity()).first()
#     if not model:
#         return jsonify(msg="Model not found"), 404
#     try:
#         id_pairs = update_db(model)
#         response = refresh_list_id_pairs_in_model(model.user_id, model.id, id_pairs)
#         if response:
#             return response
#     except NotAuthorizedException:
#         db.session.rollback()
#         return jsonify(msg="Unauthorized to connect to Baserow"), 400
#     except InvalidGroupException:
#         db.session.rollback()
#         return jsonify(msg="Baserow group invalid"), 400
#     except InvalidDatabaseException:
#         db.session.rollback()
#         return jsonify(msg="Baserow database invalid"), 400
#     except BadFieldException:
#         db.session.rollback()
#         return jsonify(msg="Error while creating a field"), 400
#     return jsonify(msg="Model upgraded"), 200


@api.delete('/models/<model_id>')
@jwt_required()
def delete_model(model_id):
    """Delete a model by ID"""
    try:
        model = model_found(model_id)
        db.session.delete(model)
        db.session.commit()
        delete_baserow_database(model)
        id_pairs = IDPair.query.filter_by(uml_model_id=model_id).all()
        for pair in id_pairs:
            delete_id_pair(pair)
        # response = refresh_list_id_pairs_in_model(get_jwt_identity(), model.id, [])
        # if response[1] != 200:
        #    return response[0]
    except NotFoundException:
        return jsonify(msg="Model not found"), 404
    except DeletingDatabasesException:
        db.session.rollback()
        return jsonify(msg="Unable to delete model"), 400

    return "", 204
