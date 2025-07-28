import os
import random
import shutil

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
        user_input = input('Exit? (y/n): ').strip().lower()
        if user_input == 'y':
            break
        
        ratios_input = input('Nova divisão (train,val,test) ex: 70,20,10 -> ')
        train_ratio, val_ratio, test_ratio = [float(i.strip()) for i in ratios_input.split(',')]
        
        if train_ratio < 0 or val_ratio < 0 or test_ratio < 0:
            print("Valores não podem ser negativos!")
            continue
            
        if train_ratio + val_ratio + test_ratio == 0:
            print("Pelo menos um valor deve ser maior que zero!")
            continue
        
        redistribute_dataset(train_ratio, val_ratio, test_ratio)
        show_distribution()
        
    except ValueError:
        print("Erro! Digite 3 números separados por vírgula (ex: 70,20,10)")
        continue
    except KeyboardInterrupt:
        print("\nSaindo...")
        break
    except Exception as e:
        print(f"Erro inesperado: {e}")
        continue