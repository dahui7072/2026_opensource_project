# app.py
import csv
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder="dashboard/templates", static_folder="dashboard/static")

LOG_PATH = "data/violations.csv"

@app.route("/")
def index():
    """대시보드 메인 페이지"""
    return render_template("index.html")

@app.route("/api/violations")
def get_violations():
    """CSV 읽어서 위반 데이터 JSON으로 반환"""
    violations = []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                violations.append(row)
    except FileNotFoundError:
        pass
    return jsonify(violations)

@app.route("/api/stats")
def get_stats():
    """위반 유형별 통계 반환"""
    stats = {"no_helmet": 0, "two_person": 0}
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vtype = row["violation_type"]
                if vtype in stats:
                    stats[vtype] += 1
    except FileNotFoundError:
        pass
    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)