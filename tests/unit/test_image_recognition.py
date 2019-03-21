from os import path

import pytest

from processor.image_recognition import digit_to_price, DigitDetection, digit_recognition

SAMPLE_IMG = 'images/file_69.png'
IMG_NEG = 'images/file_0.jpg'

SAMPLE_FUEL = '92'
SAMPLE_PRICE = '27.08'
SAMPLE_RECTANGLE = (78, 13, 44, 81)
SAMPLE_LEN = 6
SAMPLE_FIRST_DIGIT = 9


def get_full_path(img_name):
    return path.join(path.dirname(__file__), img_name)

@pytest.mark.skip(reason="not working")
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_digit_to_price_positive():
    assert digit_to_price(get_full_path(SAMPLE_IMG)) == (True, SAMPLE_FUEL, SAMPLE_PRICE)


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_digit_to_price_negative():
    assert digit_to_price(get_full_path(IMG_NEG)) == (False, None, None)


@pytest.mark.skip(reason="not working")
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@pytest.mark.xfail(raises=FileNotFoundError)
def test_digit_to_price_not_found():
    digit_to_price(get_full_path(''))


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_detection_roi_user_img():
    dd = DigitDetection(get_full_path(SAMPLE_IMG))
    rectangles = dd.detection_roi_user_img()
    assert rectangles[0] == SAMPLE_RECTANGLE
    assert len(rectangles) == SAMPLE_LEN


@pytest.mark.filterwarnings('ignore::DeprecationWarning')
def test_digit_recognition_positive():
    dd = DigitDetection(get_full_path(SAMPLE_IMG))
    rectangles = dd.detection_roi_user_img()
    rectangles = sorted(rectangles, key=lambda x: int(x[0]))
    assert digit_recognition(get_full_path(SAMPLE_IMG), rectangles[0]) == SAMPLE_FIRST_DIGIT
