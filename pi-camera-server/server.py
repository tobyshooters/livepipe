import json
from autobahn.twisted.websocket import WebSocketServerProtocol

import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO

import torch
from torchvision import models, transforms

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def encode_np_array(A, fmt='jpeg'):
    image = Image.fromarray(A)
    buf = BytesIO()
    image.save(buf, fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    prefix = f'data:image/{fmt};base64,'
    return prefix + b64


class WS(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()

    def read(self, payload):
        return json.loads(payload.decode('utf8'))

    def send(self, d):
        self.sendMessage(json.dumps(d).encode('utf8'), isBinary=False)

    def onMessage(self, payload, isBinary):
        d = self.read(payload)
        if d["type"] == "frame":
            img = picam2.capture_array()[:, :, :3]

            pil = Image.fromarray(img)
            pil = pil.resize((160, 120))

            output = model(pil, size=160)
            output.print()
            pd = output.pandas().xyxyn[0]
            people = pd.loc[pd['class'] == 0]

            if len(people) > 0:
                best = people['confidence'].idxmax()
                person = people.iloc[best]
                bbox = [x for x in person[["xmin", "ymin", "xmax", "ymax"]]]

                img = encode_np_array(img)
                self.send({ 
                    "frame": img,
                    "bounds": bbox
                })


if __name__ == '__main__':

    # Setup camera
    from picamera2.picamera2 import *
    import time

    picam2 = Picamera2()
    picam2.start_preview()

    config = picam2.preview_configuration()
    picam2.configure(config)
    picam2.start()

    # Server setup
    from twisted.internet import reactor
    from twisted.web.static import File
    from twisted.web.server import Site
    from autobahn.twisted.websocket import WebSocketServerFactory
    from autobahn.twisted.resource import WebSocketResource

    factory = WebSocketServerFactory()
    factory.protocol = WS

    root = File(".")
    root.putChild(b"ws", WebSocketResource(factory))

    reactor.listenTCP(1234, Site(root))
    reactor.run()
