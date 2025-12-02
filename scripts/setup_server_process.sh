#!/bin/bash
# ============================================================================
# Script Completo - Configuração Server PROCESS (Inferência YOLO)
# Sistema IASenior - Opus Tech
# ============================================================================

set -e

echo "=========================================="
echo "🤖 Configurando Server PROCESS - Inferência YOLO"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    error "Execute como root: sudo bash $0"
fi

APP_DIR="/opt/iasenior"
VENV_DIR="${APP_DIR}/venv"

# ============================================================================
# PASSO 1: Configurar DNS
# ============================================================================
log "Configurando DNS..."

# Verificar conectividade
if ! ping -c 1 8.8.8.8 &>/dev/null; then
    warning "Sem conectividade com internet"
else
    log "✅ Conectividade OK"
fi

# Configurar DNS permanente
if [ ! -f /etc/systemd/resolved.conf.backup ]; then
    cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.backup
fi

cat > /etc/systemd/resolved.conf <<EOF
[Resolve]
DNS=8.8.8.8 8.8.4.4 1.1.1.1
FallbackDNS=1.1.1.1 1.0.0.1
Domains=~.
DNSSEC=no
EOF

systemctl restart systemd-resolved 2>/dev/null || true
sleep 2

# Alterar repositórios para usar archive.ubuntu.com
if grep -q "br\.archive\.ubuntu\.com" /etc/apt/sources.list 2>/dev/null; then
    log "Alterando repositórios para archive.ubuntu.com..."
    sed -i 's/br\.archive\.ubuntu\.com/archive.ubuntu.com/g' /etc/apt/sources.list
    sed -i 's/br\.security\.ubuntu\.com/security.ubuntu.com/g' /etc/apt/sources.list 2>/dev/null || true
fi

# ============================================================================
# PASSO 2: Atualizar sistema
# ============================================================================
log "Atualizando sistema..."

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-pip python3-venv git curl wget

# ============================================================================
# PASSO 3: Verificar/Instalar Docker
# ============================================================================
log "Verificando Docker..."

if command -v docker &>/dev/null; then
    log "✅ Docker já instalado: $(docker --version)"
else
    log "Instalando Docker..."
    
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    systemctl start docker
    systemctl enable docker
    
    log "✅ Docker instalado"
fi

# Verificar se Docker está rodando
if systemctl is-active --quiet docker; then
    log "✅ Docker está rodando"
else
    warning "Docker não está rodando, iniciando..."
    systemctl start docker
    sleep 2
fi

# ============================================================================
# PASSO 4: Instalar FFmpeg
# ============================================================================
log "Verificando FFmpeg..."

if command -v ffmpeg &>/dev/null; then
    log "✅ FFmpeg já instalado: $(ffmpeg -version | head -1)"
else
    log "Instalando FFmpeg..."
    apt-get install -y ffmpeg
    log "✅ FFmpeg instalado"
fi

# ============================================================================
# PASSO 5: Baixar/Atualizar código do GitHub
# ============================================================================
log "Configurando código do projeto..."

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ -d ".git" ]; then
    log "Atualizando código existente..."
    git pull || warning "Falha ao atualizar, continuando..."
else
    log "Baixando código do GitHub..."
    if [ -d "$APP_DIR" ] && [ "$(ls -A $APP_DIR)" ]; then
        warning "Diretório não vazio, fazendo backup..."
        mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$APP_DIR"
    fi
    
    git clone https://github.com/Bruno95ia/iasenior.git "$APP_DIR" || error "Falha ao clonar repositório"
    log "✅ Código baixado"
fi

# ============================================================================
# PASSO 6: Criar ambiente virtual Python
# ============================================================================
log "Configurando ambiente virtual Python..."

if [ -d "$VENV_DIR" ]; then
    log "✅ Ambiente virtual já existe"
else
    log "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    log "✅ Ambiente virtual criado"
fi

# Ativar ambiente virtual
source "${VENV_DIR}/bin/activate"

# Atualizar pip
log "Atualizando pip..."
pip install --upgrade pip setuptools wheel --quiet

# ============================================================================
# PASSO 7: Instalar dependências Python
# ============================================================================
log "Instalando dependências Python..."

# Instalar PyTorch (CPU primeiro, pode ser ajustado depois)
log "Instalando PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet

# Instalar outras dependências essenciais
log "Instalando dependências ML/CV..."
pip install ultralytics opencv-python numpy pillow flask python-dotenv requests --quiet

# Verificar instalações críticas
log "Verificando instalações..."
python -c "import torch; print(f'✅ PyTorch: {torch.__version__}')" || error "PyTorch não instalado"
python -c "from ultralytics import YOLO; print('✅ YOLO OK')" || error "YOLO não instalado"
python -c "import cv2; print(f'✅ OpenCV: {cv2.__version__}')" || error "OpenCV não instalado"

log "✅ Dependências instaladas"

# ============================================================================
# PASSO 8: Configurar MediaMTX
# ============================================================================
log "Configurando MediaMTX..."

MEDIAMTX_DIR="/opt/mediamtx"
mkdir -p "$MEDIAMTX_DIR"
cd "$MEDIAMTX_DIR"

if [ ! -f mediamtx ]; then
    log "Baixando MediaMTX..."
    wget -q https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_v1.5.1_linux_amd64.tar.gz || \
    wget -q https://github.com/bluenviron/mediamtx/releases/download/v1.5.1/mediamtx_v1.5.1_linux_amd64.tar.gz
    
    if [ -f mediamtx_v1.5.1_linux_amd64.tar.gz ]; then
        tar -xzf mediamtx_v1.5.1_linux_amd64.tar.gz
        chmod +x mediamtx
        rm mediamtx_v1.5.1_linux_amd64.tar.gz
        log "✅ MediaMTX baixado"
    else
        warning "Não foi possível baixar MediaMTX, continuando..."
    fi
else
    log "✅ MediaMTX já existe"
fi

# Criar config básica se não existir
if [ ! -f mediamtx.yml ]; then
    cat > mediamtx.yml <<EOF
paths:
  ia:
    source: publisher
    sourceOnDemand: yes
EOF
    log "✅ Configuração MediaMTX criada"
fi

# ============================================================================
# PASSO 9: Configurar arquivo .env
# ============================================================================
log "Configurando arquivo .env..."

cd "$APP_DIR"

# Solicitar IPs se não estiverem no .env
if [ ! -f .env ] || ! grep -q "DB_HOST=" .env 2>/dev/null; then
    info "Preciso dos IPs dos servidores:"
    read -p "IP do Server BD (PostgreSQL): " DB_IP
    read -p "IP do Server STR (Storage): " STR_IP
    
    # Validação básica
    if [ -z "$DB_IP" ] || [ -z "$STR_IP" ]; then
        warning "IPs não fornecidos, usando valores padrão"
        DB_IP="localhost"
        STR_IP="localhost"
    fi
else
    # Ler IPs do .env existente
    DB_IP=$(grep "^DB_HOST=" .env 2>/dev/null | cut -d= -f2 | tr -d ' ' || echo "localhost")
    STR_IP=$(grep "^STORAGE_HOST=" .env 2>/dev/null | cut -d= -f2 | tr -d ' ' || echo "localhost")
    log "Usando IPs do .env existente"
fi

# Criar/Atualizar .env
cat > .env <<EOF
# ============================================================================
# Server PROCESS - Inferência YOLO
# ============================================================================

# Stream RTSP
RTSP_HOST=localhost
RTSP_PORT=8554
STREAM_NAME=ia

# Modelo YOLO
MODEL_PATH=modelos/queda_custom.pt
CONFIDENCE_THRESHOLD=0.4
FALL_DETECTION_ENABLED=true
TRACKING_ENABLED=true

# Banco de Dados (Server BD)
DB_HOST=${DB_IP}
DB_PORT=5432
DB_NAME=iasenior
DB_USER=iasenior
DB_PASSWORD=iasenior2366

# Storage (Server STR)
STORAGE_HOST=${STR_IP}
STORAGE_PATH=/mnt/iasenior

# Captura de tela
MONITOR_IDX=0
FRAME_WIDTH=1280
FRAME_HEIGHT=720
FPS=20

# MJPEG
MJPEG_PORT=8888
MJPEG_HOST=0.0.0.0
EOF

log "✅ Arquivo .env configurado"

# ============================================================================
# PASSO 10: Testar conexão com BD
# ============================================================================
log "Testando conexão com banco de dados..."

# Instalar cliente PostgreSQL se necessário
if ! command -v psql &>/dev/null; then
    log "Instalando cliente PostgreSQL..."
    apt-get install -y postgresql-client
fi

# Testar conexão
if psql -h "$DB_IP" -U iasenior -d iasenior -c "SELECT 1;" &>/dev/null <<< "iasenior2366"; then
    log "✅ Conexão com BD OK"
else
    warning "⚠️ Não foi possível conectar ao BD automaticamente"
    info "Teste manualmente: psql -h $DB_IP -U iasenior -d iasenior"
fi

# ============================================================================
# PASSO 11: Verificar modelo YOLO
# ============================================================================
log "Verificando modelo YOLO..."

if [ -f "${APP_DIR}/modelos/queda_custom.pt" ]; then
    log "✅ Modelo customizado encontrado"
else
    warning "Modelo customizado não encontrado, será baixado na primeira execução"
fi

# ============================================================================
# PASSO 12: Criar serviço systemd
# ============================================================================
log "Configurando serviço systemd..."

cat > /etc/systemd/system/iasenior-inferencia.service <<EOF
[Unit]
Description=IASenior - Inferência YOLO
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=${VENV_DIR}/bin/python ${APP_DIR}/scripts/stream_inferencia_rtsp.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable iasenior-inferencia

log "✅ Serviço systemd criado (não iniciado ainda)"

# ============================================================================
# PASSO 13: Verificações finais
# ============================================================================
log "Realizando verificações finais..."

# Verificar estrutura
if [ -f "${APP_DIR}/scripts/stream_inferencia_rtsp.py" ]; then
    log "✅ Script de inferência encontrado"
else
    error "❌ Script de inferência não encontrado"
fi

# Verificar Python
if [ -f "${VENV_DIR}/bin/python" ]; then
    PYTHON_VERSION=$("${VENV_DIR}/bin/python" --version)
    log "✅ Python: $PYTHON_VERSION"
else
    error "❌ Python não encontrado no venv"
fi

# Verificar dependências
source "${VENV_DIR}/bin/activate"
python -c "import torch, ultralytics, cv2; print('✅ Todas as dependências OK')" || warning "Algumas dependências podem estar faltando"

# ============================================================================
# RESUMO FINAL
# ============================================================================
echo ""
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "📊 Informações:"
echo "   Diretório: $APP_DIR"
echo "   Ambiente virtual: $VENV_DIR"
echo "   IP do BD: $DB_IP"
echo "   IP do STR: $STR_IP"
echo ""
echo "🧪 Próximos passos:"
echo ""
echo "1. Testar manualmente (recomendado):"
echo "   cd $APP_DIR"
echo "   source venv/bin/activate"
echo "   python scripts/stream_inferencia_rtsp.py"
echo ""
echo "2. Se funcionar, iniciar serviço:"
echo "   systemctl start iasenior-inferencia"
echo "   systemctl status iasenior-inferencia"
echo ""
echo "3. Ver logs:"
echo "   journalctl -u iasenior-inferencia -f"
echo ""
echo "4. Verificar portas:"
echo "   netstat -tulpn | grep -E '8554|8888'"
echo ""
echo "🔧 Comandos úteis:"
echo "   Parar: systemctl stop iasenior-inferencia"
echo "   Reiniciar: systemctl restart iasenior-inferencia"
echo "   Logs: journalctl -u iasenior-inferencia -n 50"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - Teste manualmente antes de iniciar o serviço"
echo "   - Verifique se o modelo YOLO está em: ${APP_DIR}/modelos/queda_custom.pt"
echo "   - Ajuste MONITOR_IDX no .env se necessário"
echo ""
echo "✅ Server PROCESS configurado e pronto!"
echo ""

