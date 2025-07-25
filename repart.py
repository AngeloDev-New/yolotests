import os
import shutil

# Configuração dos caminhos
path_images = 'dataset/images/data'
path_train = 'dataset/images/train'
path_val = 'dataset/images/val'
path_test = 'dataset/images/test'

label_train = 'dataset/labels/train'
label_val = 'dataset/labels/val'
label_test = 'dataset/labels/test'

# Lista de imagens
images = sorted(os.listdir(path_images))  # ordenado para garantir consistência
total = len(images)

# Contador e divisões
for i, image in enumerate(images):
    label_name = image.replace('.png', '.txt')
    img_src = os.path.join(path_images, image)

    if i < 921:
        # Treinamento
        img_dst = os.path.join(path_train, image)
        label_dst = os.path.join(label_train, label_name)
    elif i < 921 + 263:
        # Validação
        img_dst = os.path.join(path_val, image)
        label_dst = os.path.join(label_val, label_name)
    else:
        # Teste
        img_dst = os.path.join(path_test, image)
        label_dst = os.path.join(label_test, label_name)

    # Move imagem
    shutil.move(img_src, img_dst)

    # Cria arquivo de texto vazio correspondente
    open(label_dst, 'w').close()

print("✅ Divisão completa: imagens e rótulos organizados!")
