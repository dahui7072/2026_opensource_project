def is_overlapping(box1, box2):
    """두 bbox가 겹치는지 확인"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    return x1 < x2 and y1 < y2

def check_violation(detections):
    """
    detections: detector.py가 넘겨주는 리스트
    [{"class": "kickboard", "bbox": [x1,y1,x2,y2], "confidence": 0.91}, ...]
    
    반환값: "two_person" | "no_helmet" | "normal"
    """
    kickboards = [d for d in detections if d["class"] == "kickboard"]
    persons    = [d for d in detections if d["class"] == "person"]
    helmets    = [d for d in detections if d["class"] == "helmet"]

    for kb in kickboards:
        # kickboard 근처 person 찾기
        riders = [p for p in persons if is_overlapping(kb["bbox"], p["bbox"])]

        # 2인 탑승 판정
        if len(riders) >= 2:
            return "two_person"

        # 헬멧 미착용 판정
        if len(riders) == 1:
            rider_box = riders[0]["bbox"]
            helmet_found = any(is_overlapping(rider_box, h["bbox"]) for h in helmets)
            if not helmet_found:
                return "no_helmet"

    return "normal"