from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, flash, jsonify

from models import db, User, Video, Like, Comment, DisLike
import os
from moviepy.editor import VideoFileClip
from PIL import Image
import random
import string
from markupsafe import Markup
from werkzeug.utils import secure_filename
import base64
from flask import current_app as app
from fuzzywuzzy import fuzz, process
from os import system as s

s('cls')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'src/static/videos')
app.config['THUMBNAIL_FOLDER'] = os.path.join(app.root_path, 'static/thumbnails')
app.config['ICONS_FOLDER'] = os.path.join(app.root_path, 'static/avatars')
app.config['AVATARS_FOLDER'] = os.path.join(app.root_path, 'static/avatars/users')
app.config['VIDEOS_FOLDER'] = os.path.join(app.root_path, 'static/videos')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024 * 1024  # 8GB
app.secret_key = 'your_secret_key'  # Замените на ваш случайный секретный ключ
admin_secret_key = "123"  # Секретный ключ для админ-панели
db.init_app(app)

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_thumbnail(video_path, thumbnail_path):
    """
    Генерирует миниатюру видео, сохраняя ее в нужном размере и соотношении сторон.

    Args:
        video_path (str): Путь к видеофайлу.
        thumbnail_path (str): Путь для сохранения миниатюры.
    """
    video = VideoFileClip(video_path)

    frame = video.get_frame(t=0.0)
    image = Image.fromarray(frame)

    width, height = image.size

    # Обрезка для сохранения соотношения 16:9
    if width / height != 16 / 9:
        # Вычисляем целевую ширину, чтобы получить соотношение 16:9
        if width > height:
            crop_width = width
            crop_height = int(crop_width * 9 / 16)
        else:
            crop_height = height
            crop_width = int(crop_height * 16 / 9)

        # Вычисляем разницу в ширине и высоте
        width_diff = width - crop_width
        height_diff = height - crop_height

        # Вычисляем смещения для обрезки
        left_offset = width_diff // 2
        top_offset = height_diff // 2

        # Обрезка изображения
        left = left_offset
        right = left + crop_width
        top = top_offset
        bottom = top + crop_height

        image = image.crop((left, top, right, bottom))
    
    # Сжатие, если необходимо
    if width > 1280 or height > 720:
        new_width = 1280
        new_height = int(new_width * 9 / 16)

        image = image.resize((new_width, new_height), Image.LANCZOS)  # Используем LANCZOS для лучшего качества сжатия

    # Сохранение миниатюры
    image.save(thumbnail_path)


def generate_random_name(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def get_current_user():
    user_id = session.get('user_id')
    if user_id is not None:
        return User.query.get(user_id)
    return None


@app.route('/', methods=['GET', 'POST'])
def index():
    current_user = get_current_user()
    videos = Video.query.order_by(Video.likes.desc()).all()
    search_results = []

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            app.logger.debug(f"Search query: {search_query}")
            matches = process.extract(search_query, [video.title for video in videos], scorer=fuzz.token_sort_ratio)
            app.logger.debug(f"FuzzyWuzzy matches: {matches}")
            search_results = [video for video, score in matches if score >= 20]
            search_results = [Video.query.filter_by(
                title=video.title if isinstance(video.title, str) else str(video.title)).first() for video in
                             search_results]
            search_results = [video for video in search_results if video is not None]

    return render_template('index.html',
                           videos=videos,
                           search_results=search_results,
                           Markup=Markup,
                           current_user=current_user)

@app.route('/base', methods=['GET', 'POST'])
def base():
    current_user = get_current_user()

    return render_template('base.html',
                           Markup=Markup,
                           current_user=current_user)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    current_user = get_current_user()
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description'][:500]  # Обрезаем описание до 500 символов
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = generate_random_name() + ".mp4"
                video_path = os.path.join('src/static/videos', filename)
                app.logger.debug(f"Saving file to: {video_path}")
                file.save(video_path)
                thumbnail_path = os.path.join('src/static/thumbnails', filename[:-4] + ".jpg")
                generate_thumbnail(video_path, thumbnail_path)
                user_id = session['user_id']
                new_video = Video(title=title, url=filename, description=description, user_id=user_id)
                db.session.add(new_video)
                db.session.commit()
                return redirect(url_for('channel', username=User.query.get(user_id).username))
        return render_template('upload.html', current_user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/video/<video_name>')
def video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    current_user = get_current_user()

    related_videos = Video.query.filter(Video.id != video.id).limit(9).all()

    return render_template('video.html',
                           video=video,
                           Markup=Markup,
                           current_user=current_user,
                           related_videos=related_videos)


@app.route('/subscribe/<int:user_id>', methods=['POST'])
def subscribe(user_id):
    user = get_current_user()
    if user:
        user_to_subscribe = User.query.get(user_id)
        user.subscribed_to.append(user_to_subscribe)
        db.session.commit()
        new_count = user_to_subscribe.subscribers.count()  # Получаем обновленное количество
        return jsonify({'status': 'success', 'subscribed': True, 'subscribers': new_count})
    return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

@app.route('/unsubscribe/<int:user_id>', methods=['POST'])
def unsubscribe(user_id):
    user = get_current_user()
    if user:
        user_to_unsubscribe = User.query.get(user_id)
        user.subscribed_to.remove(user_to_unsubscribe)
        db.session.commit()
        new_count = user_to_unsubscribe.subscribers.count()  # Получаем обновленное количество
        return jsonify({'status': 'success', 'subscribed': False, 'subscribers': new_count})
    return jsonify({'status': 'error', 'message': 'User not logged in'}), 401



@app.route('/static/videos/<path:filename>')
def serve_videos(filename):
    return send_from_directory(app.config['VIDEOS_FOLDER'], filename)


@app.route('/static/thumbnails/<path:filename>')
def serve_thumbnails(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)


@app.route('/static/avatars/<path:filename>')
def serve_icons(filename):
    return send_from_directory(app.config['ICONS_FOLDER'], filename)

@app.route('/static/avatars/users/<path:filename>')
def serve_avatars(filename):
    return send_from_directory(app.config['AVATARS_FOLDER'], filename)

@app.route('/like/<video_name>')
def like_video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    user = get_current_user()
    if user:
        existing_like = Like.query.filter_by(user_id=user.id, video_id=video.id).first()
        existing_dislike = DisLike.query.filter_by(user_id=user.id, video_id=video.id).first()

        if existing_like:
            # Убираем лайк
            db.session.delete(existing_like)
            video.likes -= 1
        else:
            # Ставим лайк
            if existing_dislike:
                # Убираем дизлайк
                db.session.delete(existing_dislike)
                video.dislikes -= 1
            new_like = Like(user_id=user.id, video_id=video.id)
            db.session.add(new_like)
            video.likes += 1

        db.session.commit()

    return redirect(url_for('video', video_name=video_name))


@app.route('/dislike/<video_name>')
def dislike_video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    user = get_current_user()
    if user:
        existing_like = Like.query.filter_by(user_id=user.id, video_id=video.id).first()
        existing_dislike = DisLike.query.filter_by(user_id=user.id, video_id=video.id).first()

        if existing_dislike:
            # Убираем дизлайк
            db.session.delete(existing_dislike)
            video.dislikes -= 1
        else:
            # Ставим дизлайк
            if existing_like:
                # Убираем лайк
                db.session.delete(existing_like)
                video.likes -= 1
            new_dislike = DisLike(user_id=user.id, video_id=video.id)
            db.session.add(new_dislike)
            video.dislikes += 1

        db.session.commit()

    return redirect(url_for('video', video_name=video_name))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Неверный логин или пароль")
    current_user = get_current_user()
    return render_template('login.html', current_user=current_user)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Пользователь с таким именем уже существует")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    current_user = get_current_user()
    return render_template('register.html', current_user=current_user)


@app.route('/channel/<username>')
def channel(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).all()
    current_user = get_current_user()
    if current_user:
        avatar = current_user.avatar
    else:
        avatar = None
    return render_template('channel.html', user=user, videos=videos, avatar=avatar, Markup=Markup,
                           current_user=current_user)

@app.route('/channel/<username>/avatar', methods=['GET', 'POST'])  # Используем один маршрут
def upload_avatar(username):
    user = User.query.filter_by(username=username).first_or_404()
    current_user = get_current_user()
    if request.method == 'POST':
        avatar = request.files.get('avatar')

        if avatar and allowed_file(avatar.filename):
            filename = f"{user.username}_avatar.{avatar.filename.rsplit('.', 1)[1]}"
            avatar.save(os.path.join(app.config['AVATARS_FOLDER'], filename))
            user.avatar = filename
            db.session.commit()
            flash('Аватар успешно обновлен!', 'success')
    return redirect(url_for('channel', username=username, user=user, current_user=current_user)) 

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    current_user = get_current_user()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        avatar = request.files.get('avatar')

        user.username = username
        if password:
            user.password = password
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(app.config['AVATARS_FOLDER'], filename))
            user.avatar = filename

        # Добавление/удаление подписчиков
        add_subscriber = request.form.get('add_subscriber')
        remove_subscriber = request.form.get('remove_subscriber')
        if add_subscriber:
            subscriber = User.query.filter_by(username=add_subscriber).first()
            if subscriber and subscriber not in user.subscribers:
                user.subscribers.append(subscriber)
        if remove_subscriber:
            subscriber = User.query.filter_by(username=remove_subscriber).first()
            if subscriber and subscriber in user.subscribers:
                user.subscribers.remove(subscriber)

        # Удаление видео
        delete_video_id = request.form.get('delete_video_id')
        if delete_video_id:
            video_to_delete = Video.query.get(int(delete_video_id))
            if video_to_delete and video_to_delete.author == user:
                db.session.delete(video_to_delete)

                # Удаляем файл видео и миниатюру
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_to_delete.url)
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], video_to_delete.url[:-4] + ".jpg")
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

        db.session.commit()
        flash('Пользователь успешно обновлен!', 'success')
        return redirect(url_for('administration'))

    return render_template('edit_user.html', user=user, current_user=current_user)

@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    current_user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        video.title = title
        video.description = description
        db.session.commit()
        flash('Видео успешно обновлено!', 'success')
        return redirect(url_for('administration'))

    return render_template('edit_video.html', video=video, current_user=current_user)

@app.route('/administration', methods=['GET', 'POST'])
def administration():
    if request.method == 'POST':
        entered_key = request.form.get('admin_key')
        if entered_key == admin_secret_key:
            users = User.query.all()
            videos = Video.query.all()
            return render_template('Administration.html', users=users, videos=videos)
        else:
            return "Неверный пароль!"
    return render_template('admin_login.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)