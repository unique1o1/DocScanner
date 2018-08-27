from subprocess import Popen, PIPE

import numpy as np
import cv2
from module.transform import transform
import pytesseract
from PIL import Image
import re


def threshold_local(image, block_size, offset):
    sigma = (block_size - 1) / 6.0
    thresh_image = cv2.GaussianBlur(image, (0, 0), sigma)
    return thresh_image - offset


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        # calculate the ratio of the height and construct the dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)

    return resized


def is_cv2():

    return cv2.__version__.startswith('2.')


def ocr(img, ocr):
    if(ocr):
        print("OCR...")
        a = Image.fromarray(img)
        text = pytesseract.image_to_string(a)
        with open('text.txt', "w") as f:
            f.write(text)


def process(image, ocr_bool):

    orig = image.copy()
    ratio = image.shape[0] / 500
    image = resize(image, height=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)
    print("STEP 1: Edge Detection")
    # cv2.imshow("Image", gray)
    # cv2.imshow("Edged", edged)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if is_cv2() else cnts[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[0:1]

    # loop over the contours
    screenCnt = None
    for c in cnts:
        # approximate the contour

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        cv2.drawContours(image, [approx], -1, (0, 255, 0), 1)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            percent = h / image.shape[0] * 100
            if percent > 50:
                print("STEP 2: Found contours of paper")
                screenCnt = approx
    if screenCnt is None:
        print("STEP 2: Found contours of paper")

        screenCnt = np.array([[[0, 0]],

                              [[image.shape[1], 0]],

                              [[image.shape[1], image.shape[0]]],

                              [[0, image.shape[0]]]])

    # cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
    # cv2.imshow("Outline", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    print("STEP 3: Apply perspective transform")

    warped = transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    warped = (warped > threshold_local(
        warped, 11, offset=10)).astype("uint8") * 255
    if warped.shape[0] < warped.shape[1]:
        warped = cv2.rotate(warped, rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)

    # show the original and scanned images

    ocr(warped, ocr_bool)
    return warped

    # cv2.imshow("Original", resize(orig, height=650))
    # cv2.imshow("Scanned", resize(warped, height=650))
    # cv2.waitKey(0)


def page_count(pdf_path, userpw=None):
    if userpw is not None:
        proc = Popen(["pdfinfo", pdf_path, '-upw', userpw],
                     stdout=PIPE, stderr=PIPE)
    else:
        proc = Popen(["pdfinfo", pdf_path], stdout=PIPE, stderr=PIPE)

    out, _ = proc.communicate()
    try:
        # This will throw if we are unable to get page count
        return int(re.search(r'Pages:\s+(\d+)', out.decode("utf8", "ignore")).group(1))
    except:
        raise Exception('Unable to get page count.')
