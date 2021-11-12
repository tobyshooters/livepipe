import json
from autobahn.twisted.websocket import WebSocketServerProtocol

class WS(WebSocketServerProtocol):
    def __init__(self):
        super().__init__()

    def onOpen(self):
        self.send("HELLO WORLD")

    def onMessage(self, payload, isBinary):
        d = self.read(payload)
        if d["type"] == "frame":
            self.send({
                "frame": None,
            })

    def read(self, payload):
        return json.loads(d.decode('utf8'))

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
