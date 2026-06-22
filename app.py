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

USE_WEBCAM = False  # 웹캠 사용 여부 (True: 웹캠, False: 파일 재생)

# [수정] 원래 있던 영상 3개를 모두 포함하고, 이미지 파일도 함께 배치했습니다.
MEDIA_PATHS = [
    os.path.join(os.path.dirname(__file__), "samples","test_video1.mov"),
    os.path.join(os.path.dirname(__file__), "samples","2people.jpg"),   
    os.path.join(os.path.dirname(__file__), "samples","test_video2.mov"),
    os.path.join(os.path.dirname(__file__), "samples","2people_2.jpg"),   
    os.path.join(os.path.dirname(__file__), "samples","test_video3.mov"),
    os.path.join(os.path.dirname(__file__), "samples","2people_3.jpg"),
    os.path.join(os.path.dirname(__file__), "samples","test2.jpg"),   
]
current_media_index = 0

# 이미지가 화면에 머무를 시간 (초 단위)
IMAGE_DISPLAY_DURATION = 4.0 
# 이미지 재생 시 가상 프레임 수 (FPS)
IMAGE_FPS = 30 

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "violations.csv")

# 초기 설정
current_path = MEDIA_PATHS[current_media_index]
is_image = current_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))

if USE_WEBCAM:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    video_fps = 30
else:
    if is_image:
        cap = None
        video_fps = IMAGE_FPS
        image_start_time = time.time()
    else:
        cap = cv2.VideoCapture(current_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30

current_avg_conf = 0.0
recent_confidences = deque(maxlen=30)  # 최근 30프레임 평균용

if not USE_WEBCAM and cap and not cap.isOpened():
    print(f"영상 파일을 찾을 수 없음: {MEDIA_PATHS[current_media_index]}")


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
    global current_avg_conf, cap, current_media_index, video_fps

    # 이미지 처리를 위한 변수 내부 참조용
    image_start_time = time.time()

    while True:
        current_path = MEDIA_PATHS[current_media_index]
        is_current_image = current_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))

        if USE_WEBCAM:
            ret, frame = cap.read()
            if not ret:
                continue
        else:
            if is_current_image:
                # 1. 이미지 파일 처리 (설정한 시간 동안 루프 돌며 모델 통과)
                if time.time() - image_start_time > IMAGE_DISPLAY_DURATION:
                    current_media_index = (current_media_index + 1) % len(MEDIA_PATHS)
                    next_path = MEDIA_PATHS[current_media_index]
                    
                    if next_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        video_fps = IMAGE_FPS
                        image_start_time = time.time()
                    else:
                        if cap is not None: cap.release()
                        cap = cv2.VideoCapture(next_path)
                        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
                    continue
                
                frame = cv2.imread(current_path)
                if frame is None:
                    print(f"이미지 로드 실패: {current_path}")
                    current_media_index = (current_media_index + 1) % len(MEDIA_PATHS)
                    continue
            else:
                # 2. 동영상 파일 처리
                if cap is None or not cap.isOpened():
                    cap = cv2.VideoCapture(current_path)
                    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30

                ret, frame = cap.read()

                if not ret:
                    # 현재 영상이 끝나면 다음 미디어로 순환 전환
                    current_media_index = (current_media_index + 1) % len(MEDIA_PATHS)
                    next_path = MEDIA_PATHS[current_media_index]
                    
                    if cap is not None: 
                        cap.release()
                        cap = None

                    if next_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        video_fps = IMAGE_FPS
                        image_start_time = time.time()
                    else:
                        cap = cv2.VideoCapture(next_path)
                        video_fps = cap.get(cv2.CAP_PROP_FPS) or 30
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
                color = (0, 0, 255)

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