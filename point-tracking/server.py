import os
import json
from autobahn.twisted.websocket import WebSocketServerProtocol

from propagate import Video, propagate

class WS(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()
        self.video = None
        self.annotations = []

    def onOpen(self):
        self.send({
            "type": "LISTING",
            "message": os.listdir('fs')
        })

    def onMessage(self, payload, isBinary):
        d = json.loads(payload.decode('utf8'))

        if d["type"] == "SELECTION":
            self.video = Video(d["message"])

        if d["type"] == "ANNOTATION":
            annotation = d["message"]
            self.annotations.append(annotation)

            print(f"Received {annotation}.")

            self.send({
                "type": "PROPAGATION",
                "message": propagate(self.video, annotation)
            })

            print(f"Finished propagation.")

    def send(self, d):
        self.sendMessage(json.dumps(d).encode('utf8'), isBinary=False)


if __name__ == '__main__':
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
