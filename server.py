import flask
from flask import Response
from app import app
import json
import os
from os.path import join
import pyzxing
from PIL import Image
from datetime import datetime
from utils import *

import warnings
warnings.filterwarnings("ignore")

reader = pyzxing.BarCodeReader()

CACHE_DIR = '.cache'
if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

@app.route('/read-extracted-qr', methods=['POST'])
def read_extracted_qr():
    files = flask.request.files.getlist("files")
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
        
        scale = 800 / w
        img = Image.fromarray(org_img).resize((int(w*scale), int(h*scale)), Image.BICUBIC)
        img = np.array(img)
        qr_result = reader.decode_array(img)[0]
        if len(qr_result) > 1:
            response.append(parse_result_into_fields(qr_result, file.filename))
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = adjust_image_gamma_lookuptable(img, 0.6)
            for i in range(1, 6):
                img_i = np.clip(img*(1+i/10), 0, 255)
                img_i = cv2.GaussianBlur(img_i, (5,5), 0)
                cv2.imwrite(f'.cache/{i}.png', img_i)
                img_i = img_i.astype(np.uint8)
                _, img_i = cv2.threshold(img_i, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                qr_result = reader.decode_array(img_i)[0]
                if len(qr_result) > 1 or i == 5:
                    response.append(parse_result_into_fields(qr_result, file.filename))
                    break
            
    return Response(json.dumps(response),  mimetype='application/json')