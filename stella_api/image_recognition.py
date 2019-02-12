import os

import cv2
import pytesseract
from PIL import Image, ImageDraw


def make_gray(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            S = (a + b + c) // 3
            draw.point((i, j), (S, S, S))
    image.save('gray.jpg','JPEG')

def make_negative(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            draw.point((i, j), (255 - a, 255 - b, 255 - c))
    image.save('negative.jpg','JPEG')
    return image

def make_black_white(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()
    factor = 100
    for i in range(width):
        for j in range(height):
            a = pix[i, j][0]
            b = pix[i, j][1]
            c = pix[i, j][2]
            S = a + b + c
            if (S > (((255 + factor) // 2) * 3)):
                a, b, c = 255, 255, 255
            else:
                a, b, c = 0, 0, 0
            draw.point((i, j), (a, b, c))
    image.save('bw.png')


def img_recognition(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    data = pytesseract.image_to_string(img, config='--psm 6 --oem 3 ')
    return data





if __name__ == '__main__':

    print(os.listdir('/home/kerch007/PycharmProjects/Stella/stella_api/img/'))

    path = '/home/kerch007/PycharmProjects/Stella/stella_api/img/22.jpg'

    make_negative(path)

    path2 = '/home/kerch007/PycharmProjects/Stella/stella_api/negative.jpg'

    print(img_recognition(path2))









