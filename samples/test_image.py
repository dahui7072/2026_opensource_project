from ultralytics import YOLO
model = YOLO("model/weights/best_V2.pt")
results = model("test.jpeg", conf=0.25, iou=0.7, agnostic_nms=True, show=True)
for r in results:
    for box in r.boxes:
        print(r.names[int(box.cls)], f"{float(box.conf):.2%}")

input("엔터 누르면 종료")