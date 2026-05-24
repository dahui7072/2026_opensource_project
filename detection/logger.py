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

    # 같은 위반 상태 + 3초 이내면 저장 안 함
    if (
        current_violation == violation_type
        and current_time - last_saved_time < 3
    ):
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

    current_violation = None