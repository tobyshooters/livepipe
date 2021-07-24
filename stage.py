import numpy as np

def generate_img():
    img = np.random.randn(300, 300, 3)
    img -= img.min()
    img /- img.max()
    img *= 255.
    img = img.astype(np.uint8)
    return img

run = [
    {
        "name": "frame",
        "type": "image",
        "function": generate_img,
    }
]
