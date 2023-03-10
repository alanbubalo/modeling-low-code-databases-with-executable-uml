"""API Initialization"""
from flask import Blueprint

api = Blueprint('api', __name__)

# Initialize modules
from app.api import test
from app.api import token
from app.api import user
from app.api import files
from app.api import uml_model
from app.api import row