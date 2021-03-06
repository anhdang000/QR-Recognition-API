# Server
import flask
from flask import Response
from flask import request
from app import app

# QR decoder
import pyzxing
from pyzbar import pyzbar

# Image processing
from PIL import Image
from PIL import ImageEnhance

# Utilities
import json
import os
from os.path import join
from datetime import datetime
from utils import *

# Filters
from functions import *

import warnings
warnings.filterwarnings("ignore")

import logging

# Config logger
logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(levelname)s:\t'
        '%(asctime)s'
        '%(filename)s:'
        '%(funcName)s():'
        '%(lineno)d\t'
        '%(message)s'
        ),
    datefmt='%Y-%m-%d %H:%M:%S'
    )

reader = pyzxing.BarCodeReader()

CACHE_DIR = '.cache'
if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

@app.route('/read-extracted-qr', methods=['POST'])
def read_extracted_qr():
    files = request.files.getlist("files")
    method = request.args.get("method")
    response = []

    for file in files:
        save_path = join(
            app.config['UPLOAD_FOLDER'], 
            file.filename.split('.')[0] + '_' + '_'.join(str(datetime.now()).split()) + '.png'
            )
        file.save(save_path)
        file_ext = file.filename.split('.')[-1]
        supported_image_formats = ['bmp', 'jpg', 'JPG', 'jpeg', 'jp2', 'png', 'tiff', 'webp', 'xbm']
        if file_ext not in supported_image_formats:
                response.append({"id": file.filename, "error": "invalid input"})
                continue
        try:
            image = Image.open(save_path)
            if image is None:
                response.append({"id": file.filename, "error": "invalid input"})
                continue
        except:
            response.append({"id": file.filename, "error": "invalid input"})
            continue

        org_img = cv2.imread(save_path)
        h, w = org_img.shape if len(org_img.shape) == 2 else org_img.shape[:2]

        if h / w >= 50 or w / h >=50 or min(h, w) < 50:
            response.append({"id": file.filename, "error": "invalid input"})
            continue

        qr_found = False
        if method == "raw":
            qr_zxing = reader.decode_array(org_img)[0]
            qr_zbar = pyzbar.decode(Image.fromarray(org_img))
            res = parse_result_into_fields(qr_zxing, qr_zbar, file.filename)
            response.append(res)
        else:
            preprocess_methods = [None, 'brightness_contrast', 'invert_softlight', 'li_tri']
            for preprocess_method in preprocess_methods:
                if preprocess_method == 'brightness_contrast':
                    adjusted_img = apply_brightness_contrast(save_path)
                elif preprocess_method == 'invert_softlight':
                    adjusted_img = apply_invert_softlight(save_path)
                elif preprocess_method == 'li_tri':
                    adjusted_img = apply_li_tri(save_path)
                else:
                    adjusted_img = org_img
                adjusted_img = adjusted_img.astype(np.uint8)
                logging.info(f'Applying {preprocess_method}')

                scale = 800 / w
                img = Image.fromarray(adjusted_img).resize((int(w*scale), int(h*scale)), Image.BICUBIC)
                enhancer = ImageEnhance.Contrast(img)
                enhancer.enhance(1.8).save('test.jpg')
                img = np.array(img)

                # Attempt 1
                qr_zxing = reader.decode_array(img)[0]
                qr_zbar = pyzbar.decode(Image.fromarray(img))
                res = parse_result_into_fields(qr_zxing, qr_zbar, file.filename)
                if res["results"] is not None:
                    response.append(res)
                    qr_found = True
                    logging.info(f'Succeed at: {preprocess_method} + rgb')
                else:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(f'.cache/{preprocess_method}_gray.png', img)
                    img = img.astype(np.uint8)
                    
                    # Attempt 2
                    qr_zxing = reader.decode_array(img)[0]
                    qr_zbar = pyzbar.decode(Image.fromarray(img))
                    res = parse_result_into_fields(qr_zxing, qr_zbar, file.filename)
                    if res["results"] is not None:
                        qr_found = True
                        response.append(res)
                        logging.info(f'Succeed at: {preprocess_method} + gray')

                    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    cv2.imwrite(f'.cache/{preprocess_method}_bin.png', img)
                    
                    # Attempt 3
                    qr_zxing = reader.decode_array(img)[0]
                    qr_zbar = pyzbar.decode(Image.fromarray(img))
                    res = parse_result_into_fields(qr_zxing, qr_zbar, file.filename)
                    if res["results"] is not None:
                        qr_found = True
                        response.append(res)
                        logging.info(f'Succeed at {file.filename} by: {preprocess_method} + binary')
                if qr_found is True:
                    break
            if qr_found is False:
                response.append(res)
                logging.info(f'Failed at {file.filename}')

    return Response(json.dumps(response),  mimetype='application/json')