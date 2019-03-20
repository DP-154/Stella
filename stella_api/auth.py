from flask import Blueprint, request, redirect, flash, url_for, render_template
from flask_login import current_user, login_user, logout_user
from database.models import User
from database.db_connection import session_maker
from stella_api.forms import SignInForm, SignUpForm
from werkzeug.urls import url_parse


auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('ui.prices'))
    form = SignInForm(meta={'csrf': False})
    if form.validate_on_submit():
        session = session_maker()
        user = session.query(User).filter(User.username == form.username.data).first()
        session.close()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username and/or password")
            return redirect(url_for('auth.sign_in'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('ui.prices')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('ui.prices'))
    form = SignUpForm(meta={'csrf': False})
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        session = session_maker()
        session.add(user)
        session.commit()
        session.close()
        flash("Registration successful. Please, sign in now.")
        return redirect(url_for('auth.sign_in'))
    return render_template('auth/register.html', form=form)


@auth.route('/log_out', methods=['GET', 'POST'])
def log_out():
    logout_user()
    return redirect(url_for('ui.index'))
