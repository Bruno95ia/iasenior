#!/bin/bash
# Script rápido para verificar status do treinamento

echo "📊 Status do Treinamento"
echo "========================"
echo ""

# Verificar processo
if ps aux | grep "treinar_modelo" | grep -v grep > /dev/null; then
    echo "✅ Treinamento: RODANDO"
    ps aux | grep "treinar_modelo" | grep -v grep | awk '{printf "   PID: %s | CPU: %s%% | Mem: %s%%\n", $2, $3, $4}'
else
    echo "⏸️  Treinamento: PARADO"
fi

echo ""

# Última época
if [ -f "modelos/queda_custom/results.csv" ]; then
    echo "📈 Progresso:"
    tail -1 modelos/queda_custom/results.csv | awk -F',' '{printf "   Época: %s/50\n   Tempo total: %.1f minutos\n   mAP50: %.4f\n   mAP50-95: %.4f\n", $1, $2/60, $8, $9}'
else
    echo "⏳ Aguardando resultados..."
fi

echo ""

# Modelos
echo "💾 Modelos:"
ls -lh modelos/queda_custom/weights/*.pt 2>/dev/null | awk '{printf "   %s (%s) - %s\n", $9, $5, $6" "$7" "$8}'

echo ""
echo "💡 Para monitorar em tempo real: tail -f /tmp/treinamento_continuado.log"

