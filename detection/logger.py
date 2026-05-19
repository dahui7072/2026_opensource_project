import csv
import os
from datetime import datetime

LOG_PATH = "../data/violations.csv"

def init_logger():
    """CSV 파일 없으면 헤더 포함해서 새로 생성"""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "violation_type"])

def log_violation(violation_type: str):
    """위반 감지 시 호출 — timestamp랑 유형 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, violation_type])