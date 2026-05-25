from flask import Flask, Response, render_template, jsonify
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import platform

import cv2
import csv
import sys
import os

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

# 웹캠 연결
cap = cv2.VideoCapture(0)

# 카메라 해상도 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

current_avg_conf = 0.0

if not cap.isOpened():
    print("카메라 열기 실패")


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

        # 프레임 읽기
        ret, frame = cap.read()

        if not ret:
            continue

        # 프레임 크기 고정
        frame = cv2.resize(frame, (640, 480))

        # 1. 객체 탐지
        detections, avg_conf = detect(frame)
        current_avg_conf = avg_conf  # 실시간 정확도 업데이트

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

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            cv2.putText(
                frame,
                f"{label} {conf:.0%}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        # 6. 영상 스트리밍
        _, buffer = cv2.imencode('.jpg', frame)

        frame_bytes = buffer.tobytes()

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
    try:
        with open("data/violations.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=['timestamp', 'violation_type'])
            for row in reader:
                violations.append(row)
    except FileNotFoundError:
        pass
    return jsonify({
        "violations": violations,
        "avg_confidence": round(current_avg_conf * 100, 1)  # 실시간 정확도 추가
    })


if __name__ == '__main__':

    app.run(debug=False)