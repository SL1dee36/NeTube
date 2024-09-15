# routes/main_routes.py

from flask import Blueprint, render_template, request
from markupsafe import Markup

from helpers.utils import search_videos
from models import Video
from helpers.utils import get_current_user

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    current_user = get_current_user()
    videos = Video.query.order_by(Video.likes.desc()).all()
    search_results = []
    search_query = ''
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            search_results = search_videos(search_query, videos)


    return render_template(
        'index.html',
        videos=videos,
        search_results=search_results,
        Markup=Markup,
        current_user=current_user,
        search_query=search_query
    )
