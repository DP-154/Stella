from flask import Blueprint, render_template


ui = Blueprint('ui', __name__, url_prefix='/')


@ui.route('/prices')
def main_page():
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
    return render_template('prices/prices.html', price_list=price_list)


@ui.route('/')
def index():
    return render_template('index.html')
