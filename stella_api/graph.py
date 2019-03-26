import os
import shutil
import time
from datetime import datetime


import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot

from selenium import webdriver


from transport.data_provider import DropBoxDataProvider
from stella_api.helpers import query_to_dict


class Graph:
    def __init__(self):
        pass
        # self.query = query

    def getGraph(self):
        dbdp = DropBoxDataProvider(os.environ['DROPBOX_TOKEN'])
        py.plotly.tools.set_credentials_file(username=os.environ['Plotly_username'], api_key=os.environ['Plotly_api_key'])
        # data_from_qery = query_to_dict(self.query)

        date = ['80', '92', '95']
        price = [55.22, 66.44, 88.33]
        price2 = [44.11, 53.23, 35.14]
        price3 = [33.15, 46.31, 28.23]

        trace0 = go.Bar(
            x=date,
            y=price,
            text=price,
            textposition='auto',
            name='OKKO',
            marker=dict(
                color='rgb(49,130,189)',
                line=dict(
                    color='rgb(15,42,176)',
                    width=1.5),
            ),
            opacity=0.6
        )

        trace1 = go.Bar(
            x=date,
            y=price2,
            text=price2,
            textposition='auto',
            name='WOG',
            marker=dict(
                color='rgb(204,204,204)',
                line=dict(
                    color='rgb(33,149,10)',
                    width=1.5),
            ),
            opacity=0.6
        )

        trace2 = go.Bar(
            x=date,
            y=price3,
            text=price3,
            textposition='auto',
            name='NefTek',
            marker=dict(
                color='rgb(195,85,91)',
                line=dict(
                    color='rgb(144,8,8)',
                    width=1.5),
            ),
            opacity=0.6
        )

        data = [trace0, trace1, trace2]
        layout = go.Layout(
            xaxis=dict(tickangle=-45),
            barmode='group',
        )

        fig = go.Figure(data=data, layout=layout)

        if not os.path.exists('graph_images'):
            os.mkdir('graph_images')

        path = os.path.join(os.path.dirname(__file__), 'graph_images/')
        path_crome_driver = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

        date = datetime.today().strftime('%Y-%m-%d_%H.%M.%S')
        html_file_name = f'Fuel-price-graph-{date}.html'
        png_file_name = f'Fuel-price-graph-{date}.png'

        dbx_file_html = '/graph_html/' + html_file_name
        dbx_file_png = '/graph_png/' + png_file_name

        plot(fig, filename=f'{path}{html_file_name}', auto_open=False)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.accept_untrusted_certs = True
        chrome_options.assume_untrusted_cert_issuer = True
        chrome_options.add_argument("--no-sandbox")

        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1200x600')

        driver = webdriver.Chrome(executable_path=path_crome_driver, chrome_options=chrome_options)
        driver.get(f'{path}{html_file_name}')
        driver.save_screenshot(f'{path}{png_file_name}')
        time.sleep(1)
        driver.quit()

        dbdp.file_upload(f'{path}{png_file_name}', dbx_file_png)
        dbdp.file_upload(f'{path}{html_file_name}', dbx_file_html)

        shutil.rmtree(path)

        return
