import os

from flask import Flask
from flask_api.restful import restful
from flask_api.auth import auth
from flask_api.base import base
from flask_api.prices import ui
from flask_login import LoginManager
from database import queries, models

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.register_blueprint(restful)
app.register_blueprint(auth)
app.register_blueprint(base)
app.register_blueprint(ui)

login = LoginManager(app)
login.login_view = 'sign_in'

@login.user_loader
def load_user(uid):
    with queries.session_scope() as session:
        return session.query(models.User).filter_by(id=uid).first()

if __name__ == '__main__':
    app.run(debug=True)
