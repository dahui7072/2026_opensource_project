# app.py
from flask import Flask, Response, render_template, jsonify
import cv2
import csv
import sys
import os

sys.path.append(os.path.dirname(__file__))

from detection.detector import detect
from detection.violation import check_violation
from detection.logger import init_logger, log_violation

app = Flask(__name__, template_folder="dashboard/templates", static_folder="dashboard/static")

init_logger()

cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. 탐지
        detections = detect(frame)

        # 2. 위반 판정
        result = check_violation(detections)

        # 3. 로그 저장
        if result != "normal":
            log_violation(result)

        # 4. 화면에 경고 표시
        if result == "two_person":
            cv2.putText(frame, "⚠ 2인 탑승!", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        elif result == "no_helmet":
            cv2.putText(frame, "⚠ 헬멧 미착용!", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)

        # 5. bbox 표시
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            label = d["class"]
            conf = d["confidence"]

            if label == "person":
                color = (0, 255, 0)
            elif label == "helmet":
                color = (255, 200, 0)
            else:
                color = (255, 100, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.0%}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 6. 스트리밍
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/data')
def data():
    violations = []
    try:
        with open("data/violations.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                violations.append(row)
    except FileNotFoundError:
        pass
    return jsonify(violations)


if __name__ == '__main__':
    app.run(debug=False)