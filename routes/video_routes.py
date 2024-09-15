# routes/video_routes.py

from flask import Blueprint, request, render_template, redirect, url_for, jsonify, session
from markupsafe import Markup
from models import Video
from helpers.utils import get_current_user, allowed_file
from services.video_service import save_video, increment_video_views, add_comment_to_video
video_bp = Blueprint('video_bp', __name__)

@video_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    current_user = get_current_user()
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description'][:500]
            file = request.files['file']
            if file and allowed_file(file.filename):
                video = save_video(file, title, description, session['user_id'])
                return redirect(url_for('video_bp.video', video_name=video))
        return render_template('video/upload.html', current_user=current_user, Markup=Markup, )
    else:
        return redirect(url_for('user_bp.login'))


@video_bp.route('/video/<video_name>')
def video(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    current_user = get_current_user()
    increment_video_views(video)

    related_videos = Video.query.filter(Video.id != video.id).limit(9).all()
    return render_template('video/video.html', video=video, Markup=Markup, current_user=current_user, related_videos=related_videos)

@video_bp.route('/api/video/<video_name>/comment', methods=['POST'])
def add_comment(video_name):
    video = Video.query.filter_by(url=video_name).first_or_404()
    current_user = get_current_user()

    if current_user:
        content = request.json.get('content')  # Изменено для работы с JSON
        if content:
            new_comment = add_comment_to_video(video, current_user, content)
            return jsonify({
                "message": "Comment added successfully.",
                "comment": new_comment
            }), 200
        else:
            return jsonify({"message": "Content is required."}), 400
    return jsonify({"message": "Unauthorized access."}), 401
