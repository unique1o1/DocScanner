
import numpy as np
import argparse
import cv2
import os
from pdf2image import convert_from_path
import sys
from PIL import Image
from module import ocr, process, threshold_local, resize, page_count


def myrange(a):
    for i in range(1, (a//20)+2):
        if 20*i < a:
            yield 20*i
        else:
            yield a


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
    images_list = []
    page_no = page_count(args.pdf)
    if page_no > 33:
        images = []
        prev_count = 1
        for i in myrange(page_no):

            images.extend(convert_from_path(
                args.pdf, first_page=prev_count, last_page=i))
            prev_count = i+1
    else:
        images = convert_from_path(args.pdf)

    for img in images:
        images_list.append(Image.fromarray(process(np.array(img), args.ocr)))

    images_list[0].save(os.path.join(dirName, F), "PDF",
                        resolution=100.0, save_all=True, append_images=images_list[1:])
else:
    img = process(cv2.imread(args.image), args.ocr)
    print("Saving..")
    cv2.imwrite(f"{os.path.join(dirName, F)}", img)
