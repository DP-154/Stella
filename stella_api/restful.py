import json
from flask import request, Blueprint, make_response
from database.db_query_bot import (query_by_station_min_price, query_by_station_current_date, query_avg_all_stations)
from stella_api import helpers
from processor.imageMetadata.coordinates_metadata import gasStationInfo
from transport.data_provider import DropBoxDataProvider
from services.service_data import upload_image_to_dbx
from flask_login import login_required
from database.queries import session_scope


restful = Blueprint('restful', __name__, url_prefix='/restful')


@restful.route('/min_by_fuel', methods=['GET'])
@login_required
def min_price():
    request_data = request.args
    fuel_type = request_data.get("fuel_type")
    if not fuel_type:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no fuel type provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    date_of_price = request_data.get("date_of_price")
    if not date_of_price:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no date provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    with session_scope() as session:
        result = query_by_station_min_price(session, fuel_type, date_of_price)
    result_dict = helpers.query_to_dict(result)
    json_data = json.dumps({'status': 'ok', 'data': result_dict},
                           default=helpers.to_serializable,
                           ensure_ascii=False)
    resp = make_response(json_data)
    resp.mimetype = 'application/json'
    return resp


@restful.route('/price_by_day', methods=['GET'])
@login_required
def price_by_day():
    request_data = request.args
    long = request_data.get("longitude")
    if not long:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no longitude provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    lat = request_data.get("latitude")
    if not lat:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no latitude provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    date_of_price = request_data.get("date_of_price")
    if not date_of_price:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no date of price  provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    info = gasStationInfo(lat, long)
    company_name = info['name']
    company_address = info['adress']
    with session_scope() as session:
        result = query_by_station_current_date(session,
                                               company_name,
                                               company_address,
                                               date_of_price)
    result_dict = helpers.query_to_dict(result)
    json_data = json.dumps({'status': 'ok', 'data': result_dict},
                           default=helpers.to_serializable,
                           ensure_ascii=False)
    resp = make_response(json_data)
    resp.mimetype = 'application/json'
    return resp


@restful.route('/avg_price', methods=['GET'])
@login_required
def avg_price():
    request_data = request.args
    date_of_price = request_data.get("date_of_price")
    if not date_of_price:
        resp = make_response(json.dumps({
            'status': 'fail',
            'reason': 'no date of price  provided'
        }))
        resp.mimetype = 'application/json'
        return resp
    with session_scope() as session:
        result = query_avg_all_stations(session, date_of_price)
    result_dict = helpers.query_to_dict(result)
    json_data = json.dumps({'status': 'ok', 'data': result_dict},
                           default=helpers.to_serializable,
                           ensure_ascii=False)
    resp = make_response(json_data)
    resp.mimetype = 'application/json'
    return resp


@restful.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if request.headers['Content-Type'] in ['image/jpeg', 'image/png', 'image/tiff']:
        dbx_path = ''
        DropBoxDataProvider.file_upload(request.files, dbx_path)
    elif request.headers['Content-Type'] == 'application/json':
        request_data = request.get_json()
        file_id = request_data["file_id"]
        dbx_path = upload_image_to_dbx(file_id)
        return json.dumps({"dropbox_path": dbx_path})
