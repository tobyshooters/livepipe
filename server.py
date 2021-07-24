import os 
import importlib

import asyncio
import websockets

import json
import base64
from PIL import Image
from io import BytesIO


class Watcher:
    def __init__(self, path):
        self.path = path
        self.last_change = 0

    def has_changed(self):
        if os.path.exists(self.path):
            t = os.stat(self.path).st_mtime
            if t != self.last_change:
                self.last_change = t
                return True
        return False


def encode_np_array(A, fmt='jpeg'):
     image = Image.fromarray(A)
     buf = BytesIO()
     image.save(buf, fmt)
     b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
     prefix = f'data:image/{fmt};base64,'
     return prefix + b64


def encode(A, type):
    if type == "image":
        return encode_np_array(A)
    return A


import stage
watcher = Watcher("stage.py")

async def ws_handler(ws, path):
    while True:
        message = await ws.recv()
        if message == "GET_DATA":

            if watcher.has_changed():
                try:
                    print("Reloading stage")
                    importlib.reload(stage)
                except Exception as e:
                    print(e)
            
                data = {}
                for value in stage.run:
                    try:
                        output = value["function"]()
                        output = encode(output, value["type"])
                        data[value["name"]] = output
                    except Exception as e:
                        print(e)

                await ws.send(json.dumps(data))


start = websockets.serve(ws_handler, "localhost", 1234)

eloop = asyncio.get_event_loop()
eloop.run_until_complete(start)
eloop.run_forever()
