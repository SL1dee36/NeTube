# app.py
import traceback

from flask import Flask, render_template
from markupsafe import Markup

from helpers.utils import get_current_user
from models import db
import logging
from config import Config
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Конфигурация логгера
logging.basicConfig(level=logging.DEBUG)

# Register routes
register_routes(app)


# Регистрация обработчиков ошибок
@app.errorhandler(400)
def bad_request_error(error):
    current_user = get_current_user()
    return render_template('errors/400.html',current_user=current_user, Markup=Markup), 400

@app.errorhandler(401)
def unauthorized_error(error):
    current_user = get_current_user()
    return render_template('errors/401.html',current_user=current_user, Markup=Markup), 401

@app.errorhandler(403)
def forbidden_error(error):
    current_user = get_current_user()
    return render_template('errors/403.html',current_user=current_user, Markup=Markup), 403

@app.errorhandler(404)
def not_found_error(error):
    current_user = get_current_user()
    return render_template('errors/404.html',current_user=current_user, Markup=Markup), 404


@app.errorhandler(500)
def internal_server_error(error):
    current_user = get_current_user()

    return render_template('errors/500.html', current_user=current_user, Markup=Markup, error=error), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
