# 🏋️ Guia de Monitoramento do Treinamento

## Status Atual

O treinamento está rodando em background. Use os scripts abaixo para monitorar.

## 📊 Scripts de Monitoramento

### 1. Verificação Rápida
```bash
./verificar_treinamento.sh
```
Mostra status atual, última época e métricas.

### 2. Monitoramento Contínuo (com notificação)
```bash
./monitorar_treinamento_completo.sh
```
Monitora continuamente e notifica quando terminar.

### 3. Logs em Tempo Real
```bash
tail -f /tmp/treinamento_continuado.log
```

## 📈 Verificar Progresso Manualmente

```bash
# Última época e métricas
tail -1 modelos/queda_custom/results.csv

# Ver todas as épocas
cat modelos/queda_custom/results.csv

# Verificar processo
ps aux | grep treinar_modelo
```

## 🎯 Informações do Treinamento

- **Épocas totais**: 50
- **Device**: MPS (Apple Silicon GPU)
- **Batch size**: 8
- **Checkpoint**: Continuando de `last.pt`
- **Early stopping**: patience=20

## ⏱️ Estimativa

- **Tempo por época**: ~2-3 minutos
- **Tempo restante**: ~60-90 minutos (dependendo do progresso atual)

## ✅ Quando Terminar

O modelo final será salvo em:
- `modelos/queda_custom.pt` (modelo final)
- `modelos/queda_custom/weights/best.pt` (melhor modelo durante treinamento)
- `modelos/queda_custom/weights/last.pt` (último checkpoint)

## 🔧 Comandos Úteis

```bash
# Parar treinamento (se necessário)
pkill -f treinar_modelo

# Continuar treinamento manualmente
cd datasets/quedas
source ../../venv/bin/activate
python3 treinar_modelo.py --epochs 50 --batch 8 --device mps --resume last.pt

# Ver métricas finais
tail -1 modelos/queda_custom/results.csv | awk -F',' '{print "mAP50:", $8, "| mAP50-95:", $9}'
```

