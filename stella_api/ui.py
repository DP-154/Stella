import os
from pprint import pprint

from flask import Blueprint, render_template, redirect, url_for, flash
from stella_api.forms import SendPhotoForm
from transport.data_provider import DropBoxDataProvider
from werkzeug.utils import secure_filename
from flask_login import login_required

from database.queries import session_scope
from database.db_connection import engine, session_maker
from database.db_query_bot import query_all_price_period

from stella_api.helpers import query_to_dict
from services.service_data import upload_image_to_dbx


ui = Blueprint('ui', __name__, url_prefix='/')


@ui.route('/prices', methods=['POST', 'GET'])
@login_required
def prices():
    price_list = [
        {
            'name': 'Okko',
            'fuel': [('A-92 ', 27.00), ('A-95 ', 28.00), ('A-95+', 30.00), ('propane', 12.00)],
            'datetime': '03.03.19 12:45',
        },
        {
            'name': 'WOG',
            'fuel': [('A-92 ', 25.00), ('A-95 ', 26.00), ('A-95+', 28.00), ('propane', 10.00)],
            'datetime': '02.03.19 13:18',
        },
        {
            'name': 'Okko',
            'fuel': [('A-92 ', 27.00), ('A-95 ', 28.00), ('A-95+', 30.00), ('propane', 12.00)],
            'datetime': '03.03.19 12:45',
        },
        {
            'name': 'WOG',
            'fuel': [('A-92 ', 25.00), ('A-95 ', 26.00), ('A-95+', 28.00), ('propane', 10.00)],
            'datetime': '02.03.19 13:18',
        },
        {
            'name': 'Okko',
            'fuel': [('A-92 ', 27.00), ('A-95 ', 28.00), ('A-95+', 30.00), ('propane', 12.00)],
            'datetime': '03.03.19 12:45',
        },
        {
            'name': 'WOG',
            'fuel': [('A-92 ', 25.00), ('A-95 ', 26.00), ('A-95+', 28.00), ('propane', 10.00)],
            'datetime': '02.03.19 13:18',
        },
        {
            'name': 'Okko',
            'fuel': [('A-92 ', 27.00), ('A-95 ', 28.00), ('A-95+', 30.00), ('propane', 12.00)],
            'datetime': '03.03.19 12:45',
        },
        {
            'name': 'WOG',
            'fuel': [('A-92 ', 25.00), ('A-95 ', 26.00), ('A-95+', 28.00), ('propane', 10.00)],
            'datetime': '02.03.19 13:18',
        },
        {
            'name': 'Okko',
            'fuel': [('A-92 ', 27.00), ('A-95 ', 28.00), ('A-95+', 30.00), ('propane', 12.00)],
            'datetime': '03.03.19 12:45',
        },
        {
            'name': 'WOG',
            'fuel': [('A-92 ', 25.00), ('A-95 ', 26.00), ('A-95+', 28.00), ('propane', 10.00)],
            'datetime': '02.03.19 13:18',
        },

    ]
    
    with session_scope() as session:
        price_list = query_to_dict(query_all_price_period(session))
    
    form = SendPhotoForm(meta={'csrf': False})
    if form.validate_on_submit():
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        upload_image_to_dbx(photo, ('/telegram_files/' + filename))
        flash('Thanks for uploading photo')

        return redirect(url_for('ui.prices'))

    return render_template('main/main.html', price_list=price_list, form=form)


@ui.route('/')
def index():
    return render_template('index.html')


