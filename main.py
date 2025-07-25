from ultralytics import YOLO
import cv2

# Carrega seu modelo customizado
model = YOLO('melhor_modelo.pt')  # substitua pelo caminho real

# Abre webcam (0 = padrão)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Faz a predição no frame atual
    results = model.predict(source=frame, conf=0.6, verbose=False)

    # Inicializa contadores
    contagem = {'milho': 0, 'daninha': 0}

    # Pega as detecções do primeiro resultado
    boxes = results[0].boxes
    nomes = model.names  # nomes das classes (ex: {0: 'milho', 1: 'daninha'})

    for box in boxes:
        cls = int(box.cls[0])  # classe detectada
        conf = float(box.conf[0])  # confiança

        nome_classe = nomes[cls]
        if nome_classe in contagem:
            contagem[nome_classe] += 1

        # Desenha a caixa e a label
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = xyxy
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        texto = f'{nome_classe} {conf:.2f}'
        cv2.putText(frame, texto, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # Mostra contagens na tela
    cv2.putText(frame, f"Milho: {contagem['milho']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, f"Daninha: {contagem['daninha']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    # Exibe o resultado
    cv2.imshow("Detecção", frame)

    # Sai se apertar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera recursos
cap.release()
cv2.destroyAllWindows()
