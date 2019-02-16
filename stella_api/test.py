import cv2
from matplotlib import pyplot as plt

TEST_USER_IMG = '/home/kerch007/Stella/stella_api/test_image.png'
digits_rectangles = [(208, 245, 36, 56), (153, 245, 36, 56), (94, 244, 36, 55), (56, 242, 21, 56), (97, 179, 35, 54), (206, 178, 33, 55), (149, 178, 36, 55), (52, 175, 36, 56), (197, 106, 36, 55), (150, 105, 36, 56), (99, 105, 36, 55), (54, 104, 37, 56), (99, 32, 36, 55), (200, 31, 35, 55), (149, 31, 31, 56), (59, 30, 36, 56)]

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
    (roiH, roiW,z) = img_file.shape
    (dW, dH) = (int(roiW * 0.4), int(roiH * 0.4))
    dHC = int(roiH * 0.05)

    # define the set of 7 segments
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


def recognize_digit(crop_img, roi):
    #img_g = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    on = [0] * 7
    segments = segments_detection(crop_img, roi)
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        segROI = crop_img[yA:yB, xA:xB]
        segROI = cv2.cvtColor(segROI,cv2.COLOR_BGR2GRAY)
        total = cv2.countNonZero(segROI)
        area = (xB - xA) * (yB - yA)

        if total / float(area) > 0.5:
            on[i] = 1
    digit = DIGITS_LOOKUP[tuple(on)]
    return digit, on, segments


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

if __name__ == '__main__':

    area = digits_rectangles[4]
    crop_img = crop_images(TEST_USER_IMG, area)

    plt.imshow(crop_img)
    plt.show()

    segments = segments_detection(crop_img, area)
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        plt.imshow(crop_img[yA:yB,xA:xB])
        plt.show()

    print(recognize_digit(crop_img, area))

