
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
from module.transform import transform
import os

import pytesseract
from PIL import Image


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


# construct the argument parser and parse the arguments
a = argparse.ArgumentParser()
a.add_argument("-i", "--image", required=True,
               help="Path to the image to be scanned")

args = a.parse_args()
print(args.image)
dirName = os.path.dirname(args.image)

ext = os.path.splitext(os.path.basename(args.image))[1]
fileName = os.path.splitext(os.path.basename(args.image))[0]
image = cv2.imread(args.image)
orig = image.copy()
ratio = image.shape[0] / 500
image = resize(image, height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
print("STEP 1: Edge Detection")
cv2.imshow("Image", gray)
cv2.imshow("Edged", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()
# find the contours in the edged image, keeping only the
# largest ones, and initialize the screen contour
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if is_cv2() else cnts[1]
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

# loop over the contours
for c in cnts:
    # approximate the contour
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # if our approximated contour has four points, then we
    # can assume that we have found our screen

    if len(approx) == 4:

        print(cv2.boundingRect(approx))
        screenCnt = approx
        break

# show the contour (outline) of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 1)
cv2.imshow("Outline", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
print("STEP 3: Apply perspective transform")

warped = transform(orig, screenCnt.reshape(4, 2) * ratio)
warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

warped = (warped > threshold_local(
    warped, 11, offset=10)).astype("uint8") * 255
if warped.shape[0] < warped.shape[1]:
    warped = cv2.rotate(warped, rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)

# show the original and scanned images
print("OCR...")
a = Image.fromarray(warped)
text = pytesseract.image_to_string(a)
with open('text.txt', "w") as f:
    f.write(text)
print("Saving..")

F = fileName + "_scanned"+ext
cv2.imwrite(f"{os.path.join(dirName, F)}", warped)

# cv2.imshow("Original", resize(orig, height=650))
# cv2.imshow("Scanned", resize(warped, height=650))
# cv2.waitKey(0)
