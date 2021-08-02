from PIL import Image
import cv2
import numpy as np
from fastapi import FastAPI
from fastapi import UploadFile, File, Form
import zxing
from ISR.models import RDN
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

reader = zxing.BarCodeReader()
rdn = RDN(weights='psnr-small')

app = FastAPI()

@app.post('/read-qr')
async def read_qr(
    xmin: int = Form(...), ymin: int = Form(...), xmax: int = Form(...), ymax: int = Form(...), 
    image: UploadFile = File(...)):
    # Check file format
    file_ext = image.filename.split('.')[-1]
    supported_image_formats = ['bmp', 'jpg', 'jpeg', 'jp2', 'png', 'tiff', 'webp', 'xbm']
    if file_ext not in supported_image_formats:
        return {
            "error": "cannot read the imported file"
            }
    try:
        img = Image.open(image.file).convert('RGB')
    except:
        return {"error": f"file {image.filename} could not be read"}
    
    roi = np.array(img)[ymin: ymax, xmin:xmax]
    roi = cv2.resize(roi, (roi.shape[1]*4, roi.shape[0]*4))
    save_path = image.filename.split('.')[0] + '_' + '_'.join(str(datetime.now()).split()) + '.jpg'
    cv2.imwrite(save_path, roi)

    qrcode = reader.decode(save_path)

    return {"result": qrcode}

@app.post('/read-extracted-qr')
async def read_extracted_qr(qr_image: UploadFile = File(...)):
    img = Image.open(qr_image.file).convert('RGB')
    img = np.array(img)
    sr_img = rdn.predict(img)
    sr_img = Image.fromarray(sr_img)
    save_path = qr_image.filename.split('.')[0] + '_' + '_'.join(str(datetime.now()).split()) + '.jpg'
    sr_img.save(save_path, "JPEG", quality=80, optimize=True, progressive=True)
    qrcode = reader.decode(save_path)

    return {"result": qrcode}