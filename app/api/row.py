"""Module for creating CRUD operations on table rows"""
import requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import UMLModel

BASEROW_TABLE_URL = "https://api.baserow.io/api/database/tables/database"
BASEROW_ROW_URL = "https://api.baserow.io/api/database/rows/table"


def get_table_id(baserow_token, database_id, table_name):
    """Get table id by name"""
    res = requests.get(
        f"{BASEROW_TABLE_URL}/{database_id}/",
        headers={'Authorization': f'JWT {baserow_token}'},
        timeout=None
    )
    if res.status_code != 200:
        return None

    data = res.json()['data']
    table_id = [table['id'] for table in data if table['name'] == table_name][0]
    return table_id


@api.get('/models/<model_id>/tables')
@jwt_required()
def get_all_tables(model_id):
    """Get all tables of a given model"""
    model = UMLModel.query.get_or_404(model_id)
    res = requests.get(
        f"{BASEROW_TABLE_URL}/{model.database_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )
    if res.status_code != 200:
        return None

    data = res.json()['data']
    return data, 200


@api.get('/models/<model_id>/tables/<table_name>')
@jwt_required()
def get_table_id_by_name(model_id, table_name):
    """Get table id by name"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    return jsonify(data=table_id), 200


@api.get('/models/<model_id>/data/<table_name>')
@jwt_required()
def get_all_table_rows(model_id, table_name):
    """Get all table data"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    response = requests.get(
        f"{BASEROW_ROW_URL}/{table_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        params=request.params,
        timeout=None
    )
    if response.status_code != 200:
        return jsonify(msg="Something went wrong"), response.status_code
    return jsonify(response.json()), 204


@api.get('/models/<model_id>/tables/<table_name>/<row_id>')
@jwt_required()
def get_row_by_id(model_id, table_name, row_id):
    """Get a row by id"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    response = requests.get(
        f"{BASEROW_ROW_URL}/{table_id}/{row_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )
    if response.status_code != 200:
        return jsonify(msg="Something went wrong"), response.status_code
    return jsonify(response.json()), 204


@api.post('/models/<model_id>/data/<table_name>')
@jwt_required()
def create_row(model_id, table_name):
    """Create a new row"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    response = requests.post(
        f"{BASEROW_ROW_URL}/{table_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        json=request.json,
        params=request.params,
        timeout=None
    )
    if response.status_code != 200:
        return jsonify(msg="Something went wrong"), response.status_code
    return jsonify(response.json()), 201


@api.patch('/models/<model_id>/tables/<table_name>/<row_id>')
@jwt_required()
def update_row(model_id, table_name, row_id):
    """Update a row"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    response = requests.patch(
        f"{BASEROW_ROW_URL}/{table_id}/{row_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        json=request.json,
        params=request.params,
        timeout=None
    )
    if response.status_code != 200:
        return jsonify(msg="Something went wrong"), response.status_code
    return jsonify(response.json()), 200


@api.delete('/models/<model_id>/tables/<table_name>/<row_id>')
@jwt_required()
def delete_row(model_id, table_name, row_id):
    """Delete a row"""
    model = UMLModel.query.get_or_404(model_id)
    table_id = get_table_id(model.baserow_token, model.database_id, table_name)
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    response = requests.delete(
        f"{BASEROW_ROW_URL}/{table_id}/{row_id}/",
        headers={'Authorization': f'JWT {model.baserow_token}'},
        params=request.params,
        timeout=None
    )
    if response.status_code != 204:
        return jsonify(msg="Something went wrong"), response.status_code
    return "", 204
