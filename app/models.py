from app import db
from app.auth import login_manager
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    contacts = db.relationship('Contact', backref='user', lazy=True)
    news = db.relationship('News', backref='user', lazy=True)

    def __init__(self, username, active):
        self.username = username
        self.active = active

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    text = db.Column(db.String(128), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, username, text, image):
        self.username = username
        self.text = text
        self.image = image


class Avatar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, image):
        self.image = image


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    message = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, message):
        self.username = username
        self.email = email
        self.message = message


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stat = db.Column(db.String(256), nullable=False)

    def __init__(self, stat):
        self.stat = stat
