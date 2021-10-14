import cv2
import numpy as np

class Video:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def seek(self, t):
        frame_number = np.floor(t * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def get_next_frame(self):
        success, frame = self.cap.read()
        if not success: return False
        H, W, _ = frame.shape
        frame = cv2.resize(frame, (400, int(400 * H / W)))
        return frame

    def get_frame_at(self, t):
        self.seek(t)
        return self.get_next_frame()

    def frames(self):
        frame = self.get_next_frame()
        while frame is not False:
            yield frame
            frame = self.get_next_frame()


lk_params = dict(winSize  = (15, 15),
                 maxLevel = 2,
                 criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def propagate(video, annotation):
    video.seek(annotation["timestamp"])

    curr_frame = video.get_next_frame()
    H, W = curr_frame.shape[:2]

    pt = np.array([[
        annotation["x"] * W,
        annotation["y"] * H
    ]]).astype(np.float32)

    results = []
    for i in range(1, 10 + 1):
        next_frame = video.get_next_frame()
        next_pt, _, _ = cv2.calcOpticalFlowPyrLK(
                next_frame, curr_frame, pt, None, **lk_params)
        return_pt, _, _ = cv2.calcOpticalFlowPyrLK(
                curr_frame, next_frame, next_pt, None, **lk_params)

        err = np.abs(pt - return_pt).max()
        curr_frame = next_frame
        
        if err < 1:
            results.append({
                "x": float(next_pt[0, 0]) / W,
                "y": float(next_pt[0, 1]) / H,
                "type": "server",
                "timestamp": annotation["timestamp"] + (i / video.fps)
            })
            pt = next_pt
        else:
            # If too much error, keep the point
            results.append({
                "x": float(pt[0, 0]) / W,
                "y": float(pt[0, 1]) / H,
                "type": "server",
                "timestamp": annotation["timestamp"] + (i / video.fps)
            })

    return results
