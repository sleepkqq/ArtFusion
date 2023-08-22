from app import db
from app.auth import login_manager
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()


#asdasda
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text