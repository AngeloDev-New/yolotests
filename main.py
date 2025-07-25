from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # modelo pré-treinado

# 0 = webcam padrão
model.predict(source=0, show=True, conf=0.6)  # show=True exibe a janela com deteções ao vivo
