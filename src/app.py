# src/app.py
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from models import db, User, Video, Like, Comment
import os
from moviepy.editor import VideoFileClip
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'src/static/videos'
app.config['THUMBNAIL_FOLDER'] = 'src/static/thumbnails'
db.init_app(app)

def generate_thumbnail(video_path, thumbnail_path):
    video = VideoFileClip(video_path)
    video.save_frame(thumbnail_path, t=0.0)

def generate_random_name(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/')
def index():
    videos = Video.query.order_by(Video.likes.desc()).all()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files['file']
        if file:
            filename = generate_random_name() + ".mp4"  # Генерация случайного имени
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename[:-4] + ".jpg")
            generate_thumbnail(video_path, thumbnail_path)
            user_id = 1  # Замените на текущего пользователя
            new_video = Video(title=title, url=filename, description=description, user_id=user_id)
            db.session.add(new_video)
            db.session.commit()
            return redirect(url_for('channel', username=User.query.get(user_id).username))  # Переход на канал пользователя
    return render_template('upload.html')

@app.route('/video/<video_name>')
def video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    return render_template('video.html', video=video)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/thumbnails/<path:filename>')
def serve_thumbnails(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/like/<video_name>')
def like_video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    video.likes += 1
    db.session.commit()
    return redirect(url_for('video', video_name=video_name))

@app.route('/dislike/<video_name>')
def dislike_video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    video.likes -= 1
    db.session.commit()
    return redirect(url_for('video', video_name=video_name))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return redirect(url_for('channel', username=username))
        else:
            return render_template('login.html', error="Неверный логин или пароль")
    return render_template('login.html')

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
    return render_template('register.html')

@app.route('/channel/<username>')
def channel(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).all()
    return render_template('channel.html', user=user, videos=videos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)