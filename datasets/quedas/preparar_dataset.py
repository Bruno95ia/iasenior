"""
Prepara dataset YOLO para treinamento.
Divide em train/val/test e cria arquivo de configuração.
"""

import shutil
import random
from pathlib import Path
from collections import defaultdict

ANNOTATIONS_DIR = Path(__file__).parent / "annotations"
IMAGES_DIR = ANNOTATIONS_DIR / "images"
LABELS_DIR = ANNOTATIONS_DIR / "labels"

DATASET_DIR = Path(__file__).parent / "dataset_yolo"
TRAIN_IMAGES = DATASET_DIR / "train" / "images"
TRAIN_LABELS = DATASET_DIR / "train" / "labels"
VAL_IMAGES = DATASET_DIR / "val" / "images"
VAL_LABELS = DATASET_DIR / "val" / "labels"
TEST_IMAGES = DATASET_DIR / "test" / "images"
TEST_LABELS = DATASET_DIR / "test" / "labels"

# Criar diretórios
for d in [TRAIN_IMAGES, TRAIN_LABELS, VAL_IMAGES, VAL_LABELS, TEST_IMAGES, TEST_LABELS]:
    d.mkdir(parents=True, exist_ok=True)

def preparar_dataset(train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    """
    Divide dataset em train/val/test.
    
    Args:
        train_ratio: Proporção para treino (default: 70%)
        val_ratio: Proporção para validação (default: 20%)
        test_ratio: Proporção para teste (default: 10%)
    """
    # Listar todas as imagens
    images = list(IMAGES_DIR.glob("*.jpg"))
    
    if not images:
        print("❌ Nenhuma imagem encontrada em", IMAGES_DIR)
        print("   Execute primeiro: python anotar_quedas.py")
        return
    
    print(f"📊 Total de imagens: {len(images)}")
    
    # Separar por vídeo (para evitar data leakage)
    por_video = defaultdict(list)
    for img in images:
        # Extrair nome do vídeo do nome do frame
        video_name = img.stem.split('_frame_')[0]
        por_video[video_name].append(img)
    
    print(f"📹 Vídeos únicos: {len(por_video)}")
    
    # Embaralhar vídeos
    videos = list(por_video.keys())
    random.seed(42)
    random.shuffle(videos)
    
    # Dividir vídeos
    total_videos = len(videos)
    train_end = int(total_videos * train_ratio)
    val_end = train_end + int(total_videos * val_ratio)
    
    train_videos = set(videos[:train_end])
    val_videos = set(videos[train_end:val_end])
    test_videos = set(videos[val_end:])
    
    print(f"\n📦 Divisão:")
    print(f"   Train: {len(train_videos)} vídeos")
    print(f"   Val: {len(val_videos)} vídeos")
    print(f"   Test: {len(test_videos)} vídeos")
    
    # Copiar arquivos
    stats = {'train': 0, 'val': 0, 'test': 0}
    
    for video_name, imgs in por_video.items():
        if video_name in train_videos:
            split = 'train'
        elif video_name in val_videos:
            split = 'val'
        else:
            split = 'test'
        
        for img in imgs:
            label = LABELS_DIR / f"{img.stem}.txt"
            
            # Copiar imagem
            shutil.copy(img, DATASET_DIR / split / "images" / img.name)
            
            # Copiar label (se existir)
            if label.exists():
                shutil.copy(label, DATASET_DIR / split / "labels" / label.name)
            else:
                # Criar label vazio (sem queda)
                (DATASET_DIR / split / "labels" / label.name).touch()
            
            stats[split] += 1
    
    print(f"\n✅ Dataset preparado:")
    print(f"   Train: {stats['train']} imagens")
    print(f"   Val: {stats['val']} imagens")
    print(f"   Test: {stats['test']} imagens")
    print(f"\n📁 Dataset salvo em: {DATASET_DIR}")
    
    # Criar arquivo de configuração YOLO
    criar_config_yolo()
    
    return stats

def criar_config_yolo():
    """Cria arquivo de configuração YOLO"""
    config_path = DATASET_DIR / "dataset.yaml"
    
    config = f"""# Dataset de Quedas - IASenior
# Configuração YOLO

path: {DATASET_DIR.absolute()}  # Caminho do dataset
train: train/images  # Pasta de treino (relativo ao path)
val: val/images      # Pasta de validação (relativo ao path)
test: test/images    # Pasta de teste (relativo ao path)

# Classes
names:
  0: queda

# Número de classes
nc: 1
"""
    
    with open(config_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Configuração YOLO salva em: {config_path}")

if __name__ == "__main__":
    preparar_dataset()

