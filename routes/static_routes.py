# routes/static_routes.py

from flask import Blueprint, send_from_directory, current_app as app

static_bp = Blueprint('static_bp', __name__)

@static_bp.route('/static/videos/<path:filename>')
def serve_videos(filename):
    return send_from_directory(app.config['VIDEOS_FOLDER'], filename)

@static_bp.route('/static/thumbnails/<path:filename>')
def serve_thumbnails(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@static_bp.route('/static/avatars/<path:filename>')
def serve_icons(filename):
    return send_from_directory(app.config['ICONS_FOLDER'], filename)

@static_bp.route('/static/avatars/users/<path:filename>')
def serve_avatars(filename):
    return send_from_directory(app.config['AVATARS_FOLDER'], filename)
