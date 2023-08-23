from app import app, db
from app.models import User, News, Contact
from flask_login import login_user
from flask import render_template, request, redirect, url_for, session


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
        session['username'] = request.form['username']
        text = request.form.get('text')
        new_text = News(username=session['username'], text=text)
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for('news'))
    news_list = News.query.all()
    return render_template("news.html", news=news_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        user = User.query.filter_by(username=session['username']).first()
        if user and user.check_password(session['password']):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            new_user = User(username=session['username'])
            new_user.set_password(session['password'])
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/action')
def action():
    return render_template('action.html')


@app.route('/contactus')
def contactus():
    return render_template('contactus.html')


@app.route('/contactus', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        message = request.form.get('message')
        new_contact_us = Contact(username=username, email=email, message=message)
        db.session.add(new_contact_us)
        db.session.commit()
        return redirect(url_for('contactus'))
    return render_template('contactus.html')


@app.route('/addart')
def addart():
    return render_template('addart.html')


