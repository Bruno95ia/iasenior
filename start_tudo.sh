#!/bin/bash

# === Script melhorado para iniciar todos os serviços ===
# Adicionado validação de dependências, tratamento de erros e logging

set -e  # Parar em caso de erro (comentado para permitir continuidade)

# === CONFIGURAÇÕES ===
STREAM_NAME="${STREAM_NAME:-ia}"
RTSP_URL="rtsp://localhost:8554/${STREAM_NAME}"
ENV_PATH="${ENV_PATH:-./venv/bin/activate}"
INFERENCIA_SCRIPT="${INFERENCIA_SCRIPT:-scripts/stream_inferencia_rtsp.py}"
TRANSMISSOR_SCRIPT="${TRANSMISSOR_SCRIPT:-scripts/transmitir_gpu_m1.sh}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-docker-compose.yml}"
LOGS_DIR="${LOGS_DIR:-./logs}"
PID_FILE="${PID_FILE:-./.pids}"

# Criar diretório de logs
mkdir -p "$LOGS_DIR"

# Log file
LOG_FILE="$LOGS_DIR/start_tudo.log"

# Função de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função de erro
error() {
    log "❌ ERRO: $1"
    exit 1
}

# Função para verificar se comando existe
check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        error "Comando '$1' não encontrado. Instale-o antes de continuar."
    fi
}

# Função para verificar se porta está em uso
check_port() {
    local port=$1
    if lsof -ti:$port >/dev/null 2>&1; then
        log "⚠️ Porta $port está em uso"
        return 0
    fi
    return 1
}

# Função para matar processo na porta
kill_port() {
    local port=$1
    local PID
    PID=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        log "⚠️ Encerrando processo na porta $port (PID: $PID)..."
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
    fi
}

# Função para salvar PID
save_pid() {
    local name=$1
    local pid=$2
    mkdir -p "$(dirname "$PID_FILE")"
    echo "$pid" > "${PID_FILE}_${name}"
    log "📌 PID de $name salvo: $pid"
}

# === VALIDAÇÃO DE DEPENDÊNCIAS ===
log "🔍 Verificando dependências..."

check_command python3
check_command ffmpeg
check_command docker

if ! docker info >/dev/null 2>&1; then
    error "Docker não está rodando. Inicie o Docker antes de continuar."
fi

# === LIMPEZA DE PORTAS ===
log "🔁 Verificando portas em uso..."
kill_port 8554
kill_port 8501
kill_port 8888

# === INICIAR MEDIAMTX ===
log "🚀 Iniciando MediaMTX (RTSP Server)..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d mediamtx
    log "✅ MediaMTX iniciado via Docker Compose"
else
    log "⚠️ docker-compose.yml não encontrado. Tentando iniciar MediaMTX diretamente..."
    if command -v mediamtx >/dev/null 2>&1; then
        # Determinar caminho do arquivo de configuração
        CONFIG_FILE="${MEDIAMTX_CONFIG:-./mediamtx.yml}"
        if [ ! -f "$CONFIG_FILE" ]; then
            log "⚠️ Arquivo de configuração não encontrado em $CONFIG_FILE, usando configuração padrão"
            CONFIG_FILE=""
        fi
        # MediaMTX usa argumento posicional para o config, não flag -c
        if [ -n "$CONFIG_FILE" ]; then
            nohup mediamtx "$CONFIG_FILE" > "$LOGS_DIR/mediamtx.log" 2>&1 &
        else
            nohup mediamtx > "$LOGS_DIR/mediamtx.log" 2>&1 &
        fi
        MEDIAMTX_PID=$!
        save_pid "mediamtx" "$MEDIAMTX_PID"
        log "✅ MediaMTX iniciado (PID: $MEDIAMTX_PID)"
    else
        error "MediaMTX não encontrado e docker-compose.yml não disponível"
    fi
fi

sleep 3

# === ATIVAR AMBIENTE VIRTUAL ===
if [ -f "$ENV_PATH" ]; then
    log "📦 Ativando ambiente virtual em $ENV_PATH..."
    source "$ENV_PATH"
else
    log "⚠️ Ambiente virtual não encontrado em $ENV_PATH — prosseguindo sem ativar."
fi

# Verificar se Python tem as dependências necessárias
log "🔍 Verificando dependências Python..."
python3 -c "import cv2, ultralytics, flask, streamlit" 2>/dev/null || {
    log "⚠️ Algumas dependências Python podem estar faltando. Verifique requirements.txt"
}

# === INICIAR TRANSMISSÃO ===
log "📡 Iniciando transmissão com aceleração M1..."

if [ -f "$TRANSMISSOR_SCRIPT" ]; then
    bash "$TRANSMISSOR_SCRIPT" > "$LOGS_DIR/transmissao.log" 2>&1 &
    TRANSMISSOR_PID=$!
    save_pid "transmissao" "$TRANSMISSOR_PID"
    log "✅ Transmissão iniciada (PID: $TRANSMISSOR_PID)"
else
    log "⚠️ Script de transmissão não encontrado: $TRANSMISSOR_SCRIPT"
fi

sleep 2

# === INICIAR INFERÊNCIA ===
log "🧠 Iniciando inferência em background..."

if [ -f "$INFERENCIA_SCRIPT" ]; then
    python3 "$INFERENCIA_SCRIPT" >> "$LOGS_DIR/inferencia.log" 2>&1 &
    INFERENCIA_PID=$!
    save_pid "inferencia" "$INFERENCIA_PID"
    log "✅ Inferência iniciada (PID: $INFERENCIA_PID)"
else
    error "Script de inferência não encontrado: $INFERENCIA_SCRIPT"
fi

sleep 2

# === INICIAR PAINEL ===
log "📊 Iniciando painel Streamlit..."

if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d painel
    log "✅ Painel iniciado via Docker Compose"
else
    log "⚠️ docker-compose.yml não encontrado. Tentando iniciar Streamlit diretamente..."
    if [ -f "painel_IA/app/dashboard.py" ]; then
        cd painel_IA/app
        nohup streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501 > "../../$LOGS_DIR/painel.log" 2>&1 &
        PAINEL_PID=$!
        cd ../..
        save_pid "painel" "$PAINEL_PID"
        log "✅ Painel iniciado (PID: $PAINEL_PID)"
    else
        log "⚠️ Dashboard não encontrado"
    fi
fi

sleep 2

# === ABRIR VLC ===
log "🎥 Tentando abrir VLC apontando para $RTSP_URL..."

if command -v open >/dev/null 2>&1; then
    open -a VLC "$RTSP_URL" 2>/dev/null || log "⚠️ VLC não encontrado ou erro ao abrir"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$RTSP_URL" 2>/dev/null || log "⚠️ Erro ao abrir stream"
else
    log "⚠️ Comando para abrir aplicação não encontrado. Abra manualmente: $RTSP_URL"
fi

# === RESUMO ===
echo ""
log "═══════════════════════════════════════════════════════════"
log "✅ Tudo pronto!"
log "═══════════════════════════════════════════════════════════"
log "📌 PIDs salvos em: $PID_FILE"
log "📌 Logs em: $LOGS_DIR"
log "📺 Stream RTSP: $RTSP_URL"
log "📊 Painel: http://localhost:8501"
log ""
log "Para parar tudo, execute: ./stop_tudo.sh"
log "═══════════════════════════════════════════════════════════"
