from flask import Flask, Response, render_template, jsonify
from PIL import ImageFont, ImageDraw, Image
from collections import deque
from datetime import datetime
import numpy as np
import platform

import cv2
import csv
import sys
import os
import time

sys.path.append(os.path.dirname(__file__))

from detection.detector import detect
from detection.violation import check_violation

from detection.logger import (
    init_logger,
    log_violation,
    reset_violation
)

app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)

# logger 초기화
init_logger()

USE_WEBCAM = False  # 웹캠 사용 여부 (True: 웹캠, False: 영상 파일)
VIDEO_PATH = os.path.join(os.path.dirname(__file__), "test_video3.mov")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "violations.csv")

cap = cv2.VideoCapture(0 if USE_WEBCAM else VIDEO_PATH)

if USE_WEBCAM:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

video_fps = cap.get(cv2.CAP_PROP_FPS) or 30

current_avg_conf = 0.0
recent_confidences = deque(maxlen=30)  # 최근 30프레임 평균용

if not cap.isOpened():
    print("웹캠 열기 실패" if USE_WEBCAM else f"영상 파일을 찾을 수 없음: {VIDEO_PATH}")


def get_font(size=36):
    system = platform.system()
    try:
        if system == "Darwin":  # Mac
            return ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", size)
        elif system == "Windows":
            return ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", size)
        else:  # Linux
            return ImageFont.truetype("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", size)
    except:
        return ImageFont.load_default()

def draw_korean_text(frame, text, pos, color):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = get_font(36)
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def generate_frames():

    global current_avg_conf

    while True:

        ret, frame = cap.read()

        if not ret:
            if not USE_WEBCAM:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 480))

        # 1. 객체 탐지
        detections, avg_conf = detect(frame)

        if avg_conf > 0:
            recent_confidences.append(avg_conf)

        current_avg_conf = (
            sum(recent_confidences) / len(recent_confidences)
            if recent_confidences else 0.0
        )

        print([d["class"] for d in detections])

        # 2. 위반 판정
        result = check_violation(detections)

        # 3. 로그 저장
        if result != "normal":
            log_violation(result)
        else:
            reset_violation()

        # 4. 경고 문구 표시
        if result == "two_person":
            frame = draw_korean_text(frame, "※ 2인 탑승 감지", (30, 50), (255, 50, 50))
        elif result == "no_helmet":
            frame = draw_korean_text(frame, "※ 헬멧 미착용 감지", (30, 50), (255, 140, 0))

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
            cv2.putText(
                frame, f"{label} {conf:.0%}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

        # 6. 영상 스트리밍
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        if not USE_WEBCAM:
            time.sleep(1 / video_fps)

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame_bytes +
            b'\r\n'
        )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/data')
def data():
    violations = []
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["timestamp"].startswith(today):
                    violations.append(row)
    except FileNotFoundError:
        pass

    return jsonify({
        "violations": violations,
        "avg_confidence": round(current_avg_conf * 100, 1)
    })


if __name__ == '__main__':
    app.run(debug=False, port=5001)