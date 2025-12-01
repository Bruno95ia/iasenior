"""
Treina modelo YOLOv8 customizado para detecção de quedas.
"""

import sys
from pathlib import Path

# Adicionar raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ultralytics import YOLO
import torch

DATASET_DIR = Path(__file__).parent / "dataset_yolo"
CONFIG_PATH = DATASET_DIR / "dataset.yaml"
MODELOS_DIR = Path(__file__).parent.parent.parent / "modelos"
MODELOS_DIR.mkdir(exist_ok=True)

def treinar_modelo(epochs=100, imgsz=640, batch=16, device=None, resume=None):
    """
    Treina modelo YOLOv8 para detecção de quedas.
    
    Args:
        epochs: Número de épocas
        imgsz: Tamanho da imagem
        batch: Batch size
        device: Device ('cpu', 'cuda', 'mps' ou None para auto)
        resume: Caminho do checkpoint para continuar treinamento (ex: 'last.pt')
    """
    if not CONFIG_PATH.exists():
        print(f"❌ Arquivo de configuração não encontrado: {CONFIG_PATH}")
        print("   Execute primeiro: python preparar_dataset.py")
        return None
    
    # Detectar device
    if device is None:
        if torch.cuda.is_available():
            device = 'cuda'
        elif torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    
    print(f"🖥️  Device: {device}")
    print(f"📊 Dataset: {CONFIG_PATH}")
    
    # Verificar se deve continuar de checkpoint
    if resume:
        checkpoint_path = MODELOS_DIR / "queda_custom" / "weights" / resume
        if checkpoint_path.exists():
            print(f"📦 Continuando de checkpoint: {checkpoint_path}")
            model = YOLO(str(checkpoint_path))
        else:
            print(f"⚠️  Checkpoint não encontrado: {checkpoint_path}")
            print("   Iniciando treinamento do zero...")
            modelo_base = "yolov8n.pt"
            print(f"📦 Modelo base: {modelo_base}")
            model = YOLO(modelo_base)
    else:
        # Verificar se existe checkpoint automático
        checkpoint_auto = MODELOS_DIR / "queda_custom" / "weights" / "last.pt"
        if checkpoint_auto.exists():
            print(f"💡 Checkpoint encontrado: {checkpoint_auto}")
            resposta = input("   Continuar de onde parou? (s/N): ").strip().lower()
            if resposta == 's':
                print(f"📦 Continuando de checkpoint: {checkpoint_auto}")
                model = YOLO(str(checkpoint_auto))
            else:
                modelo_base = "yolov8n.pt"
                print(f"📦 Modelo base: {modelo_base}")
                model = YOLO(modelo_base)
        else:
            # Carregar modelo base (YOLOv8n = nano, menor e mais rápido)
            # Pode usar: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
            modelo_base = "yolov8n.pt"
            print(f"📦 Modelo base: {modelo_base}")
            model = YOLO(modelo_base)
    
    # Treinar
    print(f"\n🚀 Iniciando treinamento...")
    print(f"   Épocas: {epochs}")
    print(f"   Tamanho imagem: {imgsz}")
    print(f"   Batch size: {batch}")
    
    results = model.train(
        data=str(CONFIG_PATH),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=str(MODELOS_DIR),
        name="queda_custom",
        exist_ok=True,
        patience=20,  # Early stopping
        save=True,
        plots=True,
        verbose=True
    )
    
    # Salvar melhor modelo
    melhor_modelo = Path(results.save_dir) / "weights" / "best.pt"
    modelo_final = MODELOS_DIR / "queda_custom.pt"
    
    if melhor_modelo.exists():
        import shutil
        shutil.copy(melhor_modelo, modelo_final)
        print(f"\n✅ Modelo treinado salvo em: {modelo_final}")
        print(f"📊 Resultados em: {results.save_dir}")
    else:
        print(f"\n⚠️  Modelo best.pt não encontrado em: {results.save_dir}")
    
    return results

def validar_modelo(modelo_path):
    """Valida modelo treinado"""
    if not Path(modelo_path).exists():
        print(f"❌ Modelo não encontrado: {modelo_path}")
        return
    
    model = YOLO(modelo_path)
    
    results = model.val(data=str(CONFIG_PATH))
    
    print(f"\n📊 Métricas de Validação:")
    print(f"   mAP50: {results.box.map50:.4f}")
    print(f"   mAP50-95: {results.box.map:.4f}")
    print(f"   Precision: {results.box.mp:.4f}")
    print(f"   Recall: {results.box.mr:.4f}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Treinar modelo YOLOv8 para detecção de quedas")
    parser.add_argument("--epochs", type=int, default=100, help="Número de épocas")
    parser.add_argument("--imgsz", type=int, default=640, help="Tamanho da imagem")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu/cuda/mps)")
    parser.add_argument("--resume", type=str, default=None, help="Checkpoint para continuar (ex: last.pt)")
    parser.add_argument("--validar", action="store_true", help="Validar modelo após treinamento")
    
    args = parser.parse_args()
    
    # Treinar
    results = treinar_modelo(
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        resume=args.resume
    )
    
    # Validar se solicitado
    if args.validar and results:
        modelo_path = MODELOS_DIR / "queda_custom.pt"
        validar_modelo(modelo_path)

