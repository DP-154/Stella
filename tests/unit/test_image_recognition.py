from os import path
from operator import itemgetter

import pytest

from processor.gas_price_detection import BrsmDetect, YukonDetect

wrong_image = 'file_0.jpg'

seq = {
    'brsm': ['95E+', '95E', '95E Premium', '92', 'ДП Euro', 'ДП', 'ГАЗ'],
    'yukon': ['95+', '95', '92', 'ДТ']
}

matrix = {
    'brsm': {
        'brsm1.png': [
            '27.79', '26.19', '20.39', '25.19', '26.79', '25.89', '10.99'
        ],
        'brsm2.png': [
            '27.79', '26.19', '20.39', '25.19', '26.79', '25.89', '10.99'
        ],
        'brsm3.png': [
            '27.79', '26.19', '20.49', '25.19', '26.79', '25.79', '11.09'
        ],
        'brsm4.png': [
            '27.79', '26.19', '20.49', '25.19', '26.79', '25.79', '11.09'
        ]
    },
    'yukon': {
        'yuk1.png': [
            '28.50', '28.00', '27.00', '28.00'
        ],
        'yuk2.png': [
            '28.50', '28.00', '27.00', '28.00'
        ],
        'yuk3.png': [
            '28.50', '28.00', '27.00', '28.00'
        ],
        'yuk4.png': [
            '28.50', '28.00', '27.00', '28.00'
        ],
        'yuk5.png': [
            '28.50', '28.00', '27.00', '28.00'
        ]
    }
}


def get_full_path(img_name):
    return path.join(path.dirname(__file__), img_name)

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_brms_recognition():
    for k, v in matrix['brsm'].items():
        result = (BrsmDetect(get_full_path(path.join('images', k)))
                  .digit_to_price())

        assert result is not False,\
            f'recognition failed completely for file {k}'
        
        flags = list(map(itemgetter(0), result))
        assert all(flags), f'not all prices recognized for file {k}'
        
        labels = list(map(itemgetter(1), result))
        assert labels == seq['brsm'], f'incorrect labels for file {k}'

        prices = list(map(itemgetter(2), result))
        assert prices == matrix['brsm'][k], \
            f'price recognized incorrectly in file {k}'

@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_yukon_recognition():
    for k, v in matrix['yukon'].items():
        result = (YukonDetect(get_full_path(path.join('images', k)))
                  .digit_to_price())

        assert result is not False,\
            f'recognition failed completely for file {k}'
        
        flags = list(map(itemgetter(0), result))
        assert all(flags), f'not all prices recognized for file {k}'
        
        labels = list(map(itemgetter(1), result))
        assert labels == seq['yukon'], f'incorrect labels for file {k}'

        prices = list(map(itemgetter(2), result))
        assert prices == matrix['yukon'][k], \
            f'price recognized incorrectly in file {k}'


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_digit_to_price_negative():
    result = (YukonDetect(get_full_path(path.join('images', wrong_image)))
              .digit_to_price())
    assert result[0] is False, 'recognized price on wrong image'

    result = (BrsmDetect(get_full_path(path.join('images', wrong_image)))
              .digit_to_price())
    assert result[0] is False, 'recognized price on wrong image'
