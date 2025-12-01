#!/bin/bash
# Script para monitorar treinamento e notificar quando terminar

echo "🔍 Monitorando Treinamento YOLO"
echo "================================"
echo ""

ULTIMA_EPOCA=0
CHECK_INTERVAL=30  # Verificar a cada 30 segundos
MAX_EPOCAS=50

while true; do
    # Verificar se processo está rodando
    if ! ps aux | grep "treinar_modelo" | grep -v grep > /dev/null; then
        echo ""
        echo "✅ Treinamento CONCLUÍDO ou PARADO!"
        echo ""
        
        # Verificar se modelo final foi criado
        if [ -f "modelos/queda_custom.pt" ]; then
            echo "🎉 Modelo final criado: modelos/queda_custom.pt"
            ls -lh modelos/queda_custom.pt
        fi
        
        # Mostrar última época
        if [ -f "modelos/queda_custom/results.csv" ]; then
            echo ""
            echo "📊 Resultado Final:"
            tail -1 modelos/queda_custom/results.csv | awk -F',' '{
                printf "   Época: %s\n", $1
                printf "   Tempo total: %.1f minutos\n", $2/60
                printf "   mAP50: %.4f\n", $8
                printf "   mAP50-95: %.4f\n", $9
                printf "   Precision: %.4f\n", $6
                printf "   Recall: %.4f\n", $7
            }'
        fi
        
        # Notificação no macOS
        osascript -e 'display notification "Treinamento YOLO concluído!" with title "IASenior" sound name "Glass"' 2>/dev/null || true
        
        break
    fi
    
    # Verificar progresso
    if [ -f "modelos/queda_custom/results.csv" ]; then
        EPOCA_ATUAL=$(tail -1 modelos/queda_custom/results.csv | cut -d',' -f1)
        
        if [ "$EPOCA_ATUAL" != "$ULTIMA_EPOCA" ] && [ ! -z "$EPOCA_ATUAL" ]; then
            ULTIMA_EPOCA=$EPOCA_ATUAL
            PROGRESSO=$((EPOCA_ATUAL * 100 / MAX_EPOCAS))
            
            echo "[$(date '+%H:%M:%S')] 📊 Época $EPOCA_ATUAL/$MAX_EPOCAS ($PROGRESSO%)"
            
            # Mostrar métricas
            tail -1 modelos/queda_custom/results.csv | awk -F',' '{
                printf "   mAP50: %.4f | mAP50-95: %.4f | Tempo: %.1f min\n", $8, $9, $2/60
            }'
        fi
    fi
    
    sleep $CHECK_INTERVAL
done

echo ""
echo "✅ Monitoramento finalizado!"

