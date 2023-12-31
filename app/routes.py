from io import BytesIO
from app import app, db
from app.models import User, Post, Contact, Like
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, send_file, send_from_directory, jsonify
from PIL import Image


@app.route('/users', methods=['GET'])
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/<int:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    current_user_likes = [like.post_id for like in current_user.likes]
    return render_template('user.html',
                           user=user,
                           current_user_likes=current_user_likes)


@app.route('/', methods=['GET'])
@login_required
def main_page():
    posts = Post.query.all()
    reversed_posts = list(reversed(posts))
    current_user_likes = [like.post_id for like in current_user.likes]
    success = request.args.get('success')
    return render_template('index.html',
                           posts=reversed_posts,
                           current_user_likes=current_user_likes,
                           success=success)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        text = request.form.get('text')
        image = request.files['image'].read() if 'image' in request.files else None
        resized_image_data = resize_and_save_image(image)
        post = Post(current_user.username, text=text, image=resized_image_data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main_page', success=True))
    return render_template('create.html')


def resize_and_save_image(image_data, target_size_kb=64):
    if not image_data:
        return None

    width, height = Image.open(BytesIO(image_data)).size

    while len(image_data) > target_size_kb * 1024:
        width = int(width * 0.9)
        height = int(height * 0.9)

        output = BytesIO()
        image = Image.open(BytesIO(image_data))
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        image.save(output, format='JPEG')
        image_data = output.getvalue()

    return image_data


@app.route('/status/<int:user_id>', methods=['POST'])
@login_required
def set_user_status(user_id):
    status = request.form.get('status')
    user = User.query.get(user_id)
    if current_user.id == user_id and user:
        user.set_status(status)
        db.session.commit()
        return redirect(request.referrer)
    return '404 Not found'


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get(post_id)
    if current_user.id not in [like.user_id for like in post.likes]:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/unlike/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/image/<int:post_id>', methods=['GET'])
@login_required
def get_image(post_id):
    post = Post.query.get(post_id)
    if post and post.image:
        return send_file(BytesIO(post.image), mimetype='image/jpeg')


@app.route('/avatar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def avatar(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST' and current_user.id == user_id:
        image = request.files['image'].read() if 'image' in request.files else None
        resized_image_data = resize_and_save_image(image)
        user.avatar = resized_image_data
        db.session.commit()
        return redirect(url_for('user_profile', user_id=user_id))
    if user:
        if user.avatar:
            return send_file(BytesIO(user.avatar), mimetype='image/jpeg')
        else:
            return send_from_directory('static', 'user-Male.png')
    else:
        return '404 Not found'


@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post.username == current_user.username and post:
        for like in post.likes:
            db.session.delete(like)
        db.session.delete(post)
        db.session.commit()
    return redirect(request.referrer)


@app.route('/edit/<int:post_id>', methods=['POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if post and post.username == current_user.username:
        new_text = request.form.get('edit_text')
        post.text = new_text
        db.session.commit()
        return redirect(request.referrer)
    return '404 Not found'


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    if query:
        post_results = Post.query.filter(Post.text.contains(query)).all()
        user_results = User.query.filter(User.username.contains(query)).all()
    else:
        post_results = []
        user_results = []
    current_user_likes = [like.post_id for like in current_user.likes]
    return render_template('index.html',
                           posts=post_results,
                           query=query,
                           current_user_likes=current_user_likes,
                           users=user_results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main_page'))
        else:
            return render_template('login.html', error='Invalid username or password!')
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
        if user or mail:
            error_message = 'This name is already in use. Please choose another.'\
                if user else 'This email is already in use. Please choose another.'
            return render_template('register.html', error=error_message)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('main_page'))
    return render_template('register.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        message = request.form.get('message')
        new_contact_us = Contact(username=current_user.username, email=current_user.email, message=message)
        db.session.add(new_contact_us)
        db.session.commit()
        return render_template('contact.html', notification='Thank You!')
    return render_template('contact.html')
