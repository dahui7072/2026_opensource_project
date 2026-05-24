# 대시보드 모듈 명세서

## 1. 개요

Flask 기반 웹 서버와 Chart.js를 활용한 실시간 위반 감지 대시보드입니다.  
웹캠 영상 스트리밍, 위반 통계 시각화, 누적 로그 조회 기능을 제공합니다.

---

## 2. 실행 방법

```bash
python app.py
```

브라우저에서 `http://127.0.0.1:5000` 접속

> 웹캠이 연결된 상태에서 실행해야 합니다.

---

## 3. API 라우트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 대시보드 메인 페이지 렌더링 |
| GET | `/video_feed` | 실시간 웹캠 영상 스트리밍 (MJPEG) |
| GET | `/data` | 위반 기록 JSON 반환 |

### `/data` 응답 형식

```json
[
  {
    "timestamp": "2026-05-24 21:49:08",
    "violation_type": "no_helmet"
  },
  {
    "timestamp": "2026-05-24 21:49:10",
    "violation_type": "two_person"
  }
]
```

---

## 4. 모듈 구성

### app.py
Flask 서버 메인 파일. 라우트 정의 및 영상 스트리밍 처리.

- `generate_frames()`: 웹캠 프레임을 읽어 탐지 → 위반 판정 → 로그 저장 → 화면 오버레이 순으로 처리 후 MJPEG 스트림으로 전송
- `/data` 라우트: `data/violations.csv`를 읽어 JSON으로 반환

### detection/detector.py
YOLOv8 모델(`best.pt`)로 프레임에서 객체를 탐지하고 결과를 반환합니다.

### detection/violation.py
탐지된 객체를 기반으로 위반 여부를 판정합니다.

- `no_helmet` 클래스 탐지 시 → `"no_helmet"` 반환
- kickboard bbox 내 person 2개 이상 → `"two_person"` 반환
- 정상 → `"normal"` 반환

### detection/logger.py
위반 판정 결과를 `data/violations.csv`에 저장합니다.

---

## 5. CSV 데이터 구조

```
2026-05-24 21:49:08,no_helmet
2026-05-24 21:49:10,two_person
```

| 컬럼 | 설명 |
|------|------|
| timestamp | 위반 감지 시각 (`YYYY-MM-DD HH:MM:SS`) |
| violation_type | 위반 유형 (`no_helmet` / `two_person`) |

> CSV에 헤더 행 없음. `app.py`에서 `fieldnames`로 컬럼명 지정하여 파싱.

---

## 6. 대시보드 구성

| 구성 요소 | 설명 |
|-----------|------|
| 실시간 감지 피드 | `/video_feed`에서 MJPEG 스트림 수신 |
| 오늘 총 위반 건수 | CSV 전체 행 수 |
| 헬멧 미착용 수 | `violation_type == 'no_helmet'` 카운트 |
| 2인 탑승 수 | `violation_type == 'two_person'` 카운트 |
| 시간대별 차트 | 0~23시 막대 차트 (Chart.js) |
| 위반 유형 비율 | 도넛 차트 (Chart.js) |
| 누적 로그 테이블 | 최신 30건, 5초마다 자동 갱신 |