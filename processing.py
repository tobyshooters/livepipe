import numpy as np
import cv2

interactions = []
def interact(encoding, reload=None):
    def decorator(fn):
        interactions.append({
            "name": fn.__name__,
            "function": fn,
            "encoding": encoding,
            "reload": reload,
        })
        return fn
    return decorator


@interact(encoding="tensor")
def someNumbers():
    return np.random.randint(2, size=10)


reader = cv2.VideoCapture(0)

@interact(encoding="image", reload="always")
def frame():
    _, frame = reader.read()
    H, W = frame.shape[:2]
    frame = cv2.resize(frame, (400, int(H/W * 400)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame
