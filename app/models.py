"""Models"""
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from app import db, bcrypt


class User(db.Model, SerializerMixin):
    """User from the database"""
    __tablename__ = 'user'
    serialize_only = ('id', 'name', 'email', 'date_added')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    _password = db.Column(db.String(256), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    uml_model = db.relationship('UMLModel', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @hybrid_property
    def password(self):
        """Password"""
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    def verify_password(self, password):
        """Check if the given password matches with the password hash of that user"""
        return bcrypt.check_password_hash(self._password, password)


class UMLModel(db.Model, SerializerMixin):
    """UML Model"""
    __tablename__ = 'uml_model'
    serialize_only = ('id', 'database_name', 'user_id', 'filename')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    database_url = db.Column(db.String(), nullable=False)
    database_name = db.Column(db.String(256), nullable=False)
    baserow_token = db.Column(db.String(256), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    database_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<UMLModel {self.id}>'


class IDPair(db.Model, SerializerMixin):
    """IDs of matching tables and classes"""
    __tablename__ = 'id_pair'
    serialize_only = ('id', 'class_id', 'table_id')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.String(64), nullable=True)
    table_id = db.Column(db.Integer, nullable=True)
    uml_model_id = db.Column(db.Integer, db.ForeignKey('uml_model.id'))

    def __repr__(self) -> str:
        return f'<IDMatch {self.id}>'


# class Log(db.Model, SerializerMixin):
#     """Log records of actions"""
#     __tablename__ = 'log'
#     serialize_only = ('id', 'user_id', 'uml_model', 'action', 'datetime')

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     uml_model = db.Column(db.Integer, db.ForeignKey('uml_model.id'))
#     pair_id = db.Column(db.Integer, db.ForeignKey('id_pair.id'))
#     action = db.Column(db.String(64), nullable=False)
#     datetime = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self) -> str:
#         return f'<Log {self.id}>'
