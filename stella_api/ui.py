from flask import Blueprint, render_template, redirect, url_for, flash
from stella_api.forms import SendPhotoForm
from werkzeug.utils import secure_filename
from flask_login import login_required

from database.queries import session_scope, list_fuel_company_names
from database.db_query_bot import query_all_price_period

from stella_api.helpers import query_to_dict
from services.service_data import upload_image_to_dbx


ui = Blueprint('ui', __name__, url_prefix='/')


@ui.route('/prices', methods=['POST', 'GET'])
@login_required
def prices():
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

        companies_list = list_fuel_company_names(session)

    form = SendPhotoForm(meta={'csrf': False})
    form.company.choices = [(item, item) for item in companies_list]

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
