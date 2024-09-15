from .channel_routes import channel_bp
from .main_routes import main_bp
from .static_routes import static_bp
from .video_like_routes import video_like_bp
from .video_routes import video_bp
from .subscription_routes import subscription_bp
from .user_routes import user_bp
from .admin_routes import admin_bp

def register_routes(app):
    app.register_blueprint(video_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(channel_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(video_like_bp)

