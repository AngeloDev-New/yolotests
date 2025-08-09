# from google.colab import drive
# drive.mount('/content/drive')
# !pip install ultralytics

# Caminhos
dataset_path = '/content/drive/MyDrive/dataset'
dados = '/content/drive/MyDrive/dados.yaml'
destino = '/content/drive/MyDrive/v8n.pt'  # destino no seu Google Drive

# Importa o modelo
from ultralytics import YOLO

# Cria o modelo
model = YOLO('yolov8n.pt')  # modelo base nano

# # Treina o modelo
# model.train(data=dados, epochs=100, imgsz=600)
# Treina o modelo com augmentation
model.train(
    data=dados,
    epochs=100,
    imgsz=600,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10,
    translate=0.1,
    scale=0.5,
    shear=2.0,
    flipud=0.2,
    fliplr=0.5
)
# Caminho do best.pt gerado (geralmente dentro de runs/detect/train/)
import shutil
import os
import glob

# Encontra o caminho do último treino
ultimo_treino = sorted(glob.glob('runs/detect/train*'))[-1]
modelo_best = os.path.join(ultimo_treino, 'weights/best.pt')

# Copia o best.pt para seu Google Drive
shutil.copy(modelo_best, destino)

print(f'Modelo salvo em: {destino}')