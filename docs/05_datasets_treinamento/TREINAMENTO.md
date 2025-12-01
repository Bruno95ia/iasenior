# 🎯 Guia Completo de Treinamento de Detecção de Quedas

Sistema completo para treinar modelo YOLOv8 customizado usando seus próprios vídeos.

## ✅ Status Atual

- ✅ **963 frames extraídos** dos 8 vídeos
- ✅ Sistema de anotação criado
- ✅ Pipeline de treinamento pronto
- ✅ Integração com sistema principal

## 🚀 Passo a Passo Rápido

### 1. Anotar Frames (OBRIGATÓRIO)

**🎯 Escolha o método mais rápido para você:**

#### ⚡ Método Rápido (Recomendado - Mais Veloz)
```bash
streamlit run datasets/quedas/anotar_rapido.py
```
- ⚡ Modo turbo: 2-3 segundos por frame
- 🤖 Detecção automática de pessoas
- 📋 Reutiliza última bbox
- ⌨️ Atalhos: Setas (navegar), Espaço (próximo), Q (marcar queda)
- **Velocidade: ~200-300 frames/hora**

#### 🤖 Método Inteligente (Recomendado - Mais Preciso)
```bash
streamlit run datasets/quedas/anotar_quedas_inteligente.py
```
- 🤖 IA detecta pessoas e sugere bboxes automaticamente
- ✅ Botão "Usar Sugestão" com 1 clique
- 📋 Propagação automática para frames próximos
- 🔍 Filtro para mostrar só frames com pessoas
- **Velocidade: ~100-150 frames/hora**

#### 🎬 Método por Vídeo (Mais Rápido para Vídeos Longos)
```bash
streamlit run datasets/quedas/anotar_por_video.py
```
- ⏱️ Marque início/fim das quedas no vídeo (não frame a frame!)
- 📊 Timeline visual interativa
- 🎯 Gera anotações automaticamente para todos os frames do intervalo
- **Velocidade: ~10-20 quedas/hora (mas cada queda = muitos frames!)**
- **Exemplo:** 3 intervalos = 300 frames anotados em minutos!

#### 📝 Método Manual (Original)
```bash
streamlit run datasets/quedas/anotar_quedas.py
```
- Interface completa com todas as opções
- Controle total sobre cada frame

**💡 Dica:** Use o script interativo para escolher:
```bash
./datasets/quedas/iniciar_anotacao.sh
```

**📚 Veja [ESCOLHER_METODO.md](datasets/quedas/ESCOLHER_METODO.md) para comparar métodos**

### 2. Preparar Dataset

```bash
cd datasets/quedas
python3 preparar_dataset.py
```

Isso divide em:
- **70% treino** (para aprender)
- **20% validação** (para ajustar)
- **10% teste** (para avaliar)

### 3. Treinar Modelo

```bash
# Opção 1: Script completo (recomendado)
./datasets/quedas/treinar_completo.sh

# Opção 2: Manual
cd datasets/quedas
python3 treinar_modelo.py --epochs 100 --batch 16 --validar
```

**Parâmetros:**
- `--epochs 100`: Número de épocas (mais = melhor, mas demora mais)
- `--batch 16`: Batch size (aumente se tiver GPU)
- `--device cuda`: Forçar GPU (se disponível)
- `--validar`: Validar após treinamento

**Tempo estimado:**
- CPU: 4-8 horas
- GPU: 30-60 minutos

### 4. Usar Modelo Treinado

O sistema detecta automaticamente o modelo em `modelos/queda_custom.pt` e usa ele!

## 📊 Estrutura de Arquivos

```
datasets/quedas/
├── videos/                    # ✅ Seus 8 vídeos aqui
├── frames/                    # ✅ 963 frames extraídos
│   └── frames_index.json
├── annotations/               # 📝 Anotações (criar aqui)
│   ├── images/              # Imagens anotadas
│   ├── labels/              # Labels YOLO (.txt)
│   └── anotacoes.json       # JSON com anotações
├── dataset_yolo/            # 📦 Dataset preparado
│   ├── train/
│   ├── val/
│   ├── test/
│   └── dataset.yaml
└── modelos_treinados/        # 🎓 Modelo treinado
    └── queda_custom.pt
```

## 🎯 Dicas de Anotação

### Boas Práticas

1. **Anote bem as bounding boxes**
   - Inclua toda a pessoa caída
   - Não corte partes importantes
   - Seja consistente

2. **Diversidade é importante**
   - Diferentes ângulos
   - Diferentes iluminações
   - Diferentes tipos de queda

3. **Anote também negativos**
   - Frames SEM quedas são importantes
   - Marque "Tem queda" = false nesses casos

4. **Qualidade > Quantidade**
   - 50 frames bem anotados > 200 mal anotados
   - Foque em qualidade primeiro

### Exemplo de Bounding Box

```
┌─────────────────┐
│                 │
│   ┌───────┐     │  ← Bounding box deve incluir
│   │ QUEDA │     │     toda a pessoa caída
│   └───────┘     │
│                 │
└─────────────────┘
```

## 📈 Métricas Esperadas

Após treinamento, você verá:

- **mAP50**: Precisão média (objetivo: >0.80)
- **mAP50-95**: Precisão em múltiplos IoU (objetivo: >0.60)
- **Precision**: Precisão (objetivo: >0.85)
- **Recall**: Recall (objetivo: >0.80)

### Interpretação

- **mAP50 > 0.8**: Modelo muito bom! ✅
- **mAP50 0.6-0.8**: Modelo bom, pode melhorar
- **mAP50 < 0.6**: Precisa mais dados/treinamento

## 🔧 Troubleshooting

### "Nenhum frame encontrado"
```bash
cd datasets/quedas
python3 extrair_frames.py
```

### "Nenhuma imagem encontrada"
Execute a anotação primeiro:
```bash
streamlit run datasets/quedas/anotar_quedas.py
```

### Modelo não melhora

1. **Adicione mais dados**
   - Mais vídeos de quedas
   - Mais anotações

2. **Melhore anotações**
   - Verifique qualidade das bounding boxes
   - Anote mais frames negativos

3. **Ajuste parâmetros**
   - Aumente épocas: `--epochs 200`
   - Aumente batch: `--batch 32` (se tiver GPU)

### GPU não detectada

```bash
# Verificar PyTorch
python3 -c "import torch; print(torch.cuda.is_available())"

# Forçar CPU
python3 treinar_modelo.py --device cpu
```

## 🚀 Próximos Passos Após Treinamento

1. **Testar em vídeos novos**
   ```bash
   python3 datasets/quedas/inferencia_quedas.py videos/novo_video.mp4
   ```

2. **Integração automática**
   - Modelo em `modelos/queda_custom.pt` é usado automaticamente
   - Sistema detecta e usa modelo customizado

3. **Melhorar continuamente**
   - Adicione mais vídeos
   - Re-treine com mais dados
   - Ajuste thresholds

## 💡 Dicas Avançadas

### Transfer Learning

O modelo usa YOLOv8n como base (já treinado em milhões de imagens). Isso acelera muito o treinamento!

### Data Augmentation

YOLO aplica automaticamente:
- Rotação
- Flip
- Mudança de brilho
- Zoom

### Fine-tuning

Após treinar, você pode:
- Ajustar confidence threshold
- Treinar mais épocas
- Usar modelo maior (yolov8s.pt, yolov8m.pt)

## 📚 Recursos

- [Documentação YOLOv8](https://docs.ultralytics.com/)
- [Formato YOLO](https://docs.ultralytics.com/datasets/)
- [Guia de Treinamento](https://docs.ultralytics.com/modes/train/)

---

**Pronto para começar? Execute:**
```bash
./datasets/quedas/iniciar_anotacao.sh
```

