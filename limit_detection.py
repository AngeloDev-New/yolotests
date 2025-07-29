from ultralytics import YOLO

# Carrega o modelo pré-treinado no COCO (80 classes)
model = YOLO("yolov8n.pt")

# Faz a inferência
results = model("imagem.jpg")[0]

# Filtra somente deteções da classe "person" (classe 0 no COCO)
for box in results.boxes:
    if int(box.cls[0]) == 0:  # 0 é a classe "person" no COCO
        print("Pessoa detectada:", box.xyxy[0])

coco_dict_pt = {
    "pessoa": 0, "bicicleta": 1, "carro": 2, "moto": 3, "avião": 4, "ônibus": 5, "trem": 6, "caminhão": 7, "barco": 8,
    "semáforo": 9, "hidrante": 10, "placa de pare": 11, "parquímetro": 12, "banco": 13, "pássaro": 14, "gato": 15,
    "cachorro": 16, "cavalo": 17, "ovelha": 18, "vaca": 19, "elefante": 20, "urso": 21, "zebra": 22, "girafa": 23,
    "mochila": 24, "guarda-chuva": 25, "bolsa": 26, "gravata": 27, "mala": 28, "frisbee": 29, "esquis": 30,
    "snowboard": 31, "bola esportiva": 32, "pipa": 33, "taco de beisebol": 34, "luva de beisebol": 35, "skate": 36,
    "prancha de surf": 37, "raquete de tênis": 38, "garrafa": 39, "taça de vinho": 40, "copo": 41, "garfo": 42,
    "faca": 43, "colher": 44, "tigela": 45, "banana": 46, "maçã": 47, "sanduíche": 48, "laranja": 49, "brócolis": 50,
    "cenoura": 51, "cachorro-quente": 52, "pizza": 53, "rosquinha": 54, "bolo": 55, "cadeira": 56, "sofá": 57,
    "vaso de planta": 58, "cama": 59, "mesa de jantar": 60, "vaso sanitário": 61, "televisão": 62, "laptop": 63,
    "mouse": 64, "controle remoto": 65, "teclado": 66, "celular": 67, "micro-ondas": 68, "forno": 69, "torradeira": 70,
    "pia": 71, "geladeira": 72, "livro": 73, "relógio": 74, "vaso decorativo": 75, "tesoura": 76, "ursinho de pelúcia": 77,
    "secador de cabelo": 78, "escova de dentes": 79
}
