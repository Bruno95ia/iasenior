#!/bin/bash

# === Script melhorado para parar todos os serviços ===
# Adicionado validação, tratamento de erros e limpeza adequada

set -e  # Parar em caso de erro (comentado para permitir continuidade)

LOGS_DIR="${LOGS_DIR:-./logs}"
PID_FILE="${PID_FILE:-./.pids}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Função para parar processo por PID
stop_by_pid() {
    local name=$1
    local pid_file="${PID_FILE}_${name}"
    
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "🛑 Parando $name (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            # Force kill se ainda estiver rodando
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            log "✅ $name parado"
        else
            log "⚠️ Processo $name (PID: $pid) não está rodando"
        fi
        rm -f "$pid_file"
    fi
}

# Função para parar processos por nome
stop_by_name() {
    local pattern=$1
    local name=$2
    
    local pids
    pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    
    if [ ! -z "$pids" ]; then
        log "🛑 Parando processos $name..."
        echo "$pids" | xargs kill 2>/dev/null || true
        sleep 1
        # Force kill se ainda estiverem rodando
        pids=$(pgrep -f "$pattern" 2>/dev/null || true)
        if [ ! -z "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
        log "✅ Processos $name parados"
    else
        log "⚠️ Nenhum processo $name encontrado"
    fi
}

# Função para parar porta
stop_port() {
    local port=$1
    local name=$2
    
    local pids
    pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ ! -z "$pids" ]; then
        log "🛑 Parando processo na porta $port ($name)..."
        echo "$pids" | xargs kill 2>/dev/null || true
        sleep 1
        # Force kill se ainda estiver rodando
        pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
        log "✅ Porta $port liberada"
    fi
}

log "🛑 Encerrando todos os serviços..."

# === PARAR CONTAINERS DOCKER ===
log "⛔ Parando containers Docker..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
    log "✅ Containers Docker parados"
else
    # Tentar parar containers individuais
    docker stop painel_iasenior 2>/dev/null || true
    docker stop mediamtx 2>/dev/null || true
fi

# Parar painel do diretório painel_IA
if [ -f "painel_IA/docker-compose.yml" ]; then
    cd painel_IA
    docker-compose down 2>/dev/null || true
    cd ..
fi

# === PARAR PROCESSOS POR PID ===
log "🧹 Parando processos salvos..."

stop_by_pid "mediamtx"
stop_by_pid "transmissao"
stop_by_pid "inferencia"
stop_by_pid "painel"

# === PARAR PROCESSOS POR NOME ===
log "🧹 Parando processos por padrão..."

stop_by_name "mediamtx" "MediaMTX"
stop_by_name "stream_inferencia_rtsp.py" "Inferência RTSP"
stop_by_name "transmitir_gpu_m1.sh" "Transmissão"
stop_by_name "transmitir_rtsp.py" "Transmissão RTSP"
stop_by_name "captura_inferencia.py" "Captura/Inferência"
stop_by_name "mjpeg_server.py" "Servidor MJPEG"
stop_by_name "streamlit" "Streamlit"

# === LIBERAR PORTAS ===
log "🔌 Liberando portas..."

stop_port 8554 "MediaMTX"
stop_port 8501 "Streamlit"
stop_port 8888 "MJPEG Server"

# === LIMPEZA FINAL ===
log "🧹 Limpando arquivos temporários..."

# Limpar arquivos de PID
rm -f "${PID_FILE}"_* 2>/dev/null || true

log "✅ Tudo encerrado com sucesso!"
