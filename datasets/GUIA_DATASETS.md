# 📘 Guia Completo de Datasets - IASenior

## 🎯 Visão Geral

Este guia completo explica como criar, anotar e treinar datasets YOLO customizados para os objetivos específicos da IASenior.

## 📚 Classes Definidas

### Classes para Detecção Específica

O sistema usa 5 classes específicas para os objetivos da IASenior:

| ID | Classe | Descrição | Uso Principal |
|----|--------|-----------|---------------|
| 0 | `pessoa` | Pessoa genérica | Detecção geral quando postura não é certa |
| 1 | `pessoa_em_pe` | Pessoa em pé | Diferenciação de postura |
| 2 | `pessoa_caida` | Pessoa caída | **PRIORITÁRIA** - Detecção de quedas |
| 3 | `pessoa_sentada` | Pessoa sentada | Diferenciação de postura |
| 4 | `pessoa_no_banheiro` | Pessoa no banheiro | Monitoramento contextual |

### Por que essas classes?

1. **Classe 2 (pessoa_caida)**: Essencial para detecção de quedas
2. **Classes 1 e 3**: Reduzem falsos positivos diferenciando posturas
3. **Classe 4**: Permite treinar modelo para contexto específico
4. **Classe 0**: Fallback quando não há certeza da postura

## 🔄 Workflow Completo

```
1. COLETAR DADOS
   └─> Frames do sistema em execução
   
2. ANOTAR MANUALMENTE
   └─> Criar bounding boxes no formato YOLO
   
3. VALIDAR ANOTAÇÕES
   └─> Verificar formato e consistência
   
4. PREPARAR DATASET
   └─> Split train/val/test
   
5. ANALISAR DATASET
   └─> Verificar balanceamento e qualidade
   
6. TREINAR MODELO
   └─> Treinar YOLO customizado
   
7. AVALIAR MODELO
   └─> Testar e validar performance
   
8. DEPLOY
   └─> Usar modelo treinado no sistema
```

## 📝 Passo a Passo Detalhado

### Passo 1: Coletar Dados do Sistema

**Objetivo**: Capturar frames do sistema em execução

```bash
# Coletar 200 frames a cada 5 segundos
python datasets/coletar_dados.py --quantidade 200 --intervalo 5

# Modo contínuo (até interromper com Ctrl+C)
python datasets/coletar_dados.py --modo-continuo --intervalo 10
```

**Onde estão os dados?**
- `datasets/coletados/images/` - Imagens coletadas
- `datasets/coletados/metadata/` - Metadados (timestamp, status)

**Dicas**:
- ✅ Colete em diferentes horários e situações
- ✅ Foque em coletar mais frames de quedas e banheiro
- ✅ Mantenha boa qualidade de imagem
- ✅ Registre status do sistema quando coletar

---

### Passo 2: Anotar Imagens

**Objetivo**: Criar bounding boxes e labels no formato YOLO

```bash
# Anotar uma imagem específica
python datasets/anotar_dados.py datasets/coletados/images/frame_20250108_120000.jpg
```

**Interface de Anotação**:

1. **Selecionar Classe**: Use teclas `0-4`
   - `0`: pessoa
   - `1`: pessoa_em_pe
   - `2`: pessoa_caida ⭐ (mais importante)
   - `3`: pessoa_sentada
   - `4`: pessoa_no_banheiro

2. **Criar Bounding Box**:
   - Clique e arraste para desenhar retângulo
   - O retângulo aparece conforme arrasta
   - Solte para confirmar

3. **Ações**:
   - `s`: Salvar anotações
   - `d`: Deletar última anotação
   - `q`: Sair e salvar

**Formato Gerado** (`frame_001.txt`):
```
0 0.5 0.5 0.3 0.4
2 0.2 0.7 0.25 0.3
```

**Onde estão os labels?**
- `datasets/coletados/labels/` - Labels YOLO gerados

---

### Passo 3: Validar Anotações

**Objetivo**: Verificar se anotações estão corretas

```bash
# Validar anotações
python datasets/validar_anotacoes.py \
    --images datasets/coletados/images \
    --labels datasets/coletados/labels \
    --classes datasets/classes.yaml \
    --salvar
```

**O que valida:**
- ✅ Formato YOLO correto (5 valores por linha)
- ✅ Classes válidas (0-4)
- ✅ Coordenadas normalizadas (0-1)
- ✅ Tamanho mínimo de bounding boxes
- ✅ Correspondência imagem-label

**Output**:
- Relatório de validação
- Lista de problemas encontrados
- Estatísticas de classes

---

### Passo 4: Organizar Dataset Anotado

**Objetivo**: Copiar imagens e labels anotados para diretório organizado

```bash
# Copiar imagens anotadas
cp datasets/coletados/images/*.jpg datasets/anotados/images/
cp datasets/coletados/labels/*.txt datasets/anotados/labels/
```

**Estrutura Resultante:**
```
datasets/anotados/
├── images/
│   ├── frame_001.jpg
│   ├── frame_002.jpg
│   └── ...
└── labels/
    ├── frame_001.txt
    ├── frame_002.txt
    └── ...
```

---

### Passo 5: Preparar Dataset para Treinamento

**Objetivo**: Validar, dividir e organizar dataset final

```bash
# Preparar com split padrão (70/20/10)
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
1. ✅ Valida todas as anotações
2. ✅ Remove anotações inválidas
3. ✅ Divide em train/val/test
4. ✅ Organiza estrutura YOLO padrão
5. ✅ Cria `dataset.yaml` para treinamento
6. ✅ Gera estatísticas do dataset

**Estrutura Gerada:**
```
datasets/treino/
├── train/
│   ├── images/
│   └── labels/
├── validacao/
│   ├── images/
│   └── labels/
├── teste/
│   ├── images/
│   └── labels/
├── dataset.yaml          # Configuração YOLO
└── estatisticas.json     # Estatísticas
```

---

### Passo 6: Analisar Dataset

**Objetivo**: Verificar qualidade e balanceamento do dataset

```bash
# Análise rápida
python datasets/analisar_dataset.py --dataset datasets/treino/dataset.yaml

# Análise e salvar relatório
python datasets/analisar_dataset.py \
    --dataset datasets/treino/dataset.yaml \
    --salvar
```

**Relatório Inclui:**
- Total de imagens por split
- Distribuição de classes
- Resoluções encontradas
- Tamanho médio dos arquivos
- Anotações por imagem

**Exemplo de Output:**
```
📊 RELATÓRIO DE ANÁLISE DE DATASET
============================================

📁 Split: TRAIN
   Total de imagens: 700
   Total de anotações: 2100
   Distribuição de classes:
     pessoa: 500 (23.8%)
     pessoa_caida: 300 (14.3%)
     pessoa_em_pe: 800 (38.1%)
     ...
```

---

### Passo 7: Treinar Modelo YOLO

**Objetivo**: Treinar modelo customizado com dataset preparado

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

**Modelos Disponíveis:**

| Modelo | Tamanho | Velocidade | Precisão | Uso |
|--------|---------|------------|----------|-----|
| yolov8n.pt | Nano | ⚡⚡⚡ | ⭐ | Prototipagem rápida |
| yolov8s.pt | Small | ⚡⚡ | ⭐⭐ | **Recomendado** |
| yolov8m.pt | Medium | ⚡ | ⭐⭐⭐ | Produção |
| yolov8l.pt | Large | 🐌 | ⭐⭐⭐⭐ | Alta precisão |
| yolov8x.pt | Extra | 🐌🐌 | ⭐⭐⭐⭐⭐ | Máxima precisão |

**Output do Treinamento:**
- Modelo treinado: `runs/train/{nome}/weights/best.pt`
- Gráficos de métricas
- Curvas de aprendizado
- Resultados de validação

**Métricas Monitoradas:**
- **mAP50**: Mean Average Precision @ 0.5 IoU
- **mAP50-95**: mAP @ 0.5:0.95 IoU
- **Precision**: Precisão das detecções
- **Recall**: Recall das detecções

---

### Passo 8: Usar Modelo Treinado

**Objetivo**: Integrar modelo treinado ao sistema

```bash
# Atualizar config.py
MODEL_PATH = "runs/train/iasenior_modelo_final/weights/best.pt"

# Ou via variável de ambiente
export MODEL_PATH="runs/train/iasenior_modelo_final/weights/best.pt"
```

---

## 📊 Exemplo de Dataset Mínimo

### Recomendações de Tamanho

| Classe | Mínimo | Recomendado | Ideal |
|--------|--------|-------------|-------|
| pessoa | 200 | 500 | 1000+ |
| pessoa_em_pe | 200 | 500 | 1000+ |
| **pessoa_caida** | **300** | **800** | **1500+** |
| pessoa_sentada | 200 | 500 | 1000+ |
| pessoa_no_banheiro | 150 | 400 | 800+ |
| **TOTAL** | **1050** | **2700** | **5300+** |

**Nota**: Classe 2 (pessoa_caida) é prioridade - colete mais exemplos!

---

## 🎯 Estratégias de Coleta

### 1. Coleta Automática com Filtros

Coletar frames quando eventos específicos ocorrem:

```python
# Coletar quando queda detectada
if status == "queda":
    coletar_frame_com_status("queda")

# Coletar quando banheiro tem pessoa
if pessoa_banheiro:
    coletar_frame_com_status("banheiro")
```

### 2. Coleta Manual Estratégica

Coletar manualmente em situações específicas:
- Simular quedas em ambiente controlado
- Diversas posturas (em pé, sentado, deitado)
- Diferentes iluminações
- Diferentes ângulos

### 3. Balanceamento de Classes

Após coletar, verificar distribuição:
- Se classe 2 (pessoa_caida) estiver sub-representada → coletar mais
- Se outras classes dominarem → coletar mais exemplos raros
- Ideal: distribuição equilibrada

---

## 💡 Dicas de Anotação

### Boas Práticas

1. **Precisão**: Seja preciso com bounding boxes
   - Inclua pessoa completa quando possível
   - Evite cortar partes importantes

2. **Consistência**: 
   - Use mesma classe para situações similares
   - Seja consistente com decisões de fronteira

3. **Classe 2 (pessoa_caida)**:
   - Use quando pessoa está claramente no chão
   - Pessoa horizontal (aspect_ratio < 0.7)
   - Na parte inferior da imagem

4. **Classe 4 (pessoa_no_banheiro)**:
   - Use quando pessoa está na área do banheiro
   - Importante para contexto específico

### Quando Usar Cada Classe

- **Classe 0 (pessoa)**: Quando não há certeza da postura
- **Classe 1 (pessoa_em_pe)**: Pessoa vertical, em pé
- **Classe 2 (pessoa_caida)**: Pessoa horizontal no chão ⭐
- **Classe 3 (pessoa_sentada)**: Pessoa sentada em cadeira/cama
- **Classe 4 (pessoa_no_banheiro)**: Pessoa na área do banheiro

---

## 📈 Qualidade do Dataset

### Checklist de Qualidade

- ✅ **Tamanho**: Mínimo 1000 imagens por classe
- ✅ **Balanceamento**: Todas as classes bem representadas
- ✅ **Diversidade**: Diferentes situações, horários, iluminações
- ✅ **Anotação**: Todas as anotações validadas
- ✅ **Formato**: Formato YOLO correto
- ✅ **Split**: Train/Val/Test bem dividido

### Métricas de Qualidade

- **Distribuição de classes**: Balanceada (±20% entre classes)
- **Anotações por imagem**: Média de 1-3 por imagem
- **Tamanho de bounding boxes**: Variado (pessoas próximas e distantes)
- **Resolução**: Consistente ou bem distribuída

---

## 🔧 Troubleshooting

### Problema: Dataset muito pequeno

**Solução**:
- Colete mais dados
- Use data augmentation (YOLO já faz automaticamente)
- Considere fine-tuning de modelo pré-treinado

### Problema: Classe desbalanceada

**Solução**:
- Colete mais exemplos da classe minoritária
- Use class weights no treinamento
- Aplique oversampling na classe rara

### Problema: Modelo não detecta quedas bem

**Solução**:
- Aumente exemplos de classe 2 (pessoa_caida)
- Verifique qualidade das anotações
- Treine mais épocas
- Considere modelo maior (yolov8m ou yolov8l)

---

## 📚 Recursos Adicionais

### Scripts Disponíveis

1. **coletar_dados.py**: Coleta frames do sistema
2. **anotar_dados.py**: Interface de anotação manual
3. **validar_anotacoes.py**: Valida formato e consistência
4. **preparar_dataset.py**: Prepara dataset para treinamento
5. **analisar_dataset.py**: Analisa qualidade do dataset
6. **treinar_modelo.py**: Treina modelo YOLO customizado

### Arquivos de Configuração

- **classes.yaml**: Define classes do dataset
- **dataset.yaml**: Configuração YOLO (gerado automaticamente)

---

**Versão**: 1.0.0  
**Empresa**: IASenior  
**Data**: 2025-01

