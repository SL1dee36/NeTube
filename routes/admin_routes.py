# routes/admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app, abort

from config import Config
from models import User, Video, db
from helpers.utils import get_current_user, allowed_file
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin_bp.administration'))

    return render_template('admin/edit_user.html', user=user, current_user=current_user)

@admin_bp.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin_bp.administration'))

    return render_template('admin/edit_video.html', video=video, current_user=current_user)

@admin_bp.route('/administration', methods=['GET', 'POST'])
def administration():
    if request.method == 'POST':
        entered_key = request.form.get('admin_key')
        if entered_key == Config.ADMIN_SECRET_KEY:
            users = User.query.all()
            videos = Video.query.all()
            return render_template('admin/administration.html', users=users, videos=videos)
        else:
            return "Неверный пароль!"
    return render_template('admin/admin_login.html')