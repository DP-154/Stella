import os

from flask import Flask
from stella_api.restful import restful
from stella_api.auth import auth
from stella_api.ui import ui
from flask_login import LoginManager
from database.queries import session_scope
from database.models import User

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.register_blueprint(restful)
app.register_blueprint(auth)
app.register_blueprint(ui)

login = LoginManager(app)
login.login_view = 'auth.sign_in'


@login.user_loader
def load_user(uid):
    with session_scope() as session:
        return session.query(User).filter(User.id == uid).first()


if __name__ == '__main__':
    app.run(debug=True)
