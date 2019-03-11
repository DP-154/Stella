from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import prices, auth, api
    app.register_blueprint(prices.ui)
    app.register_blueprint(auth.auth)
    app.register_blueprint(api.bp)

    return app
