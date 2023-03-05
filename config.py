"""Flask configuration"""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config():
    """Base config."""
    APP_NAME = os.environ.get('APP_NAME', 'UML-to-Baserow')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key')
    # SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    UPLOAD_FOLDER = rf'{basedir}\files'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get('ACCESS_TOKEN_EXPIRES_DAYS', 2))
    )
    # JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('ACCESS_TOKEN_EXPIRES_DAYS', 2))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get('REFRESH_TOKEN_EXPIRES_DAYS', 30))
    )
    # JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('REFRESH_TOKEN_EXPIRES_DAYS', 30))


class ProductionConfig(Config):
    """Production config."""
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')


class DevelopmentConfig(Config):
    """Development config."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URI',
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    )
