import numpy as np

# Decorator to localize encoding and naming close to function definitions
# rather than explicitly in a data structure.
interactions = []
def interact(annotations):
    def decorator(fn):
        interactions.append({**annotations, "function": fn})
        return fn
    return decorator


@interact({"name": "someNumbers", "encoding": "tensor"})
def generate_tensor():
    return np.random.randn(10);


@interact({"name": "frame", "encoding": "image"})
def generate_img():
    img = np.random.randn(300, 300, 3)
    img -= img.min()
    img /- img.max()
    img *= 255.
    img = img.astype(np.uint8)
    return img
