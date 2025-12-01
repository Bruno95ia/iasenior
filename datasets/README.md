# 📦 Sistema de Datasets para Treinamento YOLO - IASenior

## 📋 Visão Geral

Sistema completo para criar, anotar e treinar datasets YOLO customizados para os objetivos específicos da IASenior.

## 🎯 Objetivos do Dataset

O dataset foi projetado para treinar modelos YOLO capazes de detectar:

1. **pessoa** (Classe 0): Pessoa genérica
2. **pessoa_em_pe** (Classe 1): Pessoa em pé
3. **pessoa_caida** (Classe 2): Pessoa caída (prioritária para detecção de quedas)
4. **pessoa_sentada** (Classe 3): Pessoa sentada
5. **pessoa_no_banheiro** (Classe 4): Pessoa na área do banheiro

## 📁 Estrutura de Diretórios

```
datasets/
├── classes.yaml                    # Configuração de classes
├── README.md                       # Este arquivo
│
├── coletados/                      # Frames coletados do sistema
│   ├── images/                     # Imagens coletadas
│   ├── labels/                     # Labels (vazio até anotar)
│   └── metadata/                   # Metadados de coleta
│
├── anotados/                       # Dataset após anotação manual
│   ├── images/                     # Imagens anotadas
│   └── labels/                     # Labels YOLO (.txt)
│
├── treino/                         # Dataset preparado para treinamento
│   ├── train/                      # Treino (70%)
│   │   ├── images/
│   │   └── labels/
│   ├── validacao/                  # Validação (20%)
│   │   ├── images/
│   │   └── labels/
│   ├── teste/                      # Teste (10%)
│   │   ├── images/
│   │   └── labels/
│   ├── dataset.yaml                # Configuração YOLO
│   └── estatisticas.json           # Estatísticas do dataset
│
├── coletar_dados.py               # Script para coletar frames
├── anotar_dados.py                # Utilitário de anotação
├── preparar_dataset.py            # Preparação e validação
├── analisar_dataset.py            # Análise de dataset
└── treinar_modelo.py              # Treinamento YOLO
```

## 🚀 Workflow Completo

### 1. Coletar Dados do Sistema

Coleta frames do sistema em execução para criar dataset inicial.

```bash
# Coletar 100 frames a cada 5 segundos
python datasets/coletar_dados.py --quantidade 100 --intervalo 5

# Modo contínuo (coleta até interromper com Ctrl+C)
python datasets/coletar_dados.py --modo-continuo --intervalo 10
```

**O que faz:**
- Captura frames do sistema em execução
- Salva em `datasets/coletados/images/`
- Registra metadados (timestamp, status do sistema)
- Útil para criar dataset inicial rapidamente

---

### 2. Anotar Imagens

Anota imagens coletadas no formato YOLO.

```bash
# Anotar uma imagem específica
python datasets/anotar_dados.py datasets/coletados/images/frame_20250108_120000.jpg

# Ou com arquivo de classes customizado
python datasets/anotar_dados.py imagem.jpg --classes datasets/classes.yaml
```

**Como usar:**
1. Execute o script com caminho da imagem
2. Use teclas **0-4** para selecionar classe
3. **Clique e arraste** para criar bounding box
4. Pressione **s** para salvar
5. Pressione **d** para deletar última anotação
6. Pressione **q** para sair e salvar

**Formato YOLO gerado:**
```
class_id center_x center_y width height
0 0.5 0.5 0.3 0.4
```
Todos os valores são normalizados (0.0 a 1.0).

---

### 3. Organizar Dataset Anotado

Após anotar, organize as imagens anotadas:

```bash
# Copiar imagens anotadas para diretório anotados
cp datasets/coletados/images/* datasets/anotados/images/
cp datasets/coletados/labels/* datasets/anotados/labels/
```

---

### 4. Preparar Dataset para Treinamento

Valida anotações, divide em train/val/test e organiza estrutura:

```bash
# Preparar dataset (split padrão: 70/20/10)
python datasets/preparar_dataset.py \
    --anotados datasets/anotados \
    --saida datasets/treino \
    --classes datasets/classes.yaml

# Com proporções customizadas
python datasets/preparar_dataset.py \
    --anotados datasets/anotados \
    --saida datasets/treino \
    --treino 0.8 \
    --validacao 0.15 \
    --teste 0.05 \
    --seed 42
```

**O que faz:**
- ✅ Valida todas as anotações
- ✅ Remove anotações inválidas
- ✅ Divide dataset em train/val/test
- ✅ Organiza estrutura YOLO padrão
- ✅ Cria `dataset.yaml` para treinamento
- ✅ Gera estatísticas do dataset

---

### 5. Analisar Dataset

Analisa dataset preparado e gera relatório:

```bash
# Análise rápida
python datasets/analisar_dataset.py --dataset datasets/treino/dataset.yaml

# Análise e salvar relatório
python datasets/analisar_dataset.py \
    --dataset datasets/treino/dataset.yaml \
    --salvar
```

**Relatório inclui:**
- Total de imagens por split
- Distribuição de classes
- Resoluções encontradas
- Estatísticas de anotações

---

### 6. Treinar Modelo YOLO

Treina modelo customizado com dataset preparado:

```bash
# Treinamento básico
python datasets/treinar_modelo.py \
    --dataset datasets/treino/dataset.yaml \
    --modelo yolov8n.pt \
    --epochs 100

# Treinamento completo
python datasets/treinar_modelo.py \
    --dataset datasets/treino/dataset.yaml \
    --modelo yolov8s.pt \
    --epochs 200 \
    --img-size 640 \
    --batch 32 \
    --nome iasenior_modelo_final
```

**Modelos disponíveis:**
- `yolov8n.pt` - Nano (mais rápido, menor precisão)
- `yolov8s.pt` - Small (balanceado)
- `yolov8m.pt` - Medium (mais precisão)
- `yolov8l.pt` - Large (alta precisão)
- `yolov8x.pt` - Extra Large (máxima precisão)

**Output:**
- Modelo treinado: `runs/train/{nome}/weights/best.pt`
- Métricas e gráficos em `runs/train/{nome}/`

---

## 📊 Formato YOLO

### Arquivo de Labels (.txt)

Cada imagem deve ter um arquivo `.txt` correspondente com o mesmo nome.

**Formato:**
```
class_id center_x center_y width height
class_id center_x center_y width height
...
```

**Exemplo:**
```
0 0.5 0.5 0.3 0.4
2 0.2 0.7 0.25 0.3
```

**Onde:**
- `class_id`: ID da classe (0-4)
- `center_x, center_y`: Centro da bounding box (normalizado 0-1)
- `width, height`: Largura e altura da bounding box (normalizado 0-1)

### Conversão de Coordenadas

```python
# De coordenadas absolutas para YOLO:
center_x = ((x1 + x2) / 2) / image_width
center_y = ((y1 + y2) / 2) / image_height
width = (x2 - x1) / image_width
height = (y2 - y1) / image_height
```

---

## 📝 Configuração de Classes

Arquivo: `datasets/classes.yaml`

```yaml
nc: 5  # Número de classes

names:
  0: pessoa
  1: pessoa_em_pe
  2: pessoa_caida
  3: pessoa_sentada
  4: pessoa_no_banheiro
```

---

## 🎯 Boas Práticas

### Coleta de Dados

1. **Diversidade**: Colete frames em diferentes horários e situações
2. **Qualidade**: Use frames com boa iluminação e resolução
3. **Balanceamento**: Colete mais frames de situações importantes (quedas, banheiro)
4. **Metadados**: Mantenha metadados sobre cada coleta (status, hora, etc.)

### Anotação

1. **Precisão**: Seja preciso com bounding boxes
2. **Consistência**: Use mesma classe para situações similares
3. **Completude**: Anote todas as pessoas visíveis
4. **Validação**: Revise anotações periodicamente

### Treinamento

1. **Dataset balanceado**: Garanta distribuição equilibrada de classes
2. **Validação**: Use dataset de validação adequado
3. **Épocas**: Monitore overfitting (use early stopping)
4. **Augmentação**: YOLO já aplica data augmentation automaticamente

---

## 📈 Métricas Esperadas

### Dataset Mínimo Recomendado

- **Treino**: Mínimo 1000 imagens por classe
- **Validação**: 20% do dataset
- **Teste**: 10% do dataset
- **Balanceamento**: Todas as classes bem representadas

### Performance do Modelo

- **mAP50**: > 0.7 (boa precisão)
- **mAP50-95**: > 0.5 (excelente)
- **Precision**: > 0.8
- **Recall**: > 0.8

---

## 🔧 Troubleshooting

### Erro: "Nenhuma anotação válida encontrada"

- Verifique se arquivos `.txt` existem para cada imagem
- Confirme formato YOLO correto (5 valores por linha)
- Valide coordenadas normalizadas (0-1)

### Erro: "Classes não encontradas"

- Verifique arquivo `classes.yaml`
- Confirme número de classes correto
- Valide IDs das classes (devem começar em 0)

### Performance ruim após treinamento

- Aumente tamanho do dataset
- Balance melhor as classes
- Ajuste hyperparâmetros
- Considere fine-tuning de modelo pré-treinado maior

---

## 🚀 Pipeline Completo

```bash
# 1. Coletar dados
python datasets/coletar_dados.py --quantidade 500 --intervalo 5

# 2. Anotar imagens (manual)
python datasets/anotar_dados.py datasets/coletados/images/frame_001.jpg

# 3. Organizar anotados
cp datasets/coletados/images/* datasets/anotados/images/
cp datasets/coletados/labels/* datasets/anotados/labels/

# 4. Preparar dataset
python datasets/preparar_dataset.py --anotados datasets/anotados --saida datasets/treino

# 5. Analisar dataset
python datasets/analisar_dataset.py --dataset datasets/treino/dataset.yaml --salvar

# 6. Treinar modelo
python datasets/treinar_modelo.py --dataset datasets/treino/dataset.yaml --epochs 100

# 7. Usar modelo treinado
# Atualizar config.py: MODEL_PATH = "runs/train/iasenior_customizado/weights/best.pt"
```

---

## 📚 Referências

- [Documentação Ultralytics YOLO](https://docs.ultralytics.com/)
- [Formato YOLO Dataset](https://github.com/ultralytics/ultralytics)
- [Treinamento Customizado YOLO](https://docs.ultralytics.com/modes/train/)

---

**Versão**: 1.0.0  
**Empresa**: IASenior  
**Data**: 2025-01

