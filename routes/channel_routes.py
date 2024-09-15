# routes/channel_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app as app
from markupsafe import Markup

from models import User, Video, db
from helpers.utils import get_current_user, allowed_file
import os

channel_bp = Blueprint('channel_bp', __name__)

@channel_bp.route('/channel/<username>')
def channel(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).all()
    current_user = get_current_user()
    avatar = current_user.avatar if current_user else None
    return render_template('channel/channel.html', user=user, videos=videos, avatar=avatar, current_user=current_user,
                           Markup=Markup)

@channel_bp.route('/channel/<username>/avatar', methods=['GET', 'POST'])
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
    return redirect(url_for('channel_bp.channel', username=username, user=user, current_user=current_user))
