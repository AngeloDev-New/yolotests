import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import numpy as np

# Configurar estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Carregar dados
df = pd.read_csv('yolo_training_results.csv')

# Criar figura com 4 subplots
fig = plt.figure(figsize=(20, 16))

# Cores para cada modelo/augmentation
colors = {
    'YOLOv8n_No': '#1f77b4',
    'YOLOv8n_Yes': '#ff7f0e', 
    'YOLOv8s_No': '#2ca02c',
    'YOLOv8s_Yes': '#d62728'
}

# Criar combinação de Model + Augmentation para legendas
df['Model_Aug'] = df['Model'] + '_' + df['Augmentation'].map({'No': 'No', 'Yes': 'Yes'})

# 1. Gráfico de Loss (box_loss, cls_loss, dfl_loss)
plt.subplot(2, 2, 1)
for model_aug in df['Model_Aug'].unique():
    data = df[df['Model_Aug'] == model_aug]
    plt.plot(data['Epoch'], data['box_loss'], '--', alpha=0.7, color=colors[model_aug], linewidth=1)
    plt.plot(data['Epoch'], data['cls_loss'], ':', alpha=0.7, color=colors[model_aug], linewidth=1)
    plt.plot(data['Epoch'], data['dfl_loss'], '-', color=colors[model_aug], linewidth=2)

plt.ylabel('Loss Value', fontsize=12)
plt.title('Training Losses Evolution', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

# Apenas legenda dos tipos de linha no canto superior direito
legend_elements = [
    plt.Line2D([0], [0], color='gray', linestyle='-', label='DFL Loss'),
    plt.Line2D([0], [0], color='gray', linestyle='--', label='Box Loss'), 
    plt.Line2D([0], [0], color='gray', linestyle=':', label='Cls Loss')
]
plt.legend(handles=legend_elements, loc='upper right', fontsize=9)

# 2. Gráfico de mAP (mAP50 e mAP50-95)
plt.subplot(2, 2, 2)
for model_aug in df['Model_Aug'].unique():
    data = df[df['Model_Aug'] == model_aug]
    plt.plot(data['Epoch'], data['mAP50'], '-', color=colors[model_aug], linewidth=2.5)
    plt.plot(data['Epoch'], data['mAP50-95'], '--', color=colors[model_aug], linewidth=2, alpha=0.7)

plt.ylabel('mAP Score', fontsize=12)
plt.title('Mean Average Precision Evolution', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

# Apenas legenda dos tipos de linha no canto inferior direito
legend_elements = [
    plt.Line2D([0], [0], color='gray', linestyle='-', label='mAP@0.5'),
    plt.Line2D([0], [0], color='gray', linestyle='--', label='mAP@0.5:0.95')
]
plt.legend(handles=legend_elements, loc='lower right', fontsize=9)

# 3. Gráfico de Precision e Recall
plt.subplot(2, 2, 3)
for model_aug in df['Model_Aug'].unique():
    data = df[df['Model_Aug'] == model_aug]
    plt.plot(data['Epoch'], data['Precision'], '-', color=colors[model_aug], linewidth=2.5)
    plt.plot(data['Epoch'], data['Recall'], '--', color=colors[model_aug], linewidth=2, alpha=0.7)

plt.ylabel('Score', fontsize=12)
plt.title('Precision and Recall Evolution', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)

# Apenas legenda dos tipos de linha no canto inferior direito
legend_elements = [
    plt.Line2D([0], [0], color='gray', linestyle='-', label='Precision'),
    plt.Line2D([0], [0], color='gray', linestyle='--', label='Recall')
]
plt.legend(handles=legend_elements, loc='lower right', fontsize=9)

# 4. Gráfico de GPU Memory Usage
plt.subplot(2, 2, 4)
for model_aug in df['Model_Aug'].unique():
    data = df[df['Model_Aug'] == model_aug]
    plt.plot(data['Epoch'], data['GPU_mem'], '-o', color=colors[model_aug], linewidth=2.5,
             markersize=4, label=f'{model_aug.replace("_", " + " if "Yes" in model_aug else " sem ")}Augmentation')

plt.ylabel('GPU Memory (GB)', fontsize=12)
plt.title('GPU Memory Usage Evolution', fontsize=14, fontweight='bold')
plt.legend(fontsize=10, loc='lower right')
plt.grid(True, alpha=0.3)

# Ajustar layout
plt.tight_layout(pad=3.0)

# Salvar gráfico
plt.savefig('yolo_training_comparison.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.show()

# Criar tabela de resultados finais (Epoch 100)
print("\n" + "="*80)
print("RESULTADOS FINAIS (EPOCH 100)")
print("="*80)

final_results = df[df['Epoch'] == 100].copy()
final_results = final_results.sort_values(['Model', 'Augmentation'])

print(f"{'Model':<8} {'Aug':<5} {'mAP50':<8} {'mAP50-95':<10} {'Precision':<10} {'Recall':<8} {'GPU_mem':<8}")
print("-" * 80)

for _, row in final_results.iterrows():
    aug_str = "Sim" if row['Augmentation'] == 'Yes' else "Não"
    print(f"{row['Model']:<8} {aug_str:<5} {row['mAP50']:<8.3f} {row['mAP50-95']:<10.3f} "
          f"{row['Precision']:<10.3f} {row['Recall']:<8.3f} {row['GPU_mem']:<8.1f}G")

# Análise comparativa
print("\n" + "="*80)
print("ANÁLISE COMPARATIVA")
print("="*80)

print("\n1. EFEITO DA AUGMENTATION:")
for model in ['YOLOv8n', 'YOLOv8s']:
    no_aug = final_results[(final_results['Model'] == model) & (final_results['Augmentation'] == 'No')]
    with_aug = final_results[(final_results['Model'] == model) & (final_results['Augmentation'] == 'Yes')]
    
    if not no_aug.empty and not with_aug.empty:
        map50_diff = with_aug['mAP50'].iloc[0] - no_aug['mAP50'].iloc[0]
        map50_95_diff = with_aug['mAP50-95'].iloc[0] - no_aug['mAP50-95'].iloc[0]
        
        print(f"  {model}:")
        print(f"    mAP50: {map50_diff:+.3f} ({'melhora' if map50_diff > 0 else 'piora'})")
        print(f"    mAP50-95: {map50_95_diff:+.3f} ({'melhora' if map50_95_diff > 0 else 'piora'})")

print("\n2. COMPARAÇÃO ENTRE MODELOS (com augmentation):")
v8n_aug = final_results[(final_results['Model'] == 'YOLOv8n') & (final_results['Augmentation'] == 'Yes')]
v8s_aug = final_results[(final_results['Model'] == 'YOLOv8s') & (final_results['Augmentation'] == 'Yes')]

if not v8n_aug.empty and not v8s_aug.empty:
    map50_diff = v8s_aug['mAP50'].iloc[0] - v8n_aug['mAP50'].iloc[0]
    map50_95_diff = v8s_aug['mAP50-95'].iloc[0] - v8n_aug['mAP50-95'].iloc[0]
    gpu_diff = v8s_aug['GPU_mem'].iloc[0] - v8n_aug['GPU_mem'].iloc[0]
    
    print(f"  YOLOv8s vs YOLOv8n:")
    print(f"    mAP50: {map50_diff:+.3f}")
    print(f"    mAP50-95: {map50_95_diff:+.3f}")
    print(f"    GPU Memory: {gpu_diff:+.1f}G")

print("\n3. MELHOR CONFIGURAÇÃO:")
best_map50 = final_results.loc[final_results['mAP50'].idxmax()]
best_map50_95 = final_results.loc[final_results['mAP50-95'].idxmax()]
best_efficiency = final_results.loc[(final_results['mAP50'] / final_results['GPU_mem']).idxmax()]

print(f"  Melhor mAP50: {best_map50['Model']} {'com' if best_map50['Augmentation'] == 'Yes' else 'sem'} augmentation ({best_map50['mAP50']:.3f})")
print(f"  Melhor mAP50-95: {best_map50_95['Model']} {'com' if best_map50_95['Augmentation'] == 'Yes' else 'sem'} augmentation ({best_map50_95['mAP50-95']:.3f})")
print(f"  Melhor eficiência: {best_efficiency['Model']} {'com' if best_efficiency['Augmentation'] == 'Yes' else 'sem'} augmentation (mAP50/GPU: {best_efficiency['mAP50']/best_efficiency['GPU_mem']:.3f})")