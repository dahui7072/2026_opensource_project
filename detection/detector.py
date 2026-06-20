from ultralytics import YOLO
import cv2

model = YOLO("model/weights/best.pt")

def detect(frame):
    results = model(frame, conf=0.25, iou=0.7, agnostic_nms=True, verbose=False)
    detections = []
    confidences = []  # confidence 평균 계산용

    for box in results[0].boxes:
        cls = int(box.cls)
        conf = float(box.conf)
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = results[0].names[cls]

        detections.append({
            "class": label,
            "bbox": [x1, y1, x2, y2],
            "confidence": conf
        })
        confidences.append(conf)

    # confidence 평균값 계산해서 같이 반환
    avg_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

    return detections, avg_confidence

