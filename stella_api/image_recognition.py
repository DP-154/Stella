import numpy as np
from scipy.misc.pilutil import imresize
import cv2
from matplotlib import pyplot as plt

DIGIT_WIDTH = 10
DIGIT_HEIGHT = 20
IMG_HEIGHT = 28
IMG_WIDTH = 28
CLASS_N = 10  # 0-9

DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 1, 0): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 0, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9
}


class Digit_detection:

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

        im = cv2.imread(self.img_file)
        blank_image = np.zeros((im.shape[0], im.shape[1], 3), np.uint8)
        blank_image.fill(255)
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        plt.imshow(imgray)
        kernel = np.ones((5, 5), np.uint8)

        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        thresh = cv2.erode(thresh, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        digits_rectangles = self._get_digits_(contours, hierarchy)

        for rect in digits_rectangles:
            x, y, w, h = rect
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            im_digit = imgray[y:y + h, x:x + w]
            im_digit = (255 - im_digit)
            im_digit = imresize(im_digit, (IMG_WIDTH, IMG_HEIGHT))
        return digits_rectangles


def crop_images(img_file, roi):
    img = cv2.imread(img_file)
    y = roi[1]
    x = roi[0]
    h = roi[1] + roi[3]
    w = roi[0] + roi[2]
    crop_img = img[y:h, x:w]
    return crop_img


def segments_detection(img_file, roi):
    (x, y, w, h) = roi
    (roiH, roiW, z) = img_file.shape
    (dW, dH) = (int(roiW * 0.4), int(roiH * 0.4))
    dHC = int(roiH * 0.05)

    segments = [
        ((0, 0), (w, dH)),  # top
        ((0, 0), (dW, h // 2)),  # top-left
        ((w - dW, 0), (w, h // 2)),  # top-right
        ((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # center
        ((0, h // 2), (dW, h)),  # bottom-left
        ((w - dW, h // 2), (w, h)),  # bottom-right
        ((0, h - dH), (w, h))  # bottom
    ]
    on = [0] * len(segments)
    return (segments)


def recognize_digit(img_file, roi):
    on = [0] * 7
    segments = segments_detection(img_file, roi)
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        segROI = img_file[yA:yB, xA:xB]
        segROI = cv2.cvtColor(segROI, cv2.COLOR_BGR2GRAY)
        total = cv2.countNonZero(segROI)
        area = (xB - xA) * (yB - yA)

        if total / float(area) > 0.5:
            on[i] = 1
    digit = DIGITS_LOOKUP[tuple(on)]
    return digit, on, segments


if __name__ == '__main__':
    TEST_USER_IMG = '/home/kerch007/Stella/stella_api/test_image.png'
    image1 = Digit_detection(TEST_USER_IMG)
    roi = image1.detection_roi_user_img()
    print(roi[2])

    crop_image1 = crop_images(TEST_USER_IMG, roi[12])
    import pytesseract

    plt.imshow(crop_image1)
    plt.show()

    data = pytesseract.image_to_string(crop_image1, config='--psm 8 --oem 3 tessedit_char_whitelist=0123456789 ')
    print(data)
