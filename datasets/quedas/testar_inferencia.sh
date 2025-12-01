#!/bin/bash
# Script para testar inferência de quedas com ambiente virtual ativado

# Ativar ambiente virtual
cd "$(dirname "$0")/../.."
source venv/bin/activate

# Voltar para diretório de quedas
cd datasets/quedas

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo "❌ Uso: $0 <video.mp4> [--modelo modelo.pt] [--conf 0.5]"
    echo ""
    echo "Vídeos disponíveis:"
    ls -1 videos/*.mp4 2>/dev/null | sed 's/^/   /' || echo "   Nenhum vídeo encontrado"
    exit 1
fi

VIDEO="$1"
shift  # Remove primeiro argumento, passa resto para Python

# Verificar se vídeo existe
if [ ! -f "$VIDEO" ]; then
    echo "❌ Vídeo não encontrado: $VIDEO"
    exit 1
fi

echo "🎬 Testando detecção de quedas..."
echo "📹 Vídeo: $VIDEO"
echo ""
echo "💡 Dica: O modelo customizado precisa de threshold baixo (0.01-0.1)"
echo "   Threshold padrão: 0.05"
echo "   Para mais detecções: --conf 0.01"
echo "   Para menos falsos positivos: --conf 0.1"
echo ""

# Verificar se quer testar com múltiplos thresholds
if [ "$1" = "--teste-detalhado" ]; then
    shift
    VIDEO="$1"
    shift
    echo "🔍 Executando teste detalhado com múltiplos thresholds..."
    python3 testar_deteccoes_detalhado.py "$VIDEO" "$@"
else
    # Executar inferência normal
    python3 inferencia_quedas.py "$VIDEO" "$@"
fi

