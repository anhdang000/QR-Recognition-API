import cv2
import numpy as np

# Save file utility
CHUNK_SIZE = 2 ** 20  # 1MB
async def chunked_copy(src, dst):
    await src.seek(0)
    with open(dst, "wb") as buffer:
        while True:
            contents = await src.read(CHUNK_SIZE)
            if not contents:
                break
            buffer.write(contents)

def adjust_image_gamma_lookuptable(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    table = np.array([((i / 255.0) ** gamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def parse_result_into_fields(qr_result, filename):
    if len(qr_result) > 1:
        result = qr_result["parsed"].decode('utf-8').split('|')
        result = dict(zip([f'field_{i}' for i in range(len(result))], result))
        return {
            "id": filename,
            "results": result, 
            "status": "success"
            }
    else:
        return {
            "id": filename, 
            "results": None, 
            "status": "fail"
            }