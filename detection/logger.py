import csv
import os
import time
from datetime import datetime

LOG_PATH = os.path.join(
    os.path.dirname(__file__),
    "../data/violations.csv"
)

# 마지막 저장 시간
last_log_time = 0

# 같은 위반 저장 제한 시간(초)
COOLDOWN = 5


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

    global last_log_time

    current_time = time.time()

    # 마지막 저장 후 5초 안이면 저장 안 함
    if current_time - last_log_time < COOLDOWN:
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

    # 마지막 저장 시간 갱신
    last_log_time = current_time