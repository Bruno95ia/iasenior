#!/bin/bash

# Script para treinar modelo YOLO com GPU otimizada (MacBook Apple Silicon)
# Otimizado para usar MPS (Metal Performance Shaders)

set -e

echo "🚀 Treinamento YOLO com GPU Otimizada - IASenior"
echo "=================================================="
echo ""

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se está no diretório correto
if [ ! -d "datasets" ]; then
    echo "❌ Execute este script da raiz do projeto"
    exit 1
fi

# Verificar dataset
if [ ! -f "datasets/quedas/dataset_yolo/dataset.yaml" ]; then
    echo "📦 Preparando dataset..."
    cd datasets/quedas
    python3 preparar_dataset.py
    cd ../..
fi

# Verificar PyTorch e GPU
echo "🔍 Verificando ambiente..."
python3 << EOF
import sys
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"✅ CUDA disponível: {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("✅ MPS (Apple Silicon GPU) disponível")
    else:
        print("⚠️  GPU não disponível, usando CPU")
except ImportError:
    print("❌ PyTorch não instalado")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Erro ao verificar ambiente"
    exit 1
fi

echo ""
echo "🏋️  Iniciando treinamento..."
echo ""

# Parâmetros otimizados para MacBook
EPOCHS=100
BATCH=16  # Ajustado para MPS
IMG_SIZE=640
MODELO="yolov8n.pt"  # Começar com nano (mais rápido)

# Usar script de quedas que já tem suporte MPS
cd datasets/quedas

python3 treinar_modelo.py \
    --epochs $EPOCHS \
    --batch $BATCH \
    --imgsz $IMG_SIZE \
    --device mps \
    --validar

echo ""
echo "✅ Treinamento concluído!"
echo ""
echo "📦 Modelo salvo em: modelos/queda_custom.pt"
echo "💡 Para usar o modelo, atualize MODEL_PATH no config.py"

