from collections import deque

recent_detections = deque(maxlen=30)


def is_overlapping(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    return x1 < x2 and y1 < y2


def check_violation(detections):
    kickboards = [d for d in detections if d["class"] == "kickboard"]
    persons    = [d for d in detections if d["class"] == "person"]
    helmets    = [d for d in detections if d["class"] == "helmet"]

    print(f"kb:{len(kickboards)} person:{len(persons)} helmet:{len(helmets)}")

    frame_has_rider  = False
    frame_two_person = False
    frame_no_helmet  = False

    # 킥보드 한 대씩 따로 검사
    for kb in kickboards:
        # 이 킥보드 bbox랑 실제로 겹치는 사람만 "이 킥보드 탑승자"
        riders = [p for p in persons if is_overlapping(kb["bbox"], p["bbox"])]

        if not riders:
            continue  # 사람이 안 탄(주차된) 킥보드는 무시

        frame_has_rider = True

        if len(riders) >= 2:
            frame_two_person = True

        # 탑승자 몸통이랑 겹치는 헬멧이 있는지 확인
        has_helmet = any(
            is_overlapping(p["bbox"], h["bbox"])
            for p in riders
            for h in helmets
        )
        if not has_helmet:
            frame_no_helmet = True

    recent_detections.append({
        "has_rider": frame_has_rider,
        "two_person": frame_two_person,
        "no_helmet": frame_no_helmet,
    })

    THRESHOLD = 15  # 최근 30프레임 중 절반 이상 지속돼야 위반으로 판단

    rider_count      = sum(1 for f in recent_detections if f["has_rider"])
    two_person_count = sum(1 for f in recent_detections if f["two_person"])
    no_helmet_count  = sum(1 for f in recent_detections if f["no_helmet"])

    if rider_count < THRESHOLD:
        return "normal"

    if two_person_count >= THRESHOLD:
        return "two_person"

    if no_helmet_count >= THRESHOLD:
        return "no_helmet"

    return "normal"