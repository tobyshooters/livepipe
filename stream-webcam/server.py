import asyncio
import websockets

import cv2
import numpy as np

import base64
from PIL import Image
from io import BytesIO

from datetime import datetime
import time


def encode_np_array(A, fmt='jpeg'):
     image = Image.fromarray(A)
     buf = BytesIO()
     image.save(buf, fmt)
     b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
     prefix = f'data:image/{fmt};base64,'
     return prefix + b64


def postprocess(frame, size=240, to_rgb=True):
    H, W, _ = frame.shape
    frame = cv2.resize(frame, (size, int(size * H/W)))
    if to_rgb:
        frame = frame[:, :, ::-1]
    return frame


async def ws_handler(ws, path):
    webcam = cv2.VideoCapture(0)
    while True:
        message = await ws.recv()

        if message == "STREAM":
            _, raw_frame = webcam.read()
            frame = postprocess(raw_frame)
            await ws.send(encode_np_array(frame))


start = websockets.serve(ws_handler, "localhost", 1234)

eloop = asyncio.get_event_loop()
eloop.run_until_complete(start)
eloop.run_forever()
