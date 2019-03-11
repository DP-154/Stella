from flask import Flask
from flask_api.restful import restful
from flask_api.auth import auth
from flask_login import LoginManager

app = Flask(__name__)
app.register_blueprint(restful)
app.register_blueprint(auth)

login = LoginManager(app)
login.login_view = 'sign_in'

if __name__ == '__main__':
    app.run(debug=True)
