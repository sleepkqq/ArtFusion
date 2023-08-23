from app import db
from app.auth import login_manager
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    contacts = db.relationship('Contact', backref='user', lazy=True)

    def __init__(self, username, active):
        self.username = username
        self.active = active

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    text = db.Column(db.String(128), nullable=False)

    def __init__(self, username, text):
        self.username = username
        self.text = text


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    message = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, message):
        self.username = username
        self.email = email
        self.message = message

