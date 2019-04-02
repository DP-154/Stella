import json
from datetime import datetime, date

from flask import request, Blueprint, make_response
from flask_restplus import Api, Resource, reqparse

from database.db_connection import session_maker
from database.db_query_bot import (query_by_station_min_price, query_by_station_current_date, query_avg_all_stations,
                                   query_all_price_period, query_avg_price_period)
from processor.imageMetadata.coordinates_metadata import gasStationInfo
from services.service_data import upload_image_to_dbx
from stella_api import helpers

restful = Blueprint('restful', __name__, url_prefix='/restful')
api = Api(restful, doc='/docs')
session = session_maker()


def get_date_param(cur_request, name):
    date_param = cur_request.args.get(name, None)
    if date_param:
        date_param = datetime.strptime(date_param, '%d-%m-%Y').date()
    return date_param


def make_response_json(cur_dict):
    json_data = json.dumps(cur_dict, default=helpers.to_serializable, ensure_ascii=False)
    resp = make_response(json_data)
    resp.mimetype = 'application/json'
    return resp


@api.route('/min_by_fuel')
class MinPrice(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('fuel_type', type=str, required=True, default='92')
    request_arguments.add_argument('date_of_price', type=str, help="Date format: day-month-year ")

    @api.expect(request_arguments, validate=True)
    def get(self):
        """Returns the minimum price for fuel at particular date (if date is omit at max date with info)."""
        if not request.args.get("fuel_type"):
            return make_response_json({
                'status': 'fail',
                'reason': 'no fuel type provided'
            })
        try:
            get_date_param(request, 'date_of_price')
        except ValueError:
            return make_response_json({
                'status': 'fail',
                'reason': 'wrong date'
            })
        result = query_by_station_min_price(session, request.args.get("fuel_type"),
                                            get_date_param(request, 'date_of_price'))
        result_dict = helpers.query_to_dict(result)
        return make_response_json({'status': 'ok', 'data': result_dict})


@api.route('/price_by_day')
class PriceByDay(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('longitude', type=float, required=True, help="longitude of gas station")
    request_arguments.add_argument('latitude', type=float, required=True, help="latitude of gas station")
    request_arguments.add_argument('date_of_price', type=str, help="Date format: day-month-year ")

    @api.expect(request_arguments, validate=True)
    def get(self):
        """Returns all prices for gas station at particular date (if date is omit at max date with info)."""
        try:
            longitude = float(request.args.get("longitude"))
            latitude = float(request.args.get("latitude"))
        except ValueError:
            return make_response_json({
                'status': 'fail',
                'reason': 'wrong longitude or latitude'
            })
        companies = gasStationInfo(longitude, latitude)
        if len(companies) > 0:
            company_name = companies[0]['name']
            company_address = companies[0]['adress']
            try:
                get_date_param(request, 'date_of_price')
            except ValueError:
                return make_response_json({
                    'status': 'fail',
                    'reason': 'wrong date'
                })
            result = query_by_station_current_date(session, company_name, company_address,
                                                   get_date_param(request, 'date_of_price'))
            result_dict = helpers.query_to_dict(result)
        else:
            result_dict = {}
        return make_response_json({'status': 'ok', 'data': result_dict})


@api.route('/avg_price')
class AVGPrice(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('date_of_price', type=str, help="Date format: day-month-year ")

    @api.expect(request_arguments, validate=True)
    def get(self):
        """Returns average prices for all gas station at particular date (if date is omit at max date with info)."""
        try:
            get_date_param(request, 'date_of_price')
        except ValueError:
            return make_response_json({
                'status': 'fail',
                'reason': 'wrong date'
            })
        result = query_avg_all_stations(session, get_date_param(request, 'date_of_price'))
        result_dict = helpers.query_to_dict(result)
        return make_response_json({'status': 'ok', 'data': result_dict})


@api.route('/avg_price_period')
class AVGPricePeriod(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('fuel_type', type=str, required=True, default='92')
    request_arguments.add_argument('date_from', type=str, help="Date format: day-month-year ")
    request_arguments.add_argument('date_to', type=str, help="Date format: day-month-year ")

    @api.expect(request_arguments, validate=True)
    def get(self):
        """Returns average prices for fuel at period (if dates are omit for last 10 days)."""
        if not request.args.get("fuel_type"):
            return make_response_json({
                'status': 'fail',
                'reason': 'no fuel type provided'
            })
        try:
            get_date_param(request, 'date_from')
            get_date_param(request, 'date_to')
        except ValueError:
            return make_response_json({
                'status': 'fail',
                'reason': 'wrong date'
            })
        result = query_avg_price_period(session, request.args.get("fuel_type"),
                                        get_date_param(request, 'date_from'), get_date_param(request, 'date_to'))
        result_dict = helpers.query_to_dict(result)
        return make_response_json({'status': 'ok', 'data': result_dict})


@api.route('/all_price_period')
class AllPricePeriod(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('date_from', type=str, help="Date format: day-month-year ")
    request_arguments.add_argument('date_to', type=str, help="Date format: day-month-year ")

    @api.expect(request_arguments, validate=True)
    def get(self):
        """Returns all prices for period (if dates are omit for last 10 days)."""
        try:
            get_date_param(request, 'date_from')
            get_date_param(request, 'date_to')
        except ValueError:
            return make_response_json({
                'status': 'fail',
                'reason': 'wrong date'
            })
        result = query_all_price_period(session, get_date_param(request, 'date_from'),
                                        get_date_param(request, 'date_to'))
        result_dict = helpers.query_to_dict(result)
        return make_response_json({'status': 'ok', 'data': result_dict})


@api.route('/upload_image')
class UploadImage(Resource):
    request_arguments = reqparse.RequestParser()
    request_arguments.add_argument('file_link', type=str, required=True, help="file link for uploading ")
    request_arguments.add_argument('file_name', type=str, required=True)

    @api.expect(request_arguments, validate=True)
    def post(self):
        """Saves the file from link to dropbox as file_name."""
        file_path = request.args['file_link']
        dbx_path = '/telegram_files/' + request.args['file_name']
        try:
            dbx_path, dbx_link = upload_image_to_dbx(file_path, dbx_path)
        except Exception:
            return make_response_json({
                'status': 'fail',
                'reason': Exception
            })
        result_dict = {"dropbox_path": dbx_path}
        return make_response_json({'status': 'ok', 'data': result_dict})
