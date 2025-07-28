import os
import random
from ultralytics import YOLO
import cv2
from matplotlib import pyplot as plt

# Caminho para a pasta de teste
test_folder = 'dataset/images/test'

# Lista todas as imagens na pasta test
imagens_test = [f for f in os.listdir(test_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Escolhe uma imagem aleatória
img_nome = random.choice(imagens_test)
img_path = os.path.join(test_folder, img_nome)
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
