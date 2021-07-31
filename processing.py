import numpy as np

interactions = []
def interact(encoding):
    def decorator(fn):
        interactions.append({
            "name": fn.__name__,
            "function": fn,
            "encoding": encoding,
        })
        return fn
    return decorator


@interact(encoding="tensor")
def someNumbers():
    return np.random.randn(10);


@interact(encoding="image")
def frame():
    img = np.random.randn(300, 300, 3)
    img -= img.min()
    img /- img.max()
    img *= 255.
    img = img.astype(np.uint8)
    return img
