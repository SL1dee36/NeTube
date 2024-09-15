# routes/user_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session
from markupsafe import Markup

from models import User, db
from helpers.utils import get_current_user

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect(url_for('main_bp.index'))
        else:
            return render_template('user/login.html', error="Неверный логин или пароль")
    current_user = get_current_user()
    return render_template('user/login.html', current_user=current_user,
                           Markup=Markup)

@user_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('main_bp.index'))

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return render_template('user/register.html', error="Пользователь с таким именем уже существует")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_bp.login'))
    current_user = get_current_user()
    return render_template('user/register.html', current_user=current_user,
                           Markup=Markup, )
