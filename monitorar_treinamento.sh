#!/bin/bash
# Script para monitorar progresso do treinamento

echo "📊 Monitorando Treinamento YOLO"
echo "================================"
echo ""

while true; do
    clear
    echo "📊 Status do Treinamento - $(date '+%H:%M:%S')"
    echo "================================"
    echo ""
    
    # Verificar se processo está rodando
    if ps aux | grep -E "treinar_modelo.*mps" | grep -v grep > /dev/null; then
        echo "✅ Treinamento: RODANDO"
    else
        echo "⏸️  Treinamento: PARADO"
    fi
    
    echo ""
    
    # Mostrar última época
    if [ -f "modelos/queda_custom/results.csv" ]; then
        echo "📈 Última Época:"
        tail -1 modelos/queda_custom/results.csv | awk -F',' '{printf "   Época: %s\n   Tempo: %.1f minutos\n   mAP50: %.4f\n   mAP50-95: %.4f\n", $1, $2/60, $8, $9}'
    else
        echo "⏳ Aguardando resultados..."
    fi
    
    echo ""
    echo "💾 Modelos salvos:"
    ls -lh modelos/queda_custom/weights/*.pt 2>/dev/null | awk '{printf "   %s (%s)\n", $9, $5}'
    
    echo ""
    echo "⏱️  Atualizando a cada 5 segundos... (Ctrl+C para sair)"
    sleep 5
done
