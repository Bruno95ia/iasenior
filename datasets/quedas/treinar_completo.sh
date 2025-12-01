#!/bin/bash
# Script completo para treinar modelo de quedas

cd "$(dirname "$0")"
cd ../..

echo "🚀 Pipeline Completo de Treinamento de Quedas"
echo "=============================================="
echo ""

# 1. Extrair frames
echo "📹 Passo 1/4: Extraindo frames dos vídeos..."
python3 datasets/quedas/extrair_frames.py
echo ""

# 2. Preparar dataset (se já anotado)
if [ -f "datasets/quedas/annotations/anotacoes.json" ]; then
    echo "📦 Passo 2/4: Preparando dataset..."
    python3 datasets/quedas/preparar_dataset.py
    echo ""
    
    # 3. Treinar
    echo "🎓 Passo 3/4: Treinando modelo..."
    echo "   Isso pode levar várias horas dependendo do hardware..."
    python3 datasets/quedas/treinar_modelo.py --epochs 100 --batch 16 --validar
    echo ""
    
    # 4. Resumo
    echo "✅ Passo 4/4: Treinamento completo!"
    echo ""
    echo "📊 Modelo salvo em: modelos/queda_custom.pt"
    echo "📁 Resultados em: modelos/queda_custom/"
    echo ""
    echo "💡 O sistema usará automaticamente o modelo customizado!"
else
    echo "⚠️  Anotações não encontradas!"
    echo ""
    echo "📝 Execute primeiro a anotação:"
    echo "   ./datasets/quedas/iniciar_anotacao.sh"
    echo ""
    echo "   Ou:"
    echo "   streamlit run datasets/quedas/anotar_quedas.py"
fi

