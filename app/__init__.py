"""
App initialization.

"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from app.baserow_client import BaserowClient

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
upload_dir = {
    'path': ''
}
client = BaserowClient()

def create_app(config_class):
    """Create a Flask application"""
    app = Flask(__name__)

    app.config.from_object(config_class) # 'app.config.DevConfig'
    upload_dir['path'] = app.config['UPLOAD_FOLDER']
    # print(app.config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # if not os.path.exists(app.config['UPLOAD_FOLDER']):
    #     os.makedirs(app.config['UPLOAD_FOLDER'])

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    app.app_context().push()

    return app
