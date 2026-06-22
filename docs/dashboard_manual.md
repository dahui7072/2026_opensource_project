# 대시보드 모듈 명세서

## 1. 개요
Flask 기반 웹 서버와 Chart.js를 활용한 실시간 위반 감지 대시보드입니다.
웹캠 또는 사전 녹화된 영상 파일 스트리밍, 위반 통계 시각화, 누적 로그 조회 기능을 제공합니다.

---

## 2. 실행 방법

```bash
python app.py
```

브라우저에서 `http://127.0.0.1:5001` 접속

> `app.py`의 `USE_WEBCAM` 값으로 웹캠/파일 입력을 전환합니다. `True`면 웹캠, `False`면 `MEDIA_PATHS`에 지정된 영상 및 이미지 파일 목록을 순서대로 순환 재생합니다.

---

## 3. API 라우트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 대시보드 메인 페이지 렌더링 |
| GET | `/video_feed` | 실시간 영상 스트리밍 (MJPEG, 웹캠 또는 영상 파일) |
| GET | `/data` | 오늘 날짜의 위반 기록과 현재 AI 감지 정확도를 JSON으로 반환 |

### `/data` 응답 형식

```json
{
  "violations": [
    {
      "timestamp": "2026-06-20 13:50:11",
      "violation_type": "no_helmet"
    },
    {
      "timestamp": "2026-06-20 13:50:23",
      "violation_type": "two_person"
    }
  ],
  "avg_confidence": 76.1
}
```

- `violations`: 오늘 날짜(`YYYY-MM-DD`)로 시작하는 기록만 필터링되어 반환됨
- `avg_confidence`: 최근 30프레임의 평균 confidence(%)

---

## 4. 모듈 구성

### app.py
Flask 서버 메인 파일. 라우트 정의 및 영상 스트리밍 처리.
- `generate_frames()`: 웹캠 또는 영상 파일에서 프레임을 읽어 탐지 → 위반 판정 → 로그 저장 → 화면 오버레이 순으로 처리 후 MJPEG 스트림으로 전송
- 최근 30프레임의 confidence를 누적해 평균값(`current_avg_conf`)을 계산
- `/data` 라우트: `data/violations.csv`에서 오늘 날짜 기록만 읽어 JSON으로 반환
- 영상 파일과 이미지 파일을 혼합한 재생 목록(`MEDIA_PATHS`)을 순환 재생하며, 이미지는 지정된 시간(`IMAGE_DISPLAY_DURATION`) 동안 표시 후 다음 파일로 전환

### detection/detector.py
YOLOv8 모델(`best.pt`)로 프레임에서 객체(`helmet`, `person`, `kickboard`)를 탐지하고, bbox와 confidence를 반환합니다.

### detection/violation.py
탐지된 객체를 킥보드 단위로 분석해 위반 여부를 판정합니다.
- 킥보드 bbox와 실제로 겹치는 `person`만 그 킥보드의 "탑승자"로 인정
- 탑승자가 2명 이상인 킥보드가 있으면 → `"two_person"`
- 탑승자의 bbox와 겹치는 `helmet`이 하나도 없으면 → `"no_helmet"`
- 최근 30프레임 중 일정 비율(threshold=15) 이상 같은 상태가 지속되어야 위반으로 확정 (일시적 오탐 방지)
- 위 조건에 해당하지 않으면 → `"normal"`

### detection/logger.py
위반 판정 결과를 `data/violations.csv`에 저장합니다.
- 같은 위반이 계속되는 동안은 한 번만 기록하고, 위반이 끝났다가 다시 시작될 때만 새로 기록 (3초마다 중복 기록되던 이전 방식에서 변경됨)

---

## 5. CSV 데이터 구조

```
timestamp,violation_type
2026-06-20 13:50:11,no_helmet
2026-06-20 13:50:23,two_person
```

| 컬럼 | 설명 |
|------|------|
| timestamp | 위반 감지 시각 (`YYYY-MM-DD HH:MM:SS`) |
| violation_type | 위반 유형 (`no_helmet` / `two_person`) |

---

## 6. 대시보드 구성

| 구성 요소 | 설명 |
|-----------|------|
| 실시간 감지 피드 | `/video_feed`에서 MJPEG 스트림 수신 |
| 오늘 총 위반 건수 | 오늘 날짜로 필터링된 CSV 행 수 |
| 헬멧 미착용 수 | 오늘 기록 중 `violation_type == 'no_helmet'` 카운트 |
| 2인 탑승 수 | 오늘 기록 중 `violation_type == 'two_person'` 카운트 |
| AI 감지 정확도 | 최근 30프레임 평균 confidence |
| 시간대별 차트 | 0~23시 막대 차트 (Chart.js, 데이터만 갱신) |
| 위반 유형 비율 | 도넛 차트 (Chart.js, 데이터만 갱신) |
| 누적 로그 테이블 | 오늘 기록 중 최신 30건, 5초마다 자동 갱신 |