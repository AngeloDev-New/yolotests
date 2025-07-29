import pygame
import os
import yaml
import random
import shutil
import subprocess


if not os.path.isdir('dataset'):
    os.makedirs('dataset/images/test', exist_ok=True)
    os.makedirs('dataset/images/val', exist_ok=True)
    os.makedirs('dataset/images/train', exist_ok=True)
    os.makedirs('dataset/labels/test', exist_ok=True)
    os.makedirs('dataset/labels/val', exist_ok=True)
    os.makedirs('dataset/labels/train', exist_ok=True)
    # Seleciona a pasta com Zenity
    result = subprocess.run(
        ["zenity", "--file-selection", "--directory", "--title=Selecione uma pasta"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        origem = result.stdout.strip()  # remove \n
        destino = "dataset/images/test"

        # Garante que a pasta de destino existe
        os.makedirs(destino, exist_ok=True)

        # Copia todos os arquivos da pasta selecionada para o destino
        for arquivo in os.listdir(origem):
            caminho_origem = os.path.join(origem, arquivo)
            caminho_destino = os.path.join(destino, arquivo)
            if os.path.isfile(caminho_origem):
                shutil.copy(caminho_origem, caminho_destino)

        # Cria os arquivos de label com o mesmo nome base
        label_dir = "dataset/labels/test"
        os.makedirs(label_dir, exist_ok=True)

        labels = [os.path.splitext(image)[0] + '.txt' for image in os.listdir(destino)]

        for label in labels:
            caminho_label = os.path.join(label_dir, label)
            open(caminho_label, 'a').close()  # Cria o arquivo vazio se não existir













































division = {}

def att_data():
    global division
    division = {
        'test': len(os.listdir('dataset/images/test')),
        'val': len(os.listdir('dataset/images/val')),
        'train': len(os.listdir('dataset/images/train'))
    }
    division['total'] = division['test'] + division['val'] + division['train']
    
    if division['total'] > 0:
        division['percents'] = {
            'test_p': (division["test"] / division['total']) * 100,
            'val_p': (division["val"] / division['total']) * 100,
            'train_p': (division['train'] / division['total']) * 100
        }
    else:
        division['percents'] = {'test_p': 0, 'val_p': 0, 'train_p': 0}

def get_all_images():
    """Coleta todas as imagens de todas as pastas"""
    all_images = []
    image_path = 'dataset/images'
    
    for folder in ['train', 'val', 'test']:
        folder_path = os.path.join(image_path, folder)
        if os.path.exists(folder_path):
            for img in os.listdir(folder_path):
                all_images.append((img, folder))
    
    return all_images

def move_file_safe(img_name, origem, destino):
    """Move imagem e label de forma segura"""
    image_path = 'dataset/images'
    label_path = 'dataset/labels'
    
    # Move imagem
    img_origem = os.path.join(image_path, origem, img_name)
    img_destino = os.path.join(image_path, destino, img_name)
    
    if os.path.exists(img_origem):
        shutil.move(img_origem, img_destino)
    
    # Move label
    base, _ = os.path.splitext(img_name)
    lbl_origem = os.path.join(label_path, origem, base + '.txt')
    lbl_destino = os.path.join(label_path, destino, base + '.txt')
    
    if os.path.exists(lbl_origem):
        shutil.move(lbl_origem, lbl_destino)

def redistribute_dataset(train_ratio, val_ratio, test_ratio):
    """Redistribui todo o dataset baseado nas proporções desejadas"""
    
    # Normaliza as proporções
    total_ratio = train_ratio + val_ratio + test_ratio
    train_ratio = train_ratio / total_ratio
    val_ratio = val_ratio / total_ratio  
    test_ratio = test_ratio / total_ratio
    
    # Coleta todas as imagens
    all_images = get_all_images()
    total_images = len(all_images)
    
    if total_images == 0:
        print("Nenhuma imagem encontrada!")
        return
    
    # Calcula quantidades desejadas
    n_train = int(total_images * train_ratio)
    n_val = int(total_images * val_ratio)
    n_test = total_images - n_train - n_val  # Garante que soma 100%
    
    print(f"Redistribuindo {total_images} imagens:")
    print(f"Train: {n_train} ({train_ratio*100:.1f}%)")
    print(f"Val: {n_val} ({val_ratio*100:.1f}%)")
    print(f"Test: {n_test} ({test_ratio*100:.1f}%)")
    
    # Embaralha as imagens
    random.shuffle(all_images)
    
    # Primeiro, move tudo pra uma pasta temporária se necessário
    # ou trabalha diretamente com a lista embaralhada
    
    # Distribui as imagens
    for i, (img_name, current_folder) in enumerate(all_images):
        if i < n_train:
            target_folder = 'train'
        elif i < n_train + n_val:
            target_folder = 'val'
        else:
            target_folder = 'test'
        
        # Só move se não estiver na pasta certa
        if current_folder != target_folder:
            move_file_safe(img_name, current_folder, target_folder)
    
    print("Redistribuição concluída!")

def show_distribution():
    """Mostra a distribuição atual"""
    att_data()
    print("\nDistribuição atual:")
    for k in ['train', 'val', 'test']:
        print(f"{k}: {division[k]} imagens ({division['percents'][k+'_p']:.1f}%)")
    print(f"Total: {division['total']} imagens\n")

# ========== Execução ==========
print("=== Dataset Redistributor ===")
show_distribution()

while True:
    try:
        user_input = input('Distribuir de forma personalizada? (y/n): ').strip().lower()
        if user_input == 'y':
            ratios_input = input('Nova divisão (train,val,test) ex: 70,20,10 -> ')
        else:
            ratios_input = '7,2,1'
        train_ratio, val_ratio, test_ratio = [float(i.strip()) for i in ratios_input.split(',')]
        
        if train_ratio < 0 or val_ratio < 0 or test_ratio < 0:
            print("Valores não podem ser negativos!")
            continue
            
        if train_ratio + val_ratio + test_ratio == 0:
            print("Pelo menos um valor deve ser maior que zero!")
            continue
        
        redistribute_dataset(train_ratio, val_ratio, test_ratio)
        show_distribution()
        break
        
    except ValueError:
        print("Erro! Digite 3 números separados por vírgula (ex: 70,20,10)")
        continue
    except KeyboardInterrupt:
        print("\nSaindo...")
        break
    except Exception as e:
        print(f"Erro inesperado: {e}")
        continue

def salvar_yaml(classes):
    with open('dados.yaml', 'w') as f:
        f.write(f"""path: dataset
train: images/train
val: images/val
nc: {len(classes)}
names: {classes}
""")

if not os.path.isfile('dados.yaml'):
    print('dados.yaml criado')
    if True:
        classes = []

        print("Digite o nome de cada classe. Digite 'exit' para finalizar.")
        while True:
            classe = input(f'Classe {len(classes)}: ')
            if classe.lower() == 'exit':
                break
            if classe.strip():
                classes.append(classe.strip())

        if classes:
            salvar_yaml(classes)
            print("Arquivo dados.yaml criado com sucesso.")
        else:
            print("Nenhuma classe inserida. YAML não criado.")
else:
    # Carrega as classes existentes
    with open('dados.yaml', 'r') as f:
        dados = yaml.safe_load(f)

    classes = dados.get("names", [])
    print(f"Classes atuais: {classes}")

    print("\nO que deseja fazer?")
    print("1 - Adicionar nova classe")
    print("2 - Remover uma classe")
    print("3 - Reescrever todas as classes")
    print("4 - Manter como está")
    opcao = input("Escolha (1/2/3/4): ")

    if opcao == '1':
        nova = input("Digite o nome da nova classe: ").strip()
        if nova and nova not in classes:
            classes.append(nova)
            salvar_yaml(classes)
            print("Classe adicionada com sucesso.")
        else:
            print("Classe vazia ou já existe.")
    elif opcao == '2':
        print("Classes:")
        for i, c in enumerate(classes):
            print(f"{i}: {c}")
        idx = input("Digite o número da classe a remover: ")
        if idx.isdigit() and 0 <= int(idx) < len(classes):
            removida = classes.pop(int(idx))
            salvar_yaml(classes)
            print(f"Classe '{removida}' removida com sucesso.")
        else:
            print("Índice inválido.")
    elif opcao == '3':
        novas = []
        print("Digite o nome de cada classe nova. Digite 'exit' para finalizar.")
        while True:
            classe = input(f'Classe {len(novas)}: ')
            if classe.lower() == 'exit':
                break
            if classe.strip():
                novas.append(classe.strip())

        if novas:
            classes = novas
            salvar_yaml(classes)
            print("Classes reescritas com sucesso.")
        else:
            print("Nenhuma classe inserida. Nada foi alterado.")
    elif opcao == '4':
        print("Mantendo as classes existentes.")
    else:
        print("Opção inválida.")





# Configurações iniciais
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Anotador de Imagens")

# Cores e fonte
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT = pygame.font.SysFont(None, 24)

# Carrega classes do dados.yaml
with open('dados.yaml', 'r') as f:
    data_yaml = yaml.safe_load(f)
classes = data_yaml['names']
current_class_index = 0

# Caminhos das imagens
paths = ['dataset/images/train', 'dataset/images/val', 'dataset/images/test']
image_paths = [os.path.join(p, f) for p in paths for f in os.listdir(p) if f.endswith(('.jpg', '.png'))]
current_image_index = 0

boxes = []
drawing = False
start_pos = None

# Variáveis para controle de escala e posição da imagem
image_rect = None
scale_factor = 1.0
original_image_size = (0, 0)

def calculate_image_display(image):
    """Calcula como exibir a imagem mantendo a proporção"""
    global image_rect, scale_factor, original_image_size
    
    img_width, img_height = image.get_size()
    original_image_size = (img_width, img_height)
    
    # Calcula a escala para caber na tela mantendo proporção
    scale_x = SCREEN_WIDTH / img_width
    scale_y = SCREEN_HEIGHT / img_height
    scale_factor = min(scale_x, scale_y)
    
    # Calcula o novo tamanho
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    
    # Centraliza a imagem na tela
    x = (SCREEN_WIDTH - new_width) // 2
    y = (SCREEN_HEIGHT - new_height) // 2
    
    image_rect = pygame.Rect(x, y, new_width, new_height)
    
    return pygame.transform.scale(image, (new_width, new_height))

def screen_to_image_coords(screen_pos):
    """Converte coordenadas da tela para coordenadas da imagem original"""
    if not image_rect:
        return None
    
    # Verifica se o ponto está dentro da área da imagem
    if not image_rect.collidepoint(screen_pos):
        return None
    
    # Converte para coordenadas relativas à imagem
    rel_x = screen_pos[0] - image_rect.x
    rel_y = screen_pos[1] - image_rect.y
    
    # Converte para coordenadas da imagem original
    orig_x = rel_x / scale_factor
    orig_y = rel_y / scale_factor
    
    return (int(orig_x), int(orig_y))

def image_to_screen_coords(image_pos):
    """Converte coordenadas da imagem original para coordenadas da tela"""
    if not image_rect:
        return None
    
    screen_x = image_pos[0] * scale_factor + image_rect.x
    screen_y = image_pos[1] * scale_factor + image_rect.y
    
    return (int(screen_x), int(screen_y))

def image_rect_to_screen_rect(img_rect):
    """Converte um retângulo da imagem original para coordenadas da tela"""
    if not image_rect:
        return None
    
    screen_x = img_rect[0] * scale_factor + image_rect.x
    screen_y = img_rect[1] * scale_factor + image_rect.y
    screen_w = img_rect[2] * scale_factor
    screen_h = img_rect[3] * scale_factor
    
    return pygame.Rect(int(screen_x), int(screen_y), int(screen_w), int(screen_h))

def screen_rect_to_image_rect(screen_rect):
    """Converte um retângulo da tela para coordenadas da imagem original"""
    if not image_rect:
        return None
    
    # Ajusta as coordenadas para serem relativas à imagem
    rel_x = screen_rect.x - image_rect.x
    rel_y = screen_rect.y - image_rect.y
    
    # Converte para coordenadas da imagem original
    img_x = rel_x / scale_factor
    img_y = rel_y / scale_factor
    img_w = screen_rect.width / scale_factor
    img_h = screen_rect.height / scale_factor
    
    return (int(img_x), int(img_y), int(img_w), int(img_h))

def draw_boxes():
    for box in boxes:
        # Converte o retângulo da imagem para coordenadas da tela
        screen_rect = image_rect_to_screen_rect(box['image_rect'])
        if screen_rect:
            pygame.draw.rect(screen, RED, screen_rect, 2)
            label = FONT.render(classes[box['class_id']], True, RED)
            screen.blit(label, (screen_rect.x, screen_rect.y - 20))

def convert_to_yolo(img_rect, img_width, img_height):
    """Converte retângulo da imagem para formato YOLO"""
    x_center = (img_rect[0] + img_rect[2] / 2) / img_width
    y_center = (img_rect[1] + img_rect[3] / 2) / img_height
    width = img_rect[2] / img_width
    height = img_rect[3] / img_height
    return x_center, y_center, width, height

def yolo_to_image_rect(yolo_coords, img_width, img_height):
    """Converte coordenadas YOLO para retângulo da imagem"""
    x_center, y_center, width, height = yolo_coords
    
    w = width * img_width
    h = height * img_height
    x = x_center * img_width - w / 2
    y = y_center * img_height - h / 2
    
    return (int(x), int(y), int(w), int(h))

def save_labels(img_path):
    label_path = img_path.replace('images', 'labels').rsplit('.', 1)[0] + '.txt'
    os.makedirs(os.path.dirname(label_path), exist_ok=True)
    with open(label_path, 'w') as f:
        for box in boxes:
            x, y, w, h = convert_to_yolo(box['image_rect'], original_image_size[0], original_image_size[1])
            f.write(f"{box['class_id']} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

def load_labels(img_path):
    boxes.clear()
    label_path = img_path.replace('images', 'labels').rsplit('.', 1)[0] + '.txt'
    if not os.path.exists(label_path):
        return
    with open(label_path, 'r') as f:
        for line in f:
            class_id, x, y, w, h = map(float, line.split())
            img_rect = yolo_to_image_rect((x, y, w, h), original_image_size[0], original_image_size[1])
            boxes.append({'image_rect': img_rect, 'class_id': int(class_id)})

def remove_box(screen_pos):
    for i, box in enumerate(boxes):
        screen_rect = image_rect_to_screen_rect(box['image_rect'])
        if screen_rect and screen_rect.collidepoint(screen_pos):
            boxes.pop(i)
            return

def load_new_image(index):
    """Carrega uma nova imagem e ajusta a exibição"""
    global current_image, scaled_image
    current_image = pygame.image.load(image_paths[index])
    scaled_image = calculate_image_display(current_image)
    load_labels(image_paths[index])

def main():
    global current_image_index, drawing, start_pos, current_class_index, current_image, scaled_image

    clock = pygame.time.Clock()
    running = True
    
    # Carrega a primeira imagem
    load_new_image(current_image_index)

    while running:
        screen.fill(BLACK)
        
        # Desenha a imagem centralizada
        if scaled_image and image_rect:
            screen.blit(scaled_image, image_rect)
        
        draw_boxes()

        if drawing and start_pos:
            mouse_pos = pygame.mouse.get_pos()
            # Só desenha se ambas as posições estão dentro da área da imagem
            if (image_rect.collidepoint(start_pos) and image_rect.collidepoint(mouse_pos)):
                rect = pygame.Rect(*start_pos, mouse_pos[0] - start_pos[0], mouse_pos[1] - start_pos[1])
                rect.normalize()
                pygame.draw.rect(screen, RED, rect, 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    save_labels(image_paths[current_image_index])
                    current_image_index = (current_image_index + 1) % len(image_paths)
                    load_new_image(current_image_index)
                elif event.key == pygame.K_LEFT:
                    save_labels(image_paths[current_image_index])
                    current_image_index = (current_image_index - 1) % len(image_paths)
                    load_new_image(current_image_index)
                elif event.key == pygame.K_SPACE:
                    current_class_index = (current_class_index + 1) % len(classes)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Esquerdo
                    # Só permite desenhar se o clique for dentro da área da imagem
                    if image_rect and image_rect.collidepoint(event.pos):
                        drawing = True
                        start_pos = event.pos
                elif event.button == 3:  # Direito
                    remove_box(event.pos)
                    save_labels(image_paths[current_image_index])
                elif event.button == 2:  # Meio
                    current_class_index = (current_class_index + 1) % len(classes)

            elif event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    save_labels(image_paths[current_image_index])
                    current_image_index = (current_image_index + 1) % len(image_paths)
                    load_new_image(current_image_index)
                elif event.y > 0:
                    save_labels(image_paths[current_image_index])
                    current_image_index = (current_image_index - 1) % len(image_paths)
                    load_new_image(current_image_index)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = event.pos
                    # Verifica se ambas as posições estão dentro da área da imagem
                    if (image_rect and image_rect.collidepoint(start_pos) and 
                        image_rect.collidepoint(end_pos)):
                        
                        rect = pygame.Rect(*start_pos, end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
                        rect.normalize()
                        
                        if rect.width > 5 and rect.height > 5:
                            # Converte o retângulo da tela para coordenadas da imagem
                            img_rect = screen_rect_to_image_rect(rect)
                            if img_rect:
                                boxes.append({'image_rect': img_rect, 'class_id': current_class_index})
                                save_labels(image_paths[current_image_index])
                    
                    drawing = False
                    start_pos = None

        # Mostrar informações
        class_name = classes[current_class_index]
        image_name = os.path.basename(image_paths[current_image_index])
        image_info = f"({current_image_index + 1}/{len(image_paths)})"
        scale_info = f"Escala: {scale_factor:.2f}"
        
        # Informações na parte superior
        info_text = f"Imagem: {image_name} {image_info} | Classe: {class_name} (Espaço para trocar) | {scale_info}"
        label = FONT.render(info_text, True, WHITE)
        screen.blit(label, (10, 10))
        
        # Instruções na parte inferior
        instructions = [
            "Controles: ←→ ou scroll = navegar | Espaço/botão meio = trocar classe",
            "Mouse: esquerdo = desenhar caixa | direito = remover caixa"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_label = FONT.render(instruction, True, WHITE)
            screen.blit(inst_label, (10, SCREEN_HEIGHT - 50 + i * 25))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()