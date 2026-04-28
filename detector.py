# Dae.Anuj

from ultralytics import YOLO
import cv2
from controller import DIRECTIONS

# Load YOLO model (auto-downloads first time)
model = YOLO("yolov8n.pt")

# COCO vehicle classes
VEHICLE_CLASSES = {
    2: 1.0,   # car
    3: 0.5,   # motorcycle
    5: 2.5,   # bus
    7: 2.0    # truck
}

def detect_once(caps):

    scores = {}

    for d in DIRECTIONS:

        cap = caps[d]
        weighted_count = 0
        frames_used = 5   # average for stability

        for _ in range(frames_used):

            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()

            if not ret:
                continue

            results = model(frame, conf=0.35, verbose=False)

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])

                    if cls in VEHICLE_CLASSES:
                        weighted_count += VEHICLE_CLASSES[cls]

        # Average score
        scores[d] = round(weighted_count / frames_used, 2)

    return scores