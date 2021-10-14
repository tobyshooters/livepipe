import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import time

import cv2
import asyncio
import websockets

import json
import base64
from PIL import Image
from io import BytesIO

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

def init_weights(m):
    if type(m) == nn.Linear or type(m) == nn.Conv2d:
        nn.init.xavier_uniform(m.weight)
        m.bias.data.fill_(0.01)

class Model(nn.Module):
    """
    Takes 64x64 image, regresses on (x, y) in (0, 1)^2.
    """
    def __init__(self):
        super().__init__()

        self.c1 = nn.Conv2d(3, 4, kernel_size=3, stride=1, padding=1)
        self.c2 = nn.Conv2d(4, 4, 3, 1, 1)
        self.m1 = nn.MaxPool2d(kernel_size=2)

        self.c3 = nn.Conv2d(4, 6, 3, 1, 1)
        self.c4 = nn.Conv2d(6, 6, 3, 1, 1)
        self.m2 = nn.MaxPool2d(kernel_size=2)

        self.c5 = nn.Conv2d(6, 6, 3, 1, 1)
        self.ll = nn.Linear(16 * 16 * 6, 2)


    def forward(self, x):
        x = F.relu(self.c1(x))
        x = F.relu(self.c2(x))
        x = self.m1(x)

        x = F.relu(self.c3(x))
        x = F.relu(self.c4(x))
        x = self.m2(x)

        x = F.relu(self.c5(x))
        x = self.ll(x.view(-1, 16 * 16 * 6))

        x = torch.sigmoid(x)
        x = 0.5 + x
        return x


def encode_np_array(A):
    image = Image.fromarray(A)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return "data:image/jpeg;base64," + b64


model = Model()
model.apply(init_weights)
criterion = nn.L1Loss()
optimizer = optim.SGD(model.parameters(), lr=1e-2, momentum=0.9)

dataset = {}
prediction = None


async def ws_handler(ws, path):
    while True:
        message = await ws.recv()
        message = json.loads(message)

        if message["type"] == "frame":
            print("\nAsked for a frame!")

            vidcap = cv2.VideoCapture(0)
            _, raw_frame = vidcap.read()
            vidcap.release()

            frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
            small_frame = cv2.resize(frame, (64, 64))

            name = str(time.time()).replace(".", "")
            cv2.imwrite(f"data/{name}.jpg", small_frame)

            frame_t = torch.tensor(small_frame).float()
            frame_t = frame_t.permute(2,0,1).unsqueeze(0)
            frame_t = (frame_t - 127.5) / 255.0
            prediction = model(frame_t)
            pred = prediction.detach().numpy().tolist()[0]
            print(f"Prediction {name}: {pred}")

            display_frame = cv2.resize(frame, (200, 200))
            b64 = encode_np_array(display_frame)
            await ws.send(json.dumps({
                "name": name,
                "frame": b64,
                "pred": pred,
            }))

        elif message["type"] == "label":
            print("Received label:", message["data"])

            # Add to dataset
            dataset[message["data"]["id"]] = message["data"]["pos"]

            # Train on whole dataset
            for name, pos in dataset.items():
                print(name, pos)
                frame = cv2.imread(f"data/{name}.jpg")
                target = torch.tensor([pos]).unsqueeze(0)

                frame_t = torch.tensor(frame).float()
                frame_t = frame_t.permute(2,0,1).unsqueeze(0)
                frame_t = (frame_t - 127.5) / 255.0
                prediction = model(frame_t)

                loss = criterion(prediction, target)
                loss.backward()

            optimizer.step()

            print(f"Loss: {loss}")


start = websockets.serve(ws_handler, "localhost", 1234)

eloop = asyncio.get_event_loop()
eloop.run_until_complete(start)
eloop.run_forever()
