
import numpy as np
import argparse
import cv2
import os
from pdf2image import convert_from_path
import sys
from PIL import Image
from module import ocr, process, threshold_local, resize, page_count

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
        images_list.append(Image.fromarray(process(np.array(img), args.ocr)))
    images_list[0].save(os.path.join(dirName, F), "PDF",
                        resolution=100.0, save_all=True, append_images=images_list[1:])
else:
    img = process(cv2.imread(args.image), args.ocr)
    print("Saving..")
    cv2.imwrite(f"{os.path.join(dirName, F)}", img)
