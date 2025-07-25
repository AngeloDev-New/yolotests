from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # modelo base (nano)
model.train(data='dados.yaml', epochs=100, imgsz=640)