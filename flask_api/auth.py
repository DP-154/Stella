from flask import Blueprint, request, redirect, flash, url_for, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash
from database.models import User
from database.db_connection import session_maker
from database.queries import get_or_none


auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_session = session_maker()
        error = None
        user = new_session.query(User.username, User.password_hash).filter(User.username == username).first()

        if user is None:
            error = "User doesn't exist."
        elif not(check_password_hash(user['password_hash'], password)):
            error = "Incorrect password."
        else:
            return redirect(url_for('prices'))

        flash(error)
    return render_template('auth/login.html')


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_session = session_maker()
        error = None

        if not (username or password):
            error = "You need to fill all of required fields."
        if get_or_none(new_session, User, username=username) is not None:
            error = f"User with a name '{username}' already exists."
        else:
            new_user = User(username=username, password_hash=generate_password_hash(password))
            try:
                new_session.add(new_user)
                new_session.commit()
            except:
                new_session.rollback()
                error = "Sorry, an error occurred during the transaction of user's information to the database. " \
                        "Please, try again."
            finally:
                new_session.close()
            return redirect(url_for('api.sign_in'))

        flash(error)
    return render_template('auth/register.html')


@auth.route('/logout', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('homepage'))
