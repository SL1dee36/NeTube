from flask import Blueprint, jsonify, request
from models import Video, Like, DisLike, db
from helpers.utils import get_current_user

video_like_bp = Blueprint('video_like_bp', __name__)


@video_like_bp.route('/api/like/<video_name>', methods=['POST'])
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
            liked = False
        else:
            # Ставим лайк
            if existing_dislike:
                # Убираем дизлайк
                db.session.delete(existing_dislike)
                video.dislikes -= 1
            new_like = Like(user_id=user.id, video_id=video.id)
            db.session.add(new_like)
            video.likes += 1
            liked = True

        db.session.commit()

        return jsonify({'status': 'success', 'liked': liked, 'likes': video.likes, 'dislikes': video.dislikes})
    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401


@video_like_bp.route('/api/dislike/<video_name>', methods=['POST'])
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
            disliked = False
        else:
            # Ставим дизлайк
            if existing_like:
                # Убираем лайк
                db.session.delete(existing_like)
                video.likes -= 1
            new_dislike = DisLike(user_id=user.id, video_id=video.id)
            db.session.add(new_dislike)
            video.dislikes += 1
            disliked = True

        db.session.commit()

        return jsonify({'status': 'success', 'disliked': disliked, 'likes': video.likes, 'dislikes': video.dislikes})
    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
