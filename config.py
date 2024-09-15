import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///netube.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/videos')
    THUMBNAIL_FOLDER = os.path.join(os.getcwd(), 'static/thumbnails')
    ICONS_FOLDER = os.path.join(os.getcwd(), 'static/avatars')
    AVATARS_FOLDER = os.path.join(os.getcwd(), 'static/avatars/users')
    VIDEOS_FOLDER = os.path.join(os.getcwd(), 'static/videos')
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024 * 1024  # 8GB
    SECRET_KEY = 'your_secret_key'  # Change to a secure key
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}
    ADMIN_SECRET_KEY = "123"  # Change this in production

