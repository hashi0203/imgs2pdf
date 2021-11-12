import numpy as np
import cv2
from PIL import Image
import pyheif

def pil2cv(img_pil):
    img_cv = np.array(img_pil, dtype=np.uint8)
    if img_cv.ndim == 3:
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    return img_cv

def read_heic(filename):
    img_heic = pyheif.read(filename)
    img_pil = Image.frombytes(
        img_heic.mode,
        img_heic.size,
        img_heic.data,
        "raw",
        img_heic.mode,
        img_heic.stride,
        )
    if img_pil.mode == 'RGBA':
        img_pil = img_pil.convert('RGB')
    return pil2cv(img_pil)
