import pygame
import os
import yaml

# Configurações iniciais
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Anotador de Imagens")

# Cores e fonte
WHITE = (255, 255, 255)
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

def draw_boxes():
    for box in boxes:
        pygame.draw.rect(screen, RED, box['rect'], 2)
        label = FONT.render(classes[box['class_id']], True, RED)
        screen.blit(label, (box['rect'].x, box['rect'].y - 20))

def convert_to_yolo(rect, img_width, img_height):
    x_center = (rect.x + rect.width / 2) / img_width
    y_center = (rect.y + rect.height / 2) / img_height
    width = rect.width / img_width
    height = rect.height / img_height
    return x_center, y_center, width, height

def save_labels(img_path):
    label_path = img_path.replace('images', 'labels').rsplit('.', 1)[0] + '.txt'
    os.makedirs(os.path.dirname(label_path), exist_ok=True)
    with open(label_path, 'w') as f:
        for box in boxes:
            x, y, w, h = convert_to_yolo(box['rect'], SCREEN_WIDTH, SCREEN_HEIGHT)
            f.write(f"{box['class_id']} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

def load_labels(img_path):
    boxes.clear()
    label_path = img_path.replace('images', 'labels').rsplit('.', 1)[0] + '.txt'
    if not os.path.exists(label_path):
        return
    with open(label_path, 'r') as f:
        for line in f:
            class_id, x, y, w, h = map(float, line.split())
            x *= SCREEN_WIDTH
            y *= SCREEN_HEIGHT
            w *= SCREEN_WIDTH
            h *= SCREEN_HEIGHT
            rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
            boxes.append({'rect': rect, 'class_id': int(class_id)})

def remove_box(pos):
    for i, box in enumerate(boxes):
        if box['rect'].collidepoint(pos):
            boxes.pop(i)
            return

def main():
    global current_image_index, drawing, start_pos, current_class_index

    clock = pygame.time.Clock()
    running = True
    current_image = pygame.image.load(image_paths[current_image_index])
    current_image = pygame.transform.scale(current_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    load_labels(image_paths[current_image_index])

    while running:
        screen.fill(WHITE)
        screen.blit(current_image, (0, 0))
        draw_boxes()

        if drawing and start_pos:
            mouse_pos = pygame.mouse.get_pos()
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
                    current_image = pygame.image.load(image_paths[current_image_index])
                    current_image = pygame.transform.scale(current_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    load_labels(image_paths[current_image_index])
                elif event.key == pygame.K_LEFT:
                    save_labels(image_paths[current_image_index])
                    current_image_index = (current_image_index - 1) % len(image_paths)
                    current_image = pygame.image.load(image_paths[current_image_index])
                    current_image = pygame.transform.scale(current_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    load_labels(image_paths[current_image_index])
                elif event.key == pygame.K_SPACE:
                    current_class_index = (current_class_index + 1) % len(classes)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Esquerdo
                    drawing = True
                    start_pos = event.pos
                elif event.button == 3:  # Direito
                    remove_box(event.pos)
                    save_labels(image_paths[current_image_index])

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    end_pos = event.pos
                    rect = pygame.Rect(*start_pos, end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
                    rect.normalize()
                    if rect.width > 5 and rect.height > 5:
                        boxes.append({'rect': rect, 'class_id': current_class_index})
                        save_labels(image_paths[current_image_index])
                    drawing = False
                    start_pos = None

        # Mostrar classe atual
        class_name = classes[current_class_index]
        image_name = os.path.basename(image_paths[current_image_index])
        label = FONT.render(f"Image:{image_name},Classe: {class_name} (Espaço para trocar)", True, (0, 0, 0))
        screen.blit(label, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

main()
