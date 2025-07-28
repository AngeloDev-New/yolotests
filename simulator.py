import pygame
import threading
import queue
from ultralytics import YOLO
import cv2
import numpy as np
import time

# Inicialização
pygame.init()
TELA_LARG, TELA_ALTURA = 1200, 700
tela = pygame.display.set_mode((TELA_LARG, TELA_ALTURA))
clock = pygame.time.Clock()

# Carregamento de imagens
mapa_img = pygame.image.load("assets/map.png").convert()
drone_img = pygame.image.load("assets/drone.png").convert_alpha()
drone_img = pygame.transform.scale(drone_img, (50, 50))  # Drone maior

# Modelo YOLO
model = YOLO('v8s.pt')

# Posição inicial do drone no mundo
drone_world_x, drone_world_y = 400, 300
velocidade = 5

# Posição da câmera (offset do mundo)
camera_x, camera_y = 0, 0

# Tamanho da captura (600x600 como você treinou)
camera_larg, camera_alt = 600, 600

# Tamanho da mini visão lateral (menor para caber na tela)
mini_larg, mini_alt = 200, 200

# Cores para as classes
cores_classes = [(255, 215, 0), (255, 0, 0)]  # Classe 0: Milho (dourado), Classe 1: Daninha (vermelho)
nomes_classes = ["Milho", "Daninha"]

# Queue para comunicação entre threads
detection_queue = queue.Queue(maxsize=2)
frame_queue = queue.Queue(maxsize=2)

# Variáveis globais para detecções
current_detections = []
detection_lock = threading.Lock()

def yolo_worker():
    """Thread worker para processamento YOLO"""
    while True:
        try:
            # Pega frame da queue (timeout para não travar)
            frame_data = frame_queue.get(timeout=0.1)
            if frame_data is None:  # Sinal para parar
                break
            
            fragmento_cv, timestamp = frame_data
            
            # Processa detecção
            resultados = model.predict(fragmento_cv, verbose=False)[0]
            detections = []
            
            for caixa in resultados.boxes:
                x1, y1, x2, y2 = map(int, caixa.xyxy[0].tolist())
                classe = int(caixa.cls[0])
                confianca = float(caixa.conf[0])
                
                # Escala as coordenadas da detecção para o tamanho da mini visão
                scale_x = mini_larg / camera_larg
                scale_y = mini_alt / camera_alt
                
                x1_scaled = int(x1 * scale_x)
                y1_scaled = int(y1 * scale_y)
                w_scaled = int((x2 - x1) * scale_x)
                h_scaled = int((y2 - y1) * scale_y)
                
                detections.append((x1_scaled, y1_scaled, w_scaled, h_scaled, classe, confianca))
            
            # Atualiza detecções globais de forma thread-safe
            with detection_lock:
                global current_detections
                current_detections = detections
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Erro no YOLO worker: {e}")
            continue

def detectar_async(fragmento_cv):
    """Envia frame para processamento assíncrono"""
    try:
        # Remove frame antigo se a queue estiver cheia
        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass
        
        # Adiciona novo frame
        frame_queue.put((fragmento_cv.copy(), time.time()), block=False)
    except queue.Full:
        pass  # Ignora se não conseguir adicionar

def desenhar_legenda():
    """Desenha a legenda das classes"""
    fontes = pygame.font.SysFont(None, 24)
    
    # Fundo da legenda
    pygame.draw.rect(tela, (40, 40, 40), (1020, 420, 160, 80))
    pygame.draw.rect(tela, (200, 200, 200), (1020, 420, 160, 80), 2)
    
    # Título
    txt_titulo = fontes.render("Classes:", True, (255, 255, 255))
    tela.blit(txt_titulo, (1030, 430))
    
    # Classes específicas
    for i, (cor, nome) in enumerate(zip(cores_classes, nomes_classes)):
        pygame.draw.rect(tela, cor, (1030, 450 + i * 25, 20, 20))
        txt = fontes.render(nome, True, (255, 255, 255))
        tela.blit(txt, (1060, 450 + i * 25))

def desenhar_mini_visao_com_moldura(fragmento, pos_x, pos_y):
    """Desenha a mini visão com moldura destacada (QUADRADA)"""
    # Cria surface para a mini visão
    mini_visao = pygame.Surface((mini_larg, mini_alt), pygame.SRCALPHA)
    
    # Redimensiona o fragmento para o tamanho da mini visão
    fragmento_scaled = pygame.transform.scale(fragmento, (mini_larg, mini_alt))
    mini_visao.blit(fragmento_scaled, (0, 0))
    
    # Desenha detecções (thread-safe)
    with detection_lock:
        for x, y, w, h, classe, conf in current_detections:
            if classe < len(cores_classes):
                cor = cores_classes[classe]
                pygame.draw.rect(mini_visao, cor, (x, y, w, h), 2)
                
                # Desenha confiança
                font_small = pygame.font.SysFont(None, 16)
                conf_text = font_small.render(f"{conf:.2f}", True, cor)
                mini_visao.blit(conf_text, (x, max(0, y - 15)))
    
    # REMOVIDA A MÁSCARA CIRCULAR - agora é quadrado!
    
    # Desenha fundo da moldura (mais escuro)
    pygame.draw.rect(tela, (20, 20, 20), (pos_x - 10, pos_y - 10, mini_larg + 20, mini_alt + 20))
    
    # Moldura externa (destacada)
    pygame.draw.rect(tela, (100, 200, 255), (pos_x - 8, pos_y - 8, mini_larg + 16, mini_alt + 16), 4)
    
    # Moldura interna
    pygame.draw.rect(tela, (255, 255, 255), (pos_x - 2, pos_y - 2, mini_larg + 4, mini_alt + 4), 2)
    
    # Blit da visão quadrada
    tela.blit(mini_visao, (pos_x, pos_y))
    
    # Título da mini visão
    font_titulo = pygame.font.SysFont(None, 20)
    titulo = font_titulo.render("Visão do Drone", True, (255, 255, 255))
    tela.blit(titulo, (pos_x, pos_y - 30))

# Inicia thread do YOLO
yolo_thread = threading.Thread(target=yolo_worker, daemon=True)
yolo_thread.start()

# Loop principal
running = True
last_detection_time = 0
detection_interval = 0.1  # Processa detecção a cada 100ms

try:
    while running:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

        # Movimentação do drone no mundo
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            drone_world_x -= velocidade
        if keys[pygame.K_RIGHT]:
            drone_world_x += velocidade  
        if keys[pygame.K_UP]:
            drone_world_y -= velocidade
        if keys[pygame.K_DOWN]:
            drone_world_y += velocidade

        # Limita o drone às bordas do mapa
        drone_world_x = max(0, min(mapa_img.get_width(), drone_world_x))
        drone_world_y = max(0, min(mapa_img.get_height(), drone_world_y))

        # Atualiza a câmera para seguir o drone
        # Centraliza o drone na tela, mas limita pelas bordas do mapa
        camera_x = drone_world_x - TELA_LARG // 2
        camera_y = drone_world_y - TELA_ALTURA // 2
        
        # Limita a câmera para não mostrar além das bordas do mapa
        camera_x = max(0, min(mapa_img.get_width() - TELA_LARG, camera_x))
        camera_y = max(0, min(mapa_img.get_height() - TELA_ALTURA, camera_y))
        
        # Posição do drone na tela (relativa à câmera)
        drone_screen_x = drone_world_x - camera_x
        drone_screen_y = drone_world_y - camera_y

        # Recorte da visão da câmera (600x600) - baseado na posição mundial
        camera_rect = pygame.Rect(
            drone_world_x - camera_larg // 2, 
            drone_world_y - camera_alt // 2, 
            camera_larg, 
            camera_alt
        )
        
        # Garante que o recorte não saia das bordas do mapa
        camera_rect.clamp_ip(pygame.Rect(0, 0, mapa_img.get_width(), mapa_img.get_height()))
        
        fragmento = mapa_img.subsurface(camera_rect).copy()

        # Processa detecção apenas a intervalos regulares
        current_time = time.time()
        if current_time - last_detection_time > detection_interval:
            # Converte para o formato OpenCV
            fragmento_cv = pygame.surfarray.array3d(fragmento)
            fragmento_cv = cv2.cvtColor(np.rot90(fragmento_cv), cv2.COLOR_RGB2BGR)
            
            # Envia para processamento assíncrono
            detectar_async(fragmento_cv)
            last_detection_time = current_time

        # Desenha mapa completo (com offset da câmera)
        tela.fill((30, 30, 30))  # Fundo escuro
        
        # Recorta a parte visível do mapa baseada na posição da câmera
        visible_rect = pygame.Rect(camera_x, camera_y, TELA_LARG, TELA_ALTURA)
        visible_rect.clamp_ip(pygame.Rect(0, 0, mapa_img.get_width(), mapa_img.get_height()))
        
        # Desenha apenas a parte visível do mapa
        if visible_rect.width > 0 and visible_rect.height > 0:
            visible_map = mapa_img.subsurface(visible_rect)
            tela.blit(visible_map, (visible_rect.x - camera_x, visible_rect.y - camera_y))

        # Quadrado da visão do drone (600x600) - posição relativa à tela
        vision_rect_screen = pygame.Rect(
            drone_screen_x - camera_larg // 2,
            drone_screen_y - camera_alt // 2,
            camera_larg,
            camera_alt
        )
        pygame.draw.rect(tela, (0, 255, 255), vision_rect_screen, 3)

        # Desenha drone (posição relativa à tela)
        tela.blit(drone_img, (drone_screen_x - 25, drone_screen_y - 25))

        # Desenha mini visão com moldura
        desenhar_mini_visao_com_moldura(fragmento, 1020, 50)

        # Legenda
        desenhar_legenda()
        
        # Info de performance e posição
        font_info = pygame.font.SysFont(None, 18)
        fps_text = font_info.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        
        # Conta detecções por classe
        milho_count = sum(1 for _, _, _, _, classe, _ in current_detections if classe == 0)
        daninha_count = sum(1 for _, _, _, _, classe, _ in current_detections if classe == 1)
        
        detec_text = font_info.render(f"🌽 Milho: {milho_count} | 🌿 Daninha: {daninha_count}", True, (255, 255, 255))
        pos_text = font_info.render(f"Drone: ({drone_world_x}, {drone_world_y})", True, (255, 255, 255))
        camera_text = font_info.render(f"Câmera: ({int(camera_x)}, {int(camera_y)})", True, (255, 255, 255))
        
        tela.blit(fps_text, (10, 10))
        tela.blit(detec_text, (10, 30))
        tela.blit(pos_text, (10, 50))
        tela.blit(camera_text, (10, 70))

        pygame.display.flip()
        clock.tick(60)

finally:
    # Sinaliza para parar a thread
    frame_queue.put(None)
    yolo_thread.join(timeout=1)
    pygame.quit()