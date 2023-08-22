from app import app, db
from app.models import User, News
from flask_login import login_user
from flask import render_template, request, redirect, url_for


#asdasda
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/users', methods=['GET'])
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST':
        text = request.form.get('text')
        new_text = News(text=text)
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for('news'))
    news_list = News.query.all()
    return render_template("news.html", news=news_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('login'))
    return render_template('register.html')
