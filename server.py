import os 
import importlib

import tornado.ioloop
import tornado.web
import tornado.websocket

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
    elif type == "tensor":
        return A.tolist()
    return A


import processing
ui_watcher = Watcher("ui.html")
processing_watcher = Watcher("processing.py")


def get_data():
    data = {}
    for value in processing.interactions:
        try:
            print(f"Running {value}")
            output = value["function"]()
            output = encode(output, value["encoding"])
            data[value["name"]] = output
        except Exception as e:
            print(e)
    return data


class WSHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        if message == "initialize":
            self.write_message(json.dumps(get_data()))

        elif message == "reload?":
            if ui_watcher.has_changed():
                print("Reloading UI")
                self.write_message("reload")

            elif processing_watcher.has_changed():
                try:
                    print("Reloading processing")
                    importlib.reload(processing)
                except Exception as e:
                    print(e)

                self.write_message(json.dumps(get_data()))


if __name__ == "__main__":
    app = tornado.web.Application([
        ("/ws", WSHandler),
        ("/(.*)", tornado.web.StaticFileHandler, {"path": "./", "default_filename": "ui.html"}), 
    ])
    app.listen(1234)
    tornado.ioloop.IOLoop.current().start()
