import os
from os.path import join

from resize_bicubic import bicubic

from fastapi import FastAPI
from fastapi import UploadFile, File, Form
from typing import List

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
async def read_extracted_qr(files: List[UploadFile] = File(...)):
    response = []
    for qr_image in files:
        file_ext = qr_image.filename.split('.')[-1]
        supported_image_formats = ['bmp', 'jpg', 'JPG', 'jpeg', 'jp2', 'png', 'tiff', 'webp', 'xbm']
        if file_ext not in supported_image_formats:
                response.append({"id": qr_image.filename, "error": "invalid input"})
                continue
        try:
            image = Image.open(qr_image.file).convert('RGB')
            if image is None:
                response.append({"id": qr_image.filename, "error": "invalid input"})
                continue
        except:
            response.append({"id": qr_image.filename, "error": "invalid input"})
            continue

        save_path = join(CACHE_DIR, qr_image.filename.split('.')[0] + '_' + '_'.join(str(datetime.now()).split()) + '.png')
        await chunked_copy(qr_image, save_path)

        org_img = cv2.imread(save_path)
        h, w = org_img.shape if len(org_img.shape) == 2 else org_img.shape[:2]

        if h / w >= 50 or w / h >=50 or min(h, w) < 50:
            response.append({"id": qr_image.filename, "error": "invalid input"})
            continue
        
        scale = 800 / w
        coeff = -1/2
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
            response.append(parse_result_into_fields(qr_result, qr_image.filename))
        else:
            img = bicubic(org_img, scale/2, coeff)
            img = bicubic(img, scale/2, coeff)
            qr_result = reader.decode_array(img)[0]
            response.append(parse_result_into_fields(qr_result, qr_image.filename))

    return response