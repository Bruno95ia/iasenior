#!/bin/bash
# ============================================================================
# Script de Limpeza - Remover instalações do IASenior do Server BD
# Executado por engano no servidor BD
# ============================================================================

set -e

echo "=========================================="
echo "🧹 Limpando instalações do IASenior do Server BD"
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
}

if [ "$EUID" -ne 0 ]; then 
    echo "Execute como root: sudo bash $0"
    exit 1
fi

# ============================================================================
# PASSO 1: Verificar o que foi instalado
# ============================================================================
log "Verificando o que foi instalado..."

# Verificar se código foi baixado
if [ -d "/opt/iasenior" ]; then
    warning "Diretório /opt/iasenior encontrado"
    ls -la /opt/iasenior | head -10
    read -p "Remover /opt/iasenior? (s/N): " REMOVER_CODIGO
    if [ "$REMOVER_CODIGO" = "s" ] || [ "$REMOVER_CODIGO" = "S" ]; then
        log "Removendo /opt/iasenior..."
        rm -rf /opt/iasenior
        log "✅ Removido"
    else
        log "Mantendo /opt/iasenior"
    fi
fi

# Verificar se Docker foi instalado
if command -v docker &>/dev/null; then
    warning "Docker encontrado: $(docker --version)"
    read -p "Remover Docker? (s/N): " REMOVER_DOCKER
    if [ "$REMOVER_DOCKER" = "s" ] || [ "$REMOVER_DOCKER" = "S" ]; then
        log "Removendo Docker..."
        systemctl stop docker 2>/dev/null || true
        apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>/dev/null || true
        apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin 2>/dev/null || true
        rm -rf /var/lib/docker
        rm -rf /etc/docker
        log "✅ Docker removido"
    else
        log "Mantendo Docker"
    fi
else
    log "✅ Docker não está instalado"
fi

# Verificar se serviço systemd foi criado
if [ -f "/etc/systemd/system/iasenior-inferencia.service" ]; then
    warning "Serviço iasenior-inferencia encontrado"
    read -p "Remover serviço? (s/N): " REMOVER_SERVICO
    if [ "$REMOVER_SERVICO" = "s" ] || [ "$REMOVER_SERVICO" = "S" ]; then
        log "Removendo serviço..."
        systemctl stop iasenior-inferencia 2>/dev/null || true
        systemctl disable iasenior-inferencia 2>/dev/null || true
        rm -f /etc/systemd/system/iasenior-inferencia.service
        systemctl daemon-reload
        log "✅ Serviço removido"
    else
        log "Mantendo serviço"
    fi
else
    log "✅ Serviço não encontrado"
fi

# Verificar MediaMTX
if [ -d "/opt/mediamtx" ]; then
    warning "MediaMTX encontrado em /opt/mediamtx"
    read -p "Remover MediaMTX? (s/N): " REMOVER_MEDIAMTX
    if [ "$REMOVER_MEDIAMTX" = "s" ] || [ "$REMOVER_MEDIAMTX" = "S" ]; then
        log "Removendo MediaMTX..."
        rm -rf /opt/mediamtx
        log "✅ MediaMTX removido"
    else
        log "Mantendo MediaMTX"
    fi
else
    log "✅ MediaMTX não encontrado"
fi

# ============================================================================
# PASSO 2: Verificar PostgreSQL (importante não quebrar!)
# ============================================================================
log "Verificando PostgreSQL..."

if systemctl is-active --quiet postgresql@16-main || systemctl is-active --quiet postgresql@15-main; then
    log "✅ PostgreSQL está rodando"
    
    # Testar conexão
    if psql -h localhost -U iasenior -d iasenior -c "SELECT 1;" &>/dev/null <<< "iasenior2366"; then
        log "✅ Conexão com banco iasenior OK"
    else
        warning "⚠️ Não foi possível testar conexão (pode ser normal)"
    fi
else
    warning "⚠️ PostgreSQL não está rodando"
    read -p "Iniciar PostgreSQL? (s/N): " INICIAR_PG
    if [ "$INICIAR_PG" = "s" ] || [ "$INICIAR_PG" = "S" ]; then
        systemctl start postgresql@16-main 2>/dev/null || systemctl start postgresql@15-main 2>/dev/null || true
        sleep 2
        log "✅ PostgreSQL iniciado"
    fi
fi

# ============================================================================
# PASSO 3: Verificar arquivos de configuração do PostgreSQL
# ============================================================================
log "Verificando configurações do PostgreSQL..."

# Verificar se configurações foram alteradas
if [ -f "/etc/postgresql/16/main/postgresql.conf.backup" ] || [ -f "/etc/postgresql/15/main/postgresql.conf.backup" ]; then
    log "✅ Backups encontrados (configurações estão seguras)"
else
    log "Nenhum backup encontrado"
fi

# ============================================================================
# RESUMO
# ============================================================================
echo ""
echo "=========================================="
echo "✅ LIMPEZA CONCLUÍDA!"
echo "=========================================="
echo ""
echo "📊 Status:"
echo "   PostgreSQL: $(systemctl is-active postgresql@16-main 2>/dev/null || systemctl is-active postgresql@15-main 2>/dev/null || echo 'não rodando')"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   - O PostgreSQL deve continuar funcionando normalmente"
echo "   - Teste a conexão: psql -h localhost -U iasenior -d iasenior"
echo "   - Se algo não funcionar, restaure os backups em /etc/postgresql/*/main/*.backup"
echo ""
echo "✅ Server BD deve estar limpo e funcionando"
echo ""

