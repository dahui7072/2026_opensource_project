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

    # 이미 같은 위반이 진행 중이면 새로 기록하지 않음 (위반 시작 시점에만 1번 기록)
    if current_violation == violation_type:
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
    last_saved_time = time.time()


def reset_violation():
    global current_violation
    # 위반 상태가 풀리면 초기화 → 다음에 다시 위반 시작되면 새로 기록됨
    current_violation = None