# 모델 모듈 명세서

## 1. 개요

YOLOv8 기반 객체 탐지 모델로 전동 킥보드 관련 위반 상황을 실시간으로 감지합니다.

---

## 2. 감지 클래스

| 클래스 | 설명 | 학습 방식 |
|--------|------|-----------|
| `helmet` | 헬멧 착용 상태 | 직접 촬영 + 공개 데이터셋 |
| `no_helmet` | 헬멧 미착용 상태 | 직접 촬영 + 공개 데이터셋 |
| `person` | 사람 | YOLOv8 사전학습 모델 활용 |
| `kickboard` | 전동 킥보드 | 공개 데이터셋 활용 |

---

## 3. 데이터셋 구성

- **직접 촬영**: 다양한 조명(낮/저녁), 각도(정면/측면/원거리) 환경에서 촬영
- **공개 데이터셋**: Roboflow Universe 헬멧 감지 데이터셋 활용
- **라벨링 도구**: Roboflow
- **데이터 분할**: train 70% / val 20% / test 10%

---

## 4. 학습 환경

| 항목 | 내용 |
|------|------|
| 플랫폼 | Google Colab |
| 가속기 | GPU (T4) |
| 베이스 모델 | YOLOv8n (사전학습 가중치) |
| 학습 방식 | 전이학습 (Fine-tuning) |
| Epochs | 100 |
| 이미지 크기 | 640x640 |

---

## 5. 학습 실행 방법

```bash
cd model
python train.py
```

`train.py` 내부 주요 설정:

```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # 사전학습 모델 로드
model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    project='runs/train'
)
```

---

## 6. 모델 평가 실행 방법

```bash
cd model
python evaluate.py
```

---

## 7. 모델 성능 지표

| 지표 | 값 |
|------|----|
| mAP@50 | 91.2% |
| Precision | - |
| Recall | - |

> 학습 완료 후 실제 수치로 업데이트 필요

---

## 8. 가중치 파일 위치

```
model/weights/best.pt
```

학습 완료 후 자동 생성되며, `detection/detector.py`에서 이 파일을 불러와 탐지에 활용합니다.

---

## 9. data.yaml 구성

```yaml
path: ./dataset
train: images/train
val: images/val
test: images/test

nc: 4
names: ['helmet', 'no_helmet', 'person', 'kickboard']
```