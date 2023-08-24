from io import BytesIO
from app import app, db
from app.models import User, News, Contact, Avatar, Status
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, send_file



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/all', methods=['GET'])
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@login_required
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id).first()
    return render_template('user.html', user=user)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    if request.method == 'POST':
        text = request.form.get('text')
        image = request.files['image'].read() if 'image' in request.files else None
        new_text = News(current_user.username, text=text, image=image)
        db.session.add(new_text)
        db.session.commit()
        return redirect(url_for('news'))

    news_list = News.query.all()
    return render_template("news.html", news=news_list)


@app.route('/avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    if request.method == 'POST':
        image = request.files['image'].read() if 'image' in request.files else None
        new_avatar = Avatar(current_user.username, image=image)
        db.session.add(new_avatar)
        db.session.commit()
        return redirect(url_for('user'))

    ava = Avatar(current_user.username, image=image)
    return render_template("user.html", avatar=ava)


@app.route('/image/<int:post_id>')
@login_required
def get_image(post_id):
    news_item = News.query.get(post_id)
    if news_item and news_item.image:
        return send_file(BytesIO(news_item.image), mimetype='image/jpeg')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="НЕПРАВИЛЬНОЕ ИМЯ ПОЛЬЗОВАТЕЛЯ ИЛИ ПАРОЛЬ!")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, active=True)
        new_user.set_password(password)
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="ТАКОЕ ИМЯ ПОЛЬЗОВАТЕЛЯ УЖЕ СУЩЕСТВУЕТ!")
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


@app.route('/user', methods=['GET', 'POST'])
@login_required
def status():
    if request.method == 'POST':
        stat = request.form.get('stat')
        new_status = Status(stat=stat)
        db.session.add(new_status)
        db.session.commit()
        return redirect(url_for('user'))
    return render_template('user.html')
