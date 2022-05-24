import pygame
from pygame.locals import *
import io
import base64

from subprocess import run
import time

import asyncio
import websockets
import json

def run_applescript(script):
    p = run(['osascript', '-e', script])
    return p.stdout

def space(n):
    pre = 'tell application "System Events" to key code '
    post = ' using {control down}'
    return pre + str(17 + n) + post

# run_applescript(space(2))


pygame.init()
w, h = 640, 480
screen = pygame.display.set_mode((w, h))

async def client():
    async with websockets.connect("ws://raspberrypi.local:1234/ws") as ws:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            print("Requesting frame")
            await ws.send(json.dumps({"type": "frame"}))
            res = await ws.recv()
            res = json.loads(res)

            prefix = 'data:image/jpeg;base64,'
            data = res["frame"][len(prefix):]
            output = io.BytesIO(base64.b64decode(data))
            img = pygame.image.load(output)
            screen.blit(img, (0, 0))

            if "bounds" in res:
                bbox = res["bounds"]
                x = bbox[0] * 640
                y = bbox[1] * 480
                w = (bbox[2] - bbox[0]) * 640
                h = (bbox[3] - bbox[1]) * 480

                rect = pygame.Surface((w, h))
                rect.set_alpha(50)
                rect.fill((0, 255, 255))
                screen.blit(rect, (x, y))

            pygame.display.update()
            time.sleep(0.5)

        pygame.quit()

asyncio.run(client())
