"""CRUD operations on files"""
import os
from flask import jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api import api
from app import upload_dir
import app.xmi_reader as xr
# import app.api.error

UPLOAD_DIR = upload_dir['path']

@api.get("/files")
@jwt_required()
def list_files():
    """Endpoint to list files on the server."""
    files = []
    new_upload_dir = f"{UPLOAD_DIR}/user-{get_jwt_identity()}"
    for filename in os.listdir(new_upload_dir):
        path = os.path.join(new_upload_dir, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(data=files), 200


@api.get("/files/<filename>")
@jwt_required()
def get_file(filename):
    """Download a file."""
    path = os.path.join(f"{UPLOAD_DIR}/user-{get_jwt_identity()}", filename)
    if not os.path.isfile(path):
        return jsonify(msg="Could not find file"), 404
    return send_from_directory(
        f"{UPLOAD_DIR}/user-{get_jwt_identity()}",
        filename,
        as_attachment=True), 200


@api.put("/files/<filename>")
@jwt_required()
def put_file(filename):
    """Upload a file."""
    path_to_filename = f"{UPLOAD_DIR}/user-{get_jwt_identity()}"
    if not os.path.exists(path_to_filename):
        os.makedirs(path_to_filename)

    if "/" in filename:
        return jsonify(msg="No subdirectories allowed"), 400

    if filename[-4:] != ".xmi":
        return jsonify(msg="Invalid file type"), 400

    path = os.path.join(path_to_filename, filename)
    with open(path, "wb") as file:
        file.write(request.data)

    return jsonify(msg="File added"), 200


@api.patch("/files/<filename>")
@jwt_required()
def rename_file(filename):
    """Rename a file"""
    new_filename = request.json.get("new_filename")
    path_to_filename = f"{UPLOAD_DIR}/user-{get_jwt_identity()}"
    path = os.path.join(path_to_filename, filename)
    if not os.path.isfile(path):
        return jsonify(msg="Could not find file"), 404
    new_file = os.path.join(path_to_filename, new_filename)
    os.rename(path, new_file)
    return jsonify(msg="File successfully renamed"), 200


@api.delete("/files/<filename>")
@jwt_required()
def delete_file(filename):
    """Delete a file"""
    path = os.path.join(f"{UPLOAD_DIR}/user-{get_jwt_identity()}", filename)
    if not os.path.isfile(path):
        return jsonify(msg="Could not find file"), 404
    os.remove(path)
    return "", 204


@api.get('/xmi_read/files/<filename>')
@jwt_required()
def read_xmi_file(filename):
    """Get Database attributes"""
    path_to_filename = f"{UPLOAD_DIR}/user-{get_jwt_identity()}"
    path = os.path.join(path_to_filename, filename)
    if not os.path.isfile(path):
        return jsonify(msg="Could not find file"), 404
    packaged_elements = xr.get_packaged_elements(get_jwt_identity(), filename)
    data = {}
    data['classes'] = xr.get_classes(packaged_elements)
    data['data_types'] = xr.get_data_types(packaged_elements)
    data['enumerations'] = xr.get_enumerations(packaged_elements)
    data['associations'] = xr.get_associations(data['classes'])
    data['attributes'] = xr.get_attributes(
        data['classes'],
        data['data_types'],
        data['enumerations'])

    data['classes'] = list(data['classes'])
    return jsonify(data=data), 200
