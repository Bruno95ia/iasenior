#!/bin/bash
# Script para escolher método de anotação

cd "$(dirname "$0")"
cd ../..

echo "🎯 Escolha o Método de Anotação"
echo "================================"
echo ""
echo "1. ⚡ Anotação Rápida (Recomendado para velocidade)"
echo "   - Modo turbo com atalhos"
echo "   - Detecção automática"
echo "   - ~200-300 frames/hora"
echo ""
echo "2. 🤖 Anotação Inteligente (Recomendado para precisão)"
echo "   - IA detecta pessoas automaticamente"
echo "   - Sugestões de bbox"
echo "   - Propagação automática"
echo "   - ~100-150 frames/hora"
echo ""
echo "3. 🎬 Anotação por Vídeo (Mais rápido para muitos frames)"
echo "   - Marque início/fim das quedas"
echo "   - Timeline visual"
echo "   - Gera anotações automaticamente"
echo "   - ~10-20 quedas/hora (mas cada queda = muitos frames!)"
echo ""
echo "4. 📝 Anotação Manual (Original)"
echo "   - Controle total"
echo "   - Interface completa"
echo ""
read -p "Escolha (1-4): " escolha

case $escolha in
    1)
        echo "🚀 Iniciando Anotação Rápida..."
        streamlit run datasets/quedas/anotar_rapido.py
        ;;
    2)
        echo "🤖 Iniciando Anotação Inteligente..."
        streamlit run datasets/quedas/anotar_quedas_inteligente.py
        ;;
    3)
        echo "🎬 Iniciando Anotação por Vídeo..."
        streamlit run datasets/quedas/anotar_por_video.py
        ;;
    4)
        echo "📝 Iniciando Anotação Manual..."
        streamlit run datasets/quedas/anotar_quedas.py
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac
