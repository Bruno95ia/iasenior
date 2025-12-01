#!/bin/bash

# Garantir que estamos no diretório correto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔁 Ativando ambiente da IA (rtsp_env)..."
source rtsp_env/bin/activate

echo "🎯 Iniciando MediaMTX com configuração personalizada..."
# MediaMTX usa argumento posicional para o config, não flag -c
CONFIG_FILE="${MEDIAMTX_CONFIG:-./mediamtx.yml}"
if [ -f "$CONFIG_FILE" ]; then
    /opt/homebrew/opt/mediamtx/bin/mediamtx "$CONFIG_FILE" &
else
    echo "⚠️ Arquivo de configuração não encontrado em $CONFIG_FILE, usando configuração padrão"
    /opt/homebrew/opt/mediamtx/bin/mediamtx &
fi

sleep 2

echo "📡 Iniciando transmissão com IA..."
python3 scripts/transmitir_rtsp.py &

echo "🧠 Iniciando inferência com IA..."
python3 scripts/captura_inferencia.py &

deactivate
