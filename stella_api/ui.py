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
        price_list = list(dict(price_list).values())
        date_to_str = lambda d: f'{d.month}/{d.day}/{d.year}'
        attr_getter = lambda x: (x['fuel_company_name'], date_to_str(x['date_of_price']))
        companies_and_dates = map(attr_getter, price_list)
        d = {k: [] for k in dict.fromkeys(companies_and_dates)}
        fields = ['date_of_price', 'fuel_company_name', 'fuel_type', 'price']
        for record in price_list:
            date, company, fuel_type, price = [record[f] for f in fields]
            date = date_to_str(date)
            d[(company, date)].append((fuel_type, price))
        price_list = [{'fuel_company_name': company,
                       'fuel': [{'date': d, 'price': p} for d, p in fuels],
                       'date_of_price': date}
                      for (company, date), fuels in d.items()]
    
    form = SendPhotoForm(meta={'csrf': False})
    if form.validate_on_submit():
        photo = form.photo.data
        transport = DropBoxDataProvider(os.environ['DROPBOX_TOKEN'])
        filename = secure_filename(photo.filename)
        transport.file_upload(photo, ('/telegram_files/' + filename))
        flash('Thanks for uploading photo')

        return redirect(url_for('ui.prices'))

    return render_template('main/main.html', price_list=price_list, form=form)


@ui.route('/')
def index():
    return render_template('index.html')
