
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2

# construct the argument parser and parse the arguments
a = argparse.ArgumentParser()
a.add_argument("-i", "--image", required=True,
               help="Path to the image to be scanned")
args = a.parse_args()
