import os
import random
from ultralytics import YOLO
import cv2
from matplotlib import pyplot as plt




# Escolhe uma imagem aleatória
img_nome = 'map.png'
img_path = 'assets/map.png'
print(f'Imagem escolhida: {img_path}')

# Carrega o modelo customizado
model = YOLO('v8s.pt') 
# Faz a predição
results = model(img_path)

# Mostra a imagem com as detecções desenhadas
result_img = results[0].plot()  # gera a imagem com bbox e labels

# Exibe com matplotlib
plt.figure(figsize=(10,10))
plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()
