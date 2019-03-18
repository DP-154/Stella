import os

from flask import Flask
from flask_api.restful import restful
from flask_api.auth import auth
from flask_api.prices import ui
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.register_blueprint(restful)
app.register_blueprint(auth)
app.register_blueprint(ui)

login = LoginManager(app)
login.login_view = 'login'

if __name__ == '__main__':
    app.run(debug=True)
