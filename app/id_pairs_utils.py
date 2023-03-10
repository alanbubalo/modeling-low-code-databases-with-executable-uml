"""Utility functions for ID pairs"""
from flask_jwt_extended import get_jwt_identity
from app.models import UMLModel, IDPair
from app import db
from app.exc import NotFoundException


def model_found(model_id: int):
    """Check if the model exists for the specified user"""
    model = UMLModel.query.filter_by(user_id=get_jwt_identity(), id=model_id).first()
    if model is None:
        raise NotFoundException("Model not found")
    return model


def find_class_id_for_table(model_id: int, table_id: int) -> str:
    """Get class id for given table in model"""
    found_id_pair = IDPair.query.filter_by(
        table_id=table_id,
        uml_model_id=model_id
    ).first()

    if found_id_pair is None:
        raise NotFoundException("Id pair not found")
    return found_id_pair.class_id


def find_table_id_for_class(model_id: int, class_id: str) -> int:
    """Get table id for given class in model"""
    found_id_pair = IDPair.query.filter_by(
        class_id=class_id,
        uml_model_id=model_id
    ).first()

    if found_id_pair is None:
        raise NotFoundException("Id pair not found")
    return found_id_pair.table_id


def create_id_pair(class_id: str, table_id: int, uml_model_id: int) -> IDPair:
    """Create ID pair in model"""
    new_pair = IDPair(class_id=class_id, table_id=table_id, uml_model_id=uml_model_id)
    db.session.add(new_pair)
    db.session.commit()
    return new_pair


def delete_id_pair(pair: IDPair):
    """Delete ID pair"""
    db.session.delete(pair)
    db.session.commit()
    db.session.rollback()
