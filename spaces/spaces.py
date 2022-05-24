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

pygame.init()
sw, sh = 400, 300
screen = pygame.display.set_mode((sw, sh))

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
            img = pygame.transform.scale(img, (sw, sh))
            screen.blit(img, (0, 0))

            if "bounds" in res:
                bbox = res["bounds"]
                x = bbox[0] * sw
                y = bbox[1] * sh
                w = (bbox[2] - bbox[0]) * sw
                h = (bbox[3] - bbox[1]) * sh

                pygame.draw.line(screen, (0, 0, 0), (0.6 * sw, 0), (0.6 * sw, sh))

                rect = pygame.Surface((w, h))
                rect.set_alpha(50)

                if x + 0.5 * w < 0.6 * sw:
                    rect.fill((255, 0, 0))
                    run_applescript(space(1))
                else:
                    rect.fill((0, 255, 255))
                    run_applescript(space(2))

                screen.blit(rect, (x, y))

                pygame.draw.circle(screen, (0, 255, 0), (x + 0.5 * w, y + 0.5 * h), 3)

            pygame.display.update()
            time.sleep(0.5)

        pygame.quit()

asyncio.run(client())
