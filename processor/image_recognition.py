import cv2
import numpy as np
from keras.models import load_model
from skimage import io

from os import path
path_model=path.join(path.dirname(__file__), 'my_model.h5')
model = load_model(path_model)

#model = load_model('processor/my_model.h5')
# https://github.com/keras-team/keras/issues/6462#issuecomment-319232504
model._make_predict_function()


class DigitDetection:

    def __init__(self, img_file):
        self.img_file = img_file

    def _get_digits_(self, contours, hierarchy):
        hierarchy = hierarchy[0]
        bounding_rectangles = [cv2.boundingRect(ctr) for ctr in contours]
        final_bounding_rectangles = []

        u, indices = np.unique(hierarchy[:, -1], return_inverse=True)
        most_common_heirarchy = u[np.argmax(np.bincount(indices))]

        for r, hr in zip(bounding_rectangles, hierarchy):
            x, y, w, h = r

            if ((w * h) > 250) and (10 <= w <= 200) and (10 <= h <= 200) and hr[3] == most_common_heirarchy:
                final_bounding_rectangles.append(r)

        return final_bounding_rectangles


    def detection_roi_user_img(self):

        im = io.imread(self.img_file)
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((5, 5), np.uint8)

        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        thresh = cv2.erode(thresh, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        digits_rectangles = self._get_digits_(contours, hierarchy)

        return digits_rectangles

    @staticmethod
    def crop_images(image,  roi):

        img = io.imread(image)
        y = roi[1]
        x = roi[0]
        h = roi[1] + roi[3]
        w = roi[0] + roi[2]
        crop_img = img[y:h, x:w]
        return crop_img


def digit_recognition(TEST_USER_IMG, roi):
    crop_image1 = DigitDetection.crop_images(TEST_USER_IMG, roi)
    img = cv2.cvtColor(crop_image1, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (28, 28))
    img = img[np.newaxis]
    img = img.reshape(img.shape[0], 28, 28, 1)
    return(np.argmax(model.predict(img)))


def digit_to_price(img_path):

    image1 = DigitDetection(img_path)
    roi = image1.detection_roi_user_img()
    roi = sorted(roi, key=lambda x: int(x[0]))
    if len(roi) == 6:
        digit = []
        for i in range(len(roi)):
            digit.append(digit_recognition(img_path, roi[i]))

        brend = ''.join(map(str, digit[0:2]))
        grn = ''.join(map(str, digit[2:4]))
        coop = ''.join(map(str, digit[4:6]))
        return ((True, brend, grn + '.' + coop))
    else:
        return ((False, None, None))
