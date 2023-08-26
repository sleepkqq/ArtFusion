from io import BytesIO
from app import app, db
from app.models import User, News, Contact, Avatar, Status
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, send_file
from PIL import Image


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/all', methods=['GET'])
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/user/<int:id>')
@login_required
def user_profile(id):
    user = User.query.filter_by(id=id).first()
    news_list = News.query.filter_by(username=user.username).all()
    return render_template('user.html', user=user, current_user=current_user, news=news_list)


@app.route('/status/<int:id>', methods=['GET', 'POST'])
@login_required
def set_user_status(id):
    status = request.form.get('status')
    user = User.query.filter_by(id=id).first()
    if current_user.username == user.username and user:
        user.set_status(status)
        db.session.commit()
        return redirect('/user/' + str(id))
    return "User not found"


@app.route('/news', methods=['GET', 'POST'])
@login_required
def news():
    if request.method == 'POST':
        text = request.form.get('text')
        image = request.files['image'].read() if 'image' in request.files else None
        resized_image_data = resize_and_save_image(image)
        new_text = News(current_user.username, text=text, image=resized_image_data)
        db.session.add(new_text)
        db.session.commit()
    news_list = News.query.all()
    return render_template("news.html", news=news_list, current_user=current_user)


def resize_and_save_image(image_data, max_width=500, max_height=200):
    img = Image.open(BytesIO(image_data))
    img.thumbnail((max_width, max_height))
    output = BytesIO()
    img.save(output, format='JPEG')
    output.seek(0)
    return output.read()


@app.route('/image/<int:post_id>')
@login_required
def get_image(post_id):
    news_item = News.query.get(post_id)
    if news_item and news_item.image:
        return send_file(BytesIO(news_item.image), mimetype='image/jpeg')


@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    previous_url = request.referrer
    post = News.query.get(post_id)
    if post.username == current_user.username and post:
        db.session.delete(post)
        db.session.commit()
    return redirect(f"{previous_url}")


@app.route('/edit/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    post = News.query.get(post_id)
    previous_url = request.referrer
    if post and post.username == current_user.username:
        new_text = request.form.get('edit_text')
        post.text = new_text
        db.session.commit()
        return redirect(f"{previous_url}")


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
            return render_template('login.html', error="Invalid username or password!")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username=username, email=email, active=True)
        new_user.set_password(password)
        user = User.query.filter_by(username=username).first()
        mail = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', error="This name is already in use. Please choose another.")
        if mail:
            return render_template('register.html', error="This email is already in use. Please choose another.")
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
        message = request.form.get('message')
        con = Contact.query.filter_by(message=message).first()
        new_contact_us = Contact(username=current_user.username, email=current_user.email, message=message)
        if not con:
            return render_template('contact.html', error="Thank You!")
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
