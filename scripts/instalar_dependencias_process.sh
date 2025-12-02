#!/bin/bash
# ============================================================================
# Script Rápido - Instalar Dependências Faltantes no Server PROCESS
# ============================================================================

set -e

echo "=========================================="
echo "📦 Instalando Dependências Faltantes"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

if [ "$EUID" -ne 0 ]; then 
    echo "Execute como root: sudo bash $0"
    exit 1
fi

APP_DIR="/opt/iasenior"
VENV_DIR="${APP_DIR}/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Ambiente virtual não encontrado em $VENV_DIR"
    echo "Execute primeiro o script setup_server_process.sh"
    exit 1
fi

log "Ativando ambiente virtual..."
source "${VENV_DIR}/bin/activate"

log "Atualizando pip..."
pip install --upgrade pip setuptools wheel --quiet

log "Instalando dependências do requirements.txt..."

# Instalar todas as dependências do requirements.txt
if [ -f "${APP_DIR}/requirements.txt" ]; then
    pip install -r "${APP_DIR}/requirements.txt" --quiet
    log "✅ Dependências do requirements.txt instaladas"
else
    log "requirements.txt não encontrado, instalando dependências essenciais..."
    
    # Instalar dependências essenciais manualmente
    pip install mss opencv-python numpy pillow flask python-dotenv requests --quiet
fi

# Instalar dependências específicas que podem estar faltando
log "Instalando dependências adicionais..."

pip install \
    mss \
    opencv-python \
    numpy \
    pillow \
    flask \
    flask-cors \
    python-dotenv \
    requests \
    psycopg2-binary \
    --quiet

log "Verificando instalações..."

# Verificar módulos críticos
python -c "import mss; print('✅ mss OK')" || log "⚠️ mss não instalado"
python -c "import cv2; print('✅ opencv-python OK')" || log "⚠️ opencv-python não instalado"
python -c "import numpy; print('✅ numpy OK')" || log "⚠️ numpy não instalado"
python -c "import flask; print('✅ flask OK')" || log "⚠️ flask não instalado"
python -c "import psycopg2; print('✅ psycopg2 OK')" || log "⚠️ psycopg2 não instalado"
python -c "from ultralytics import YOLO; print('✅ ultralytics OK')" || log "⚠️ ultralytics não instalado"

echo ""
echo "=========================================="
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "🧪 Testar novamente:"
echo "   cd $APP_DIR"
echo "   source venv/bin/activate"
echo "   python scripts/stream_inferencia_rtsp.py"
echo ""

