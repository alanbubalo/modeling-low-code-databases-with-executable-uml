"""Module for creating CRUD operations on table rows"""
import requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.api import api
from app.models import UMLModel
from app.exc import BadRequestException


def get_table_id(database_url, baserow_token, database_id, table_name):
    """Get table id by name"""
    url = f"{database_url}/api/database/tables/database/{database_id}/"
    res = requests.get(
        url,
        headers={'Authorization': f'JWT {baserow_token}'},
        timeout=None
    )
    if res.status_code != 200:
        raise BadRequestException(res.json(), res.status_code)

    data = res.json()
    table_id = [table['id'] for table in data if table['name'] == table_name][0]
    return table_id


@api.get('/models/<model_id>/tables')
@jwt_required()
def get_all_tables(model_id):
    """Get all tables of a given model"""
    model = UMLModel.query.get_or_404(model_id)
    url = f"{model.database_url}/api/database/tables/database/{model.database_id}/"
    response = requests.get(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )

    return response.json(), response.status_code


@api.get('/models/<model_id>/tables/<table_name>')
@jwt_required()
def get_table_id_by_name(model_id, table_name):
    """Get table id by name"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code
    if table_id is None:
        return jsonify(msg="Table not found"), 404

    return jsonify(table_id=table_id), 200


@api.get('/models/<model_id>/tables/<table_name>')
@jwt_required()
def get_all_table_rows(model_id, table_name):
    """Get all table data"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code

    url = f"{model.database_url}/api/database/rows/table/{table_id}/"
    response = requests.get(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        params=request.query_string,
        timeout=None
    )

    return response.json(), response.status_code


@api.get('/models/<model_id>/data/<table_name>/<row_id>')
@jwt_required()
def get_row_by_id(model_id, table_name, row_id):
    """Get a row by id"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code

    url = f"{model.database_url}/api/database/rows/table/{table_id}/{row_id}/?user_field_names=true"
    response = requests.get(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )

    return response.json(), response.status_code


@api.post('/models/<model_id>/data/<table_name>')
@jwt_required()
def create_row(model_id, table_name):
    """Create a new row"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code

    url = f"{model.database_url}/api/database/rows/table/{table_id}/?user_field_names=true"
    response = requests.post(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        json=request.json,
        # params=request.query_string,
        timeout=None
    )

    return response.json(), response.status_code


@api.patch('/models/<model_id>/data/<table_name>/<row_id>')
@jwt_required()
def update_row(model_id, table_name, row_id):
    """Update a row"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code

    url = f"{model.database_url}/api/database/rows/table/{table_id}/{row_id}/?user_field_names=true"
    response = requests.patch(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        json=request.json,
        timeout=None
    )

    return response.json(), response.status_code


@api.delete('/models/<model_id>/data/<table_name>/<row_id>')
@jwt_required()
def delete_row(model_id, table_name, row_id):
    """Delete a row"""
    model = UMLModel.query.get_or_404(model_id)
    try:
        table_id = get_table_id(
            model.database_url,
            model.baserow_token,
            model.database_id,
            table_name)
    except BadRequestException as exc:
        return exc.json, exc.status_code

    url = f"{model.database_url}/api/database/rows/table/{table_id}/{row_id}/"
    response = requests.get(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )
    if response.status_code != 200:
        return response.json(), response.status_code
    # deleted_row = response.json()

    url = f"{model.database_url}/api/database/rows/table/{table_id}/{row_id}/"
    response = requests.delete(
        url,
        headers={'Authorization': f'JWT {model.baserow_token}'},
        timeout=None
    )

    if response.status_code != 204:
        return response.json(), response.status_code

    return "", response.status_code
