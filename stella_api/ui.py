import os

from flask import Blueprint, render_template, redirect, url_for, flash
from stella_api.forms import SendPhotoForm
from transport.data_provider import DropBoxDataProvider
from werkzeug.utils import secure_filename
from flask_login import login_required

from database.queries import session_scope
from database.db_query_bot import query_all_price_period
from database.queries import list_fuel_company_names


from stella_api.helpers import query_to_dict


ui = Blueprint('ui', __name__, url_prefix='/')


@ui.route('/prices', methods=['POST', 'GET'])
# @login_required
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
        query = query_all_price_period(session)
        price_list = query_to_dict(query)
        companies_list = list_fuel_company_names(session)

    form = SendPhotoForm(meta={'csrf': False})

    form.company.choices = [(item, item) for item in companies_list]

    if form.validate_on_submit():
        photo = form.photo.data
        transport = DropBoxDataProvider(os.environ['DROPBOX_TOKEN'])
        filename = secure_filename(photo.filename)
        transport.file_upload(photo, ('/telegram_files/' + filename))

        flash('Thanks for uploading photo')

        return redirect(url_for('ui.prices'))

    return render_template('main/main.html', price_list=price_list.values(), form=form)


@ui.route('/')
def index():
    return render_template('index.html')
