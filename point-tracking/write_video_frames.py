from propagate import Video
import sys
import os
import cv2

path = sys.argv[1]
video = Video(path)

target = path.split(".")[0]
os.makedirs(target, exist_ok=True)

for i, frame in enumerate(video.frames()):
    cv2.imwrite(f"{target}/{i:05}.png", frame)
    if i == 200: break
