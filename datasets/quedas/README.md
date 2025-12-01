# 🎯 Pipeline de Treinamento de Detecção de Quedas

Sistema completo para treinar modelo YOLOv8 customizado para detecção de quedas.

## 📋 Passo a Passo

### 1. Extrair Frames dos Vídeos

```bash
cd datasets/quedas
python3 extrair_frames.py
```

Isso vai:
- Extrair frames de todos os vídeos em `videos/`
- Salvar frames em `frames/`
- Criar índice `frames_index.json`

### 2. Anotar Frames

**Escolha o método mais rápido para você:**

#### 🚀 Opção 1: Anotação Rápida (Recomendado para velocidade)
```bash
streamlit run anotar_rapido.py
```
- ⚡ Modo turbo com atalhos
- 🤖 Detecção automática de pessoas
- 📋 Reutiliza última bbox
- ⌨️ Atalhos de teclado (setas, espaço, Q)

#### 🤖 Opção 2: Anotação Inteligente (Recomendado para precisão)
```bash
streamlit run anotar_quedas_inteligente.py
```
- 🤖 IA detecta pessoas automaticamente
- ✅ Sugestões de bounding boxes
- 📋 Propagação automática para frames próximos
- 🔍 Filtro para mostrar apenas frames com pessoas

#### 🎬 Opção 3: Anotação por Vídeo (Mais rápido para muitos frames)
```bash
streamlit run anotar_por_video.py
```
- ⏱️ Marque início/fim das quedas no vídeo
- 📊 Timeline visual interativa
- 🎯 Gera anotações automaticamente para todos os frames do intervalo
- ⚡ Muito mais rápido para vídeos longos

#### 📝 Opção 4: Anotação Manual (Original)
```bash
streamlit run anotar_quedas.py
```
- Interface completa com todas as opções
- Controle total sobre cada frame

### 3. Preparar Dataset

```bash
python3 preparar_dataset.py
```

Isso vai:
- Dividir dataset em train/val/test (70%/20%/10%)
- Organizar em formato YOLO
- Criar arquivo `dataset.yaml`

### 4. Treinar Modelo

```bash
python3 treinar_modelo.py --epochs 100 --batch 16
```

Opções:
- `--epochs`: Número de épocas (default: 100)
- `--batch`: Batch size (default: 16)
- `--imgsz`: Tamanho da imagem (default: 640)
- `--device`: Device (cpu/cuda/mps, default: auto)
- `--validar`: Validar após treinamento

### 5. Testar Modelo

```bash
python3 inferencia_quedas.py videos/Queda_qt1.mp4 --modelo modelos/queda_custom.pt
```

## 📁 Estrutura de Pastas

```
quedas/
├── videos/              # Vídeos originais (você colocou aqui)
├── frames/              # Frames extraídos
│   └── frames_index.json
├── annotations/         # Anotações
│   ├── images/         # Imagens anotadas
│   ├── labels/         # Labels YOLO (.txt)
│   └── anotacoes.json  # JSON com anotações
├── dataset_yolo/        # Dataset preparado
│   ├── train/
│   ├── val/
│   ├── test/
│   └── dataset.yaml    # Config YOLO
└── modelos_treinados/   # Modelos treinados
    └── queda_custom.pt
```

## 🎯 Integração com Sistema Principal

Após treinar, o modelo será usado automaticamente pelo sistema se estiver em:
```
modelos/queda_custom.pt
```

O sistema detecta automaticamente e usa o modelo customizado se disponível.

## 📊 Métricas Esperadas

Após treinamento, você verá:
- **mAP50**: Precisão média (objetivo: >0.8)
- **mAP50-95**: Precisão média em múltiplos IoU
- **Precision**: Precisão (objetivo: >0.85)
- **Recall**: Recall (objetivo: >0.80)

## 🔧 Troubleshooting

### Erro: "Nenhum frame encontrado"
Execute primeiro: `python3 extrair_frames.py`

### Erro: "Nenhuma imagem encontrada"
Execute: `streamlit run anotar_quedas.py` e anote alguns frames

### Modelo não melhora
- Aumente número de épocas
- Aumente batch size (se tiver GPU)
- Adicione mais dados de treinamento
- Verifique qualidade das anotações

### GPU não detectada
- Verifique instalação do PyTorch com CUDA
- Use `--device cpu` para forçar CPU

## 💡 Dicas

1. **Anote bem**: Quanto melhor as anotações, melhor o modelo
2. **Diversidade**: Anote quedas de diferentes ângulos e situações
3. **Negativos**: Anote também frames SEM quedas (importante!)
4. **Validação**: Teste em vídeos diferentes dos de treino

