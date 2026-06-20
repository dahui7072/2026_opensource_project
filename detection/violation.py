from collections import deque

recent_detections = deque(maxlen=30)

def is_overlapping(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    return x1 < x2 and y1 < y2

def is_near(box1, box2, margin=150):
    x1 = max(box1[0], box2[0]) - margin
    y1 = max(box1[1], box2[1]) - margin
    x2 = min(box1[2], box2[2]) + margin
    y2 = min(box1[3], box2[3]) + margin
    return x1 < x2 and y1 < y2

def check_violation(detections):
    kickboards = [d for d in detections if d["class"] == "kickboard"]
    persons    = [d for d in detections if d["class"] == "person"]
    helmets    = [d for d in detections if d["class"] == "helmet"]

    print(f"kb:{len(kickboards)} person:{len(persons)} helmet:{len(helmets)}")

    # 현재 프레임 클래스 list로 저장 (person 개수 파악 위해 list 사용)
    detected_classes = [d["class"] for d in detections]
    recent_detections.append(detected_classes)

    # 최근 30프레임 누적
    accumulated = set()
    for frame_classes in recent_detections:
        accumulated |= set(frame_classes)

    has_kb     = "kickboard" in accumulated
    has_helmet = "helmet" in accumulated

    if not has_kb:
        return "normal"

    # 2인 탑승: 30프레임 중 10번 이상 person:2 나왔을 때만 판정
    two_person_count = sum(
        1 for frame_classes in recent_detections
        if frame_classes.count("person") >= 2
    )
    if two_person_count >= 10:
        return "two_person"

    # 헬멧 미착용: 30프레임 누적 기준
    if not has_helmet:
        return "no_helmet"

    return "normal"