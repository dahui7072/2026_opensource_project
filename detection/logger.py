import csv
import os
import time
from datetime import datetime

LOG_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/violations.csv"
)

# 현재 위반 상태
current_violation = None

# 마지막 저장 시간
last_saved_time = 0


def init_logger():

    os.makedirs(
        os.path.dirname(LOG_PATH),
        exist_ok=True
    )

    if not os.path.exists(LOG_PATH):

        with open(
            LOG_PATH,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow([
                "timestamp",
                "violation_type"
            ])


def log_violation(violation_type: str):

    global current_violation
    global last_saved_time

    current_time = time.time()
    elapsed = current_time - last_saved_time

    # 같은 위반 유형이 3초 이내에 이미 기록됐으면 스킵
    if current_violation == violation_type and elapsed < 3:
        return

    # 다른 유형이더라도 1초 이내 연속 기록은 스킵 (유형 전환 노이즈 방지)
    if elapsed < 1:
        return

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        LOG_PATH,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            timestamp,
            violation_type
        ])

    current_violation = violation_type
    last_saved_time = current_time


def reset_violation():

    global current_violation

    # last_saved_time은 건드리지 않음
    # → 위반 해제 직후 재감지돼도 쿨다운이 유지됨
    current_violation = None
