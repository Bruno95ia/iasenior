# 🔍 Guia de Detecção de Quedas - Modelo Customizado

## ⚠️ Importante: Threshold Baixo Necessário

O modelo customizado foi treinado com dataset pequeno (234 imagens) e detecta quedas com **confiança baixa** (1-10%). 

**Use threshold baixo: 0.01 a 0.1**

## 🎯 Como Usar

### Teste Básico
```bash
cd datasets/quedas
./testar_inferencia.sh videos/Queda_qt1.mp4
```

### Com Threshold Customizado
```bash
# Mais detecções (pode ter falsos positivos)
./testar_inferencia.sh videos/Queda_qt1.mp4 --conf 0.01

# Menos detecções (mais preciso)
./testar_inferencia.sh videos/Queda_qt1.mp4 --conf 0.1
```

### Teste Detalhado (Recomendado)
```bash
# Testa múltiplos thresholds e mostra estatísticas
python3 testar_deteccoes_detalhado.py videos/Queda_qt1.mp4
```

## 📊 Por que Threshold Baixo?

O modelo detecta quedas, mas com confiança entre **1-10%**:
- Frame 0: confiança 9.5%
- Frame 1: confiança 2.7%
- Frame 2: confiança 1.5%

Isso acontece porque:
1. **Dataset pequeno**: Apenas 234 imagens de treino
2. **Validação mínima**: Apenas 2 imagens de validação
3. **Modelo precisa mais treino**: Mais épocas ou mais dados

## 🔧 Melhorias Recomendadas

### 1. Re-treinar com Mais Dados
- Adicione mais vídeos de quedas
- Anote mais frames
- Ideal: 1000+ imagens de treino

### 2. Ajustar Threshold Dinamicamente
O sistema pode usar threshold adaptativo baseado no contexto.

### 3. Usar Modelo Maior
- `yolov8s.pt` ao invés de `yolov8n.pt`
- Mais parâmetros = melhor aprendizado

## ✅ Status Atual

- ✅ Modelo detecta quedas
- ⚠️ Confiança baixa (1-10%)
- ✅ Funciona com threshold 0.01-0.1
- ⚠️ Pode ter falsos positivos com threshold muito baixo

## 💡 Dica

Para produção, combine:
1. **Threshold baixo** (0.01-0.05) para detectar
2. **Filtro temporal** (vários frames consecutivos)
3. **Validação adicional** (tamanho, posição, etc.)

