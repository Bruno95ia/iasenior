#!/bin/bash
# ============================================================================
# Script de Correção - Instalar Docker no Server PROCESS
# ============================================================================

set -e

echo "=========================================="
echo "🐳 Instalando Docker - Server PROCESS"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

if [ "$EUID" -ne 0 ]; then 
    error "Execute como root: sudo bash $0"
fi

# ============================================================================
# PASSO 1: Remover instalações antigas (se houver)
# ============================================================================
log "Limpando instalações antigas do Docker..."

apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# ============================================================================
# PASSO 2: Configurar DNS (se necessário)
# ============================================================================
log "Configurando DNS..."

if ! ping -c 1 8.8.8.8 &>/dev/null; then
    warning "Sem conectividade, configurando DNS..."
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf
    systemctl restart systemd-resolved 2>/dev/null || true
    sleep 2
fi

# Alterar repositórios
if grep -q "br\.archive\.ubuntu\.com" /etc/apt/sources.list 2>/dev/null; then
    log "Alterando repositórios..."
    sed -i 's/br\.archive\.ubuntu\.com/archive.ubuntu.com/g' /etc/apt/sources.list
fi

# ============================================================================
# PASSO 3: Atualizar sistema
# ============================================================================
log "Atualizando sistema..."

export DEBIAN_FRONTEND=noninteractive
apt-get update -y

# ============================================================================
# PASSO 4: Instalar dependências
# ============================================================================
log "Instalando dependências..."

apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# ============================================================================
# PASSO 5: Adicionar chave GPG do Docker
# ============================================================================
log "Adicionando chave GPG do Docker..."

install -m 0755 -d /etc/apt/keyrings

# Tentar baixar chave
if curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg; then
    log "✅ Chave GPG adicionada"
else
    error "❌ Falha ao adicionar chave GPG"
fi

chmod a+r /etc/apt/keyrings/docker.gpg

# ============================================================================
# PASSO 6: Adicionar repositório Docker
# ============================================================================
log "Adicionando repositório Docker..."

ARCH=$(dpkg --print-architecture)
CODENAME=$(lsb_release -cs)

echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

log "✅ Repositório adicionado"

# ============================================================================
# PASSO 7: Atualizar e instalar Docker
# ============================================================================
log "Atualizando repositórios..."

apt-get update -y

log "Instalando Docker..."

apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# ============================================================================
# PASSO 8: Iniciar e habilitar Docker
# ============================================================================
log "Iniciando Docker..."

systemctl start docker
systemctl enable docker

# Aguardar inicialização
sleep 3

# ============================================================================
# PASSO 9: Verificar instalação
# ============================================================================
log "Verificando instalação..."

if systemctl is-active --quiet docker; then
    log "✅ Docker está rodando"
else
    error "❌ Docker não está rodando"
fi

if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker --version)
    log "✅ Docker instalado: $DOCKER_VERSION"
else
    error "❌ Docker não encontrado no PATH"
fi

# Testar Docker
if docker run --rm hello-world &>/dev/null; then
    log "✅ Docker funcionando corretamente"
else
    warning "⚠️ Teste do Docker falhou, mas pode estar funcionando"
fi

# ============================================================================
# RESUMO
# ============================================================================
echo ""
echo "=========================================="
echo "✅ DOCKER INSTALADO COM SUCESSO!"
echo "=========================================="
echo ""
echo "📊 Informações:"
echo "   Versão: $(docker --version)"
echo "   Status: $(systemctl is-active docker)"
echo ""
echo "🧪 Testar:"
echo "   docker --version"
echo "   docker ps"
echo "   systemctl status docker"
echo ""
echo "✅ Agora você pode executar o script setup_server_process.sh novamente"
echo ""

