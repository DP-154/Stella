from flask_api import bp


@bp.route('/price_by_day', methods='GET')
def price_by_day():
    pass

@bp.route('/avg_price', methods='GET')
def avg_price():
    pass

@bp.route('/min_by_fuel', methods='GET')
def min_by_fuel():
    pass

@bp.route('/upload_image', methods='GET')
def upload_image(token, longitude, latitude):
    pass