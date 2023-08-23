from app import app, db
from app.models import User, News, Contact
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users', methods=['GET'])
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    if request.method == 'POST':
        text = request.form.get('text')
        new_text = News(current_user.username, text=text)
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for('news'))
    news_list = News.query.all()
    return render_template("news.html", news=news_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, active=True)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        new_contact_us = Contact(username=current_user.username, email=email, message=message)
        db.session.add(new_contact_us)
        db.session.commit()
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/addart')
@login_required
def addart():
    return render_template('addart.html')
