# routes/subscription_routes.py

from flask import Blueprint, request, jsonify, session
from models import User
from helpers.utils import get_current_user
from services.video_service import update_subscription

subscription_bp = Blueprint('subscription_bp', __name__)

@subscription_bp.route('/api/subscribe/<int:user_id>', methods=['POST'])
def subscribe(user_id):
    current_user = get_current_user()
    if current_user:
        user_to_subscribe = User.query.get(user_id)
        response = update_subscription(current_user, user_to_subscribe, subscribe=True)
        return jsonify(response)
    return jsonify({'status': 'error', 'message': 'User not logged in'}), 401


@subscription_bp.route('/api/unsubscribe/<int:user_id>', methods=['POST'])
def unsubscribe(user_id):
    current_user = get_current_user()
    if current_user:
        user_to_unsubscribe = User.query.get(user_id)
        response = update_subscription(current_user, user_to_unsubscribe, subscribe=False)
        return jsonify(response)
    return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
