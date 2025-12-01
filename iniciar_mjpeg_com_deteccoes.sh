#!/bin/bash
# Script para iniciar servidor MJPEG com detecções YOLO

cd "$(dirname "$0")"

echo "🚀 Iniciando servidor MJPEG com detecções YOLO..."
echo ""

# Verificar se ambiente virtual existe
if [ -d "venv" ]; then
    echo "✅ Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️ Ambiente virtual não encontrado. Usando Python do sistema."
fi

# Verificar se modelo existe
MODELO_PATH="modelos/queda_custom.pt"
if [ ! -f "$MODELO_PATH" ]; then
    echo "⚠️ Modelo customizado não encontrado em: $MODELO_PATH"
    echo "   Usando modelo padrão do YOLO..."
fi

# Iniciar servidor
echo "🌐 Servidor MJPEG será iniciado em:"
echo "   - URL: http://localhost:8888/video"
echo "   - Status: http://localhost:8888/status"
echo "   - Health: http://localhost:8888/health"
echo ""
echo "📡 Stream RTSP configurado em config.py"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

python3 mjpeg_server_com_deteccoes.py

