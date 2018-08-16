
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
from module.transform import transform
import os
from pdf2image import convert_from_path
import sys
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


def ocr(img):
    if(args.ocr):
        print("OCR...")
        a = Image.fromarray(img)
        text = pytesseract.image_to_string(a)
        with open('text.txt', "w") as f:
            f.write(text)


def process(image):

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
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        cv2.drawContours(image, [approx], -1, (0, 255, 0), 1)
        if len(approx) == 4:

            screenCnt = approx
            break
        else:
            screenCnt = np.array([[[0, 0]],

                                  [[image.shape[1], 0]],

                                  [[image.shape[1], image.shape[0]]],

                                  [[0, image.shape[0]]]])
            break
    # show the contour (outline) of the piece of paper
    print("STEP 2: Find contours of paper")
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

    ocr(warped)
    return warped

    # cv2.imshow("Original", resize(orig, height=650))
    # cv2.imshow("Scanned", resize(warped, height=650))
    # cv2.waitKey(0)


# construct the argument parser and parse the arguments
a = argparse.ArgumentParser()
a.add_argument("-i", "--image",
               help="Path to the image to be scanned")
a.add_argument("-o", "--ocr", action='store_true',
               help="Do OCR or not", default=False)
a.add_argument("-p", "--pdf",
               help="Path to the image to be scanned")

args = a.parse_args()
if not args.image and not args.pdf:
    a.print_help()
    sys.exit(0)
if args.image and args.pdf:
    print("Use either the 'image' option or 'pdf' option")
    sys.exit(0)
dirName = os.path.dirname(args.image or args.pdf)

ext = os.path.splitext(os.path.basename(args.image or args.pdf))[1]
fileName = os.path.splitext(os.path.basename(args.image or args.pdf))[0]
F = fileName + "_scanned" + ext
if args.pdf:
    images = convert_from_path(args.pdf)
    images_list = []
    for img in images:
        images_list.append(Image.fromarray(process(np.array(img))))
    images_list[0].save(os.path.join(dirName, F), "PDF",
                        resolution=100.0, save_all=True, append_images=images_list[1:])
else:
    img = process(cv2.imread(args.image))
    print("Saving..")
    cv2.imwrite(f"{os.path.join(dirName, F)}", img)
