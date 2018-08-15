
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2


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


# construct the argument parser and parse the arguments
a = argparse.ArgumentParser()
a.add_argument("-i", "--image", required=True,
               help="Path to the image to be scanned")
args = a.parse_args()
print(args.image)
image = cv2.imread(args.image)
orig = image.copy()
image = resize(image, height=500)
cv2.imshow("asd", image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 1)
edged = cv2.Canny(gray, 75, 200)

cv2.imshow("asd", edged)

cv2.waitKey(0)
cv2.destroyAllWindows()
