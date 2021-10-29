from pyzbar.pyzbar import decode
import cv2
from PIL import Image
import io
import barcode
from barcode.writer import ImageWriter
import qrcode
import asyncio
import random
import os


async def decode_image(data):
    img = Image.open(io.BytesIO(data))
    decoded = decode(img)
    if len(decoded) >= 1:
        decoded = decoded[0]
    else:
        return []
    return decoded


async def create_new_code(decoded):
    print(decoded)
    if decoded.type != "QRCODE":
        TYPE = barcode.get_barcode_class(decoded.type.lower())
        ready_code = TYPE(decoded.data.decode('UTF-8'), writer=ImageWriter())

        while True:
            new_file_lastname = str(random.getrandbits(100))
            if not any(map(lambda x: new_file_lastname in x, os.listdir('for_temp_img'))):
                break
        path = 'for_temp_img/' + new_file_lastname + '.png'
        ready_code.write(path)
        with open(path, 'rb') as fh:
            fp = fh.read()
        os.remove(path)
        return fp

        # ready_img = Image.open(fp)
        # ready_img.save('res_1.png')
    else:
        img = qrcode.make(decoded.data.decode('UTF-8'))
        while True:
            new_file_lastname = str(random.getrandbits(100))
            if not any(map(lambda x: new_file_lastname in x, os.listdir('for_temp_img'))):
                break
        path = 'for_temp_img/' + new_file_lastname + '.png'
        img.save(path)
        with open(path, 'rb') as fh:
            fp = fh.read()
        os.remove(path)
        return fp


async def do_work(image_bytes):
    decoded = await decode_image(image_bytes)
    if decoded:
        img = await create_new_code(decoded)
        return img
    else:
        return False
