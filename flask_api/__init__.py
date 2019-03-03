from flask import Blueprint

bp = Blueprint('api', __name__)

from flask_api import routes, auth