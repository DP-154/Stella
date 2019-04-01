from os import path

import cv2
import numpy as np
from keras.models import load_model
from skimage import io


model = load_model(path.join(path.dirname(__file__), 'my_model.h5'))
model._make_predict_function()  # https://github.com/keras-team/keras/issues/6462#issuecomment-319232504


def get_digits(contours, hierarchy):
    hierarchy = hierarchy[0]
    bounding_rectangles = [cv2.boundingRect(ctr) for ctr in contours]
    final_bounding_rectangles = []

    u, indices = np.unique(hierarchy[:, -1], return_inverse=True)
    most_common_hierarchy = u[np.argmax(np.bincount(indices))]

    for r, hr in zip(bounding_rectangles, hierarchy):
        x, y, w, h = r

        if ((w * h) > 1400) and (10 <= w <= 330) and (60 <= h <= 280) and hr[3] == most_common_hierarchy:
            final_bounding_rectangles.append(r)

    return final_bounding_rectangles


def get_roi(result):
    kernel = np.ones((3, 3), np.uint8)
    ret, thresh = cv2.threshold(result, 127, 255, 0)
    thresh = cv2.erode(thresh, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    digits_rectangles = get_digits(contours, hierarchy)
    return digits_rectangles


def crop_images(img, roi):
    y = roi[1]
    x = roi[0]
    h = roi[1] + roi[3]
    w = roi[0] + roi[2]
    crop_img = img[y:h, x:w]
    return crop_img


def digit_recognition(crop_image, roi):
    img = cv2.resize(crop_image, (28, 28))
    img = img[np.newaxis]
    img = img.reshape(img.shape[0], 28, 28, 1)
    return np.argmax(model.predict(img))


class BrsmDetect:

    def __init__(self, img_path):
        self.img_path = img_path

    def preprocess_image(self):
        image = io.imread(self.img_path)
        image = cv2.resize(image, (1000, 1000))
        y = 0
        h = image.shape[0]
        w = image.shape[1]
        x = int(w * 0.35)
        crop = image[y:y + h, x:x + w]
        img_grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        (thresh, im_bw) = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        thresh = 127
        ret, cropped_threshold = cv2.threshold(im_bw, 10, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((2, 2), np.uint8)
        erosion = cv2.erode(cropped_threshold, kernel, iterations=1)
        closing = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernel)
        return closing

    def digit_to_price(self):
        result = BrsmDetect.preprocess_image(self)
        roi = get_roi(result)
        roi2 = sorted(roi, key=lambda x: int(x[1]))
        roi_sort = [roi2[i:i + 4] for i in range(0, len(roi2), 4)]
        for i in range(len(roi_sort)):
            roi_sort[i] = sorted(roi_sort[i], key=lambda x: int(x[0]))

        if len(roi) == 28:
            digit = []
            for list in roi_sort:
                for number in list:
                    img = BrsmDetect.preprocess_image(self)
                    crop_image1 = crop_images(img, number)
                    digit.append(digit_recognition(crop_image1, number))

                price = [str(digit[i]) + str(digit[i + 1]) for i in range(0, len(digit), 2)]

            return ((True, '95E+', price[0] + '.' + price[1]), (True, '95E', price[2] + '.' + price[3]),
                    (True, '95E Premium', price[4] + '.' + price[5]), (True, '92', price[6] + '.' + price[7]),
                    (True, 'ДП Euro', price[8] + '.' + price[9]), (True, 'ДП', price[10] + '.' + price[11]),
                    (True, 'ГАЗ', price[12] + '.' + price[13]))

        else:
            return (False, None, None)


class YukonDetect:

    def __init__(self, img_path):
        self.img_path = img_path

    def preproces_image(self):
        image = io.imread(self.img_path)
        image = cv2.resize(image, (1000, 1000))
        y = 0
        h = image.shape[0]
        w = image.shape[1]
        x = int(w * 0.286)
        blur = 3
        crop = image[y:y + h, x:x + w]
        img_grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        (thresh, im_bw) = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        thresh = 127
        im_bw = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)[1]
        img_blurred = cv2.GaussianBlur(im_bw, (blur, blur), 0)
        ret, cropped_threshold = cv2.threshold(img_blurred, 10, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((5, 5), np.uint8)
        erosion = cv2.erode(cropped_threshold, kernel, iterations=1)

        closing = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernel)
        opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
        result = cv2.erode(opening, kernel, iterations=1)
        return result

    def digit_to_price(self):

        result = YukonDetect.preproces_image(self)
        roi = get_roi(result)
        roi = sorted(roi, key=lambda x: int(x[1]))
        roi_sort = [roi[i:i + 4] for i in range(0, len(roi), 4)]
        for i in range(len(roi_sort)):
            roi_sort[i] = sorted(roi_sort[i], key=lambda x: int(x[0]))

        if len(roi) == 16:
            digit = []

            for list in roi_sort:
                for number in list:
                    img = YukonDetect.preproces_image(self)
                    crop_image1 = crop_images(img, number)
                    digit.append(digit_recognition(crop_image1, number))

            price = [str(digit[i]) + str(digit[i + 1]) for i in range(0, len(digit), 2)]

            return ((True, '95+', price[0] + '.' + price[1]), (True, '95', price[2] + '.' + price[3]),
                    (True, '92', price[4] + '.' + price[5]), (True, 'ДТ', price[6] + '.' + price[7]))

        else:
            return (False, None, None)
