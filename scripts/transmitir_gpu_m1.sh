#!/bin/bash

# ===== Transmissão com GPU Apple Silicon (M1/M2) =====

# Nome do stream e URL do MediaMTX
STREAM_NAME="tela"
RTSP_URL="rtsp://localhost:8554/${STREAM_NAME}"

# Configurações do vídeo
DEVICE="6"                # Capture screen 2 (monitor virtual)
FRAMERATE="30"
RESOLUCAO="1280x720"

echo "🟢 Iniciando transmissão da tela (device ${DEVICE}) para:"
echo "🔗 ${RTSP_URL}"
echo ""

# Executa a transmissão
ffmpeg \
  -f avfoundation \
  -framerate "$FRAMERATE" \
  -video_size "$RESOLUCAO" \
  -i "$DEVICE" \
  -vcodec h264_videotoolbox \
  -pix_fmt yuv420p \
  -preset ultrafast \
  -tune zerolatency \
  -fflags +genpts \
  -f rtsp -rtsp_transport tcp "$RTSP_URL"

# Caso o ffmpeg falhe, mostra a mensagem
if [[ $? -ne 0 ]]; then
  echo "❌ Erro ao iniciar o ffmpeg. Verifique se o device \"$DEVICE\" está disponível."
  echo "Execute: ffmpeg -f avfoundation -list_devices true -i \"\""
fi
