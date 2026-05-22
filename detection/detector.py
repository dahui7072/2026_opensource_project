# detection/detector.py
from ultralytics import YOLO
import cv2

model = YOLO("model/weights/best.pt")

def detect(frame):
    results = model(frame)
    detections = []

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

    return detections


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # 웹캠

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detect(frame)

        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            label = d["class"]
            conf = d["confidence"]

            if label == "two_people":
                color = (0, 0, 255)   # 빨간색
                text = f"2인 탑승! {conf:.0%}"
            elif label == "one_people":
                color = (0, 255, 0)   # 초록색
                text = f"정상 {conf:.0%}"
            else:
                color = (255, 200, 0) # 노란색
                text = f"킥보드 {conf:.0%}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("킥보드 2인 탑승 감지", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()