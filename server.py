import os
from os.path import join

from resize_bicubic import bicubic

from fastapi import FastAPI
from fastapi import UploadFile, File, Form

import pyzxing
from PIL import Image

from datetime import datetime
from utils import *

import warnings
warnings.filterwarnings("ignore")

reader = pyzxing.BarCodeReader()

app = FastAPI()

CACHE_DIR = '.cache'
if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

@app.post('/read-extracted-qr')
async def read_extracted_qr(qr_image: UploadFile = File(...)):
    # Check file format
    file_ext = qr_image.filename.split('.')[-1]
    supported_image_formats = ['bmp', 'jpg', 'jpeg', 'jp2', 'png', 'tiff', 'webp', 'xbm']
    if file_ext not in supported_image_formats:
            return {
                "error": "invalid input"
                }
    try:
        image = Image.open(qr_image.file).convert('RGB')
        if image is None:
            return {"error": "invalid input"}
    except:
        return {"error": "invalid input"}

    save_path = join(CACHE_DIR, qr_image.filename.split('.')[0] + '_' + '_'.join(str(datetime.now()).split()) + '.png')
    await chunked_copy(qr_image, save_path)

    org_img = cv2.imread(save_path)
    h, w = org_img.shape if len(org_img.shape) == 2 else org_img.shape[:2]

    scale = 800 / w
    coeff = -1/2
    if max(h, w) < 800:
        img = cv2.resize(org_img, None, fx=scale, fy=scale)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = adjust_image_gamma_lookuptable(img, 0.6)
    img = np.clip(img*1.7, 0, 255)
    img = cv2.GaussianBlur(img, (5,5), 0)
    img = img.astype(np.uint8)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imwrite(save_path, img)
    qr_result = reader.decode_array(img)[0]
    
    if len(qr_result) > 1:
        return parse_result_into_fields(qr_result)
    else:
        img = bicubic(org_img, scale/2, coeff)
        img = bicubic(img, scale/2, coeff)
        qr_result = reader.decode_array(img)[0]
        return parse_result_into_fields(qr_result)