# 📦 Guia Completo para Criar Datasets Específicos do Sistema

## 🎯 Visão Geral

Este guia explica como buscar, coletar e criar datasets específicos para o sistema IASenior, focando em detecção de pessoas, quedas e posturas.

## 🚀 Scripts Criados

### 1. `buscar_datasets_publicos.py`
Busca e lista datasets públicos disponíveis na internet.

**Uso:**
```bash
# Listar datasets disponíveis
python datasets/buscar_datasets_publicos.py --listar

# Criar estrutura para dataset público
python datasets/buscar_datasets_publicos.py --criar-estrutura nome_dataset
```

**Funcionalidades:**
- Lista datasets públicos relevantes
- Gera lista de fontes (salva em `datasets/publicos/FONTES_DATASETS.md`)
- Cria estrutura de diretórios para datasets públicos

### 2. `coletar_dados_especificos.py`
Coleta dados específicos baseado em eventos do sistema.

**Uso:**
```bash
# Coletar frame de evento específico
python datasets/coletar_dados_especificos.py --evento queda

# Monitorar e coletar automaticamente por 60 minutos
python datasets/coletar_dados_especificos.py --monitorar 60

# Monitorar com intervalo customizado
python datasets/coletar_dados_especificos.py --monitorar 120 --intervalo-verificacao 3
```

**Funcionalidades:**
- Coleta frames quando eventos específicos ocorrem (queda, banheiro, etc)
- Monitora sistema continuamente
- Filtra coletas por tipo de evento
- Estatísticas de coleta por evento

### 3. `coletar_dados.py` (já existente)
Coleta frames gerais do sistema em execução.

**Uso:**
```bash
# Coletar 100 frames a cada 5 segundos
python datasets/coletar_dados.py --quantidade 100 --intervalo 5

# Modo contínuo
python datasets/coletar_dados.py --modo-continuo --intervalo 10
```

### 4. `organizar_todos_datasets.py` (NOVO)
Organiza e consolida todos os datasets de diferentes fontes.

**Uso:**
```bash
# Escanear todas as fontes de dados
python datasets/organizar_todos_datasets.py --escanear

# Consolidar todos os datasets
python datasets/organizar_todos_datasets.py --consolidar todos

# Consolidar apenas uma fonte
python datasets/organizar_todos_datasets.py --consolidar coletados

# Gerar relatório completo
python datasets/organizar_todos_datasets.py --relatorio
```

**Funcionalidades:**
- Escaneia todas as fontes de dados disponíveis
- Consolida datasets de diferentes fontes
- Valida pares imagem-label
- Gera relatórios completos

## 📋 Workflow Recomendado

### Passo 1: Buscar Datasets Públicos

```bash
# Listar datasets disponíveis
python datasets/buscar_datasets_publicos.py --listar

# Consultar lista de fontes
cat datasets/publicos/FONTES_DATASETS.md
```

**O que fazer:**
1. Escolha datasets públicos relevantes
2. Baixe manualmente das fontes indicadas
3. Extraia em `datasets/publicos/{nome_dataset}/raw/`

### Passo 2: Coletar Dados do Sistema

```bash
# Opção A: Coleta geral
python datasets/coletar_dados.py --quantidade 500 --intervalo 5

# Opção B: Coleta específica por eventos (RECOMENDADO)
python datasets/coletar_dados_especificos.py --monitorar 120
```

**Dicas:**
- ✅ Execute o sistema normalmente enquanto coleta
- ✅ Foque em coletar mais frames de quedas e banheiro
- ✅ Varie horários e situações
- ✅ Mantenha boa qualidade de iluminação

### Passo 3: Anotar Imagens

```bash
# Anotar imagens coletadas
python datasets/anotar_dados.py datasets/coletados/images/frame_001.jpg
```

**Classes disponíveis:**
- `0`: pessoa (genérica)
- `1`: pessoa_em_pe
- `2`: pessoa_caida ⭐ (prioridade)
- `3`: pessoa_sentada
- `4`: pessoa_no_banheiro

### Passo 4: Organizar Datasets

```bash
# Escanear todas as fontes
python datasets/organizar_todos_datasets.py --escanear

# Consolidar todos os datasets
python datasets/organizar_todos_datasets.py --consolidar todos

# Gerar relatório
python datasets/organizar_todos_datasets.py --relatorio
```

### Passo 5: Preparar para Treinamento

```bash
# Preparar dataset final
python datasets/preparar_dataset.py \
    --anotados datasets/anotados \
    --saida datasets/treino \
    --classes datasets/classes.yaml
```

### Passo 6: Analisar Dataset

```bash
# Analisar qualidade do dataset
python datasets/analisar_dataset.py \
    --dataset datasets/treino/dataset.yaml \
    --salvar
```

### Passo 7: Treinar Modelo

```bash
# Treinar modelo customizado
python datasets/treinar_modelo.py \
    --dataset datasets/treino/dataset.yaml \
    --modelo yolov8s.pt \
    --epochs 100
```

## 📊 Estratégias de Coleta

### Estratégia 1: Coleta por Evento (Recomendada)

**Vantagens:**
- Foca em situações relevantes
- Melhor balanceamento de classes
- Mais eficiente

**Como usar:**
```bash
# Monitorar e coletar quando eventos ocorrem
python datasets/coletar_dados_especificos.py --monitorar 180
```

### Estratégia 2: Coleta Geral + Filtragem

**Vantagens:**
- Coleta mais diversa
- Captura situações inesperadas

**Como usar:**
```bash
# Coletar tudo
python datasets/coletar_dados.py --modo-continuo --intervalo 10

# Depois filtrar manualmente por tipo de evento
```

### Estratégia 3: Coleta Híbrida

**Vantagens:**
- Combina ambas as abordagens
- Máxima diversidade e relevância

**Como usar:**
1. Execute coleta por evento em horários específicos
2. Execute coleta geral em outros momentos
3. Consolide tudo com `organizar_todos_datasets.py`

## 🎯 Metas de Dataset

### Dataset Mínimo

| Classe | Imagens Mínimas | Recomendado |
|--------|----------------|-------------|
| pessoa | 200 | 500 |
| pessoa_em_pe | 200 | 500 |
| **pessoa_caida** | **300** | **800** |
| pessoa_sentada | 200 | 500 |
| pessoa_no_banheiro | 150 | 400 |
| **TOTAL** | **1050** | **2700** |

### Dataset Ideal

| Classe | Imagens Ideais |
|--------|----------------|
| pessoa | 1000+ |
| pessoa_em_pe | 1000+ |
| **pessoa_caida** | **1500+** |
| pessoa_sentada | 1000+ |
| pessoa_no_banheiro | 800+ |
| **TOTAL** | **5300+** |

## 💡 Dicas Importantes

### Balanceamento

- ✅ Classe 2 (pessoa_caida) deve ter mais exemplos (prioridade)
- ✅ Evite desbalanceamento extremo (>5x diferença)
- ✅ Use oversampling se necessário

### Qualidade

- ✅ Boa iluminação
- ✅ Resolução adequada (mínimo 640x480)
- ✅ Diversidade de ângulos e situações
- ✅ Anotações precisas

### Organização

- ✅ Mantenha metadados de cada coleta
- ✅ Use nomes de arquivo descritivos
- ✅ Organize por fonte de dados
- ✅ Documente origem das imagens

## 📝 Checklist de Criação de Dataset

- [ ] Buscar e baixar datasets públicos relevantes
- [ ] Coletar dados do sistema (mínimo 1000 imagens)
- [ ] Focar em coletar mais frames de quedas
- [ ] Anotar todas as imagens coletadas
- [ ] Validar anotações
- [ ] Organizar e consolidar datasets
- [ ] Preparar split train/val/test
- [ ] Analisar balanceamento
- [ ] Preparar para treinamento
- [ ] Documentar processo

## 🔗 Recursos Úteis

- `datasets/publicos/FONTES_DATASETS.md` - Lista de fontes públicas
- `datasets/README.md` - Documentação completa do sistema
- `datasets/GUIA_DATASETS.md` - Guia detalhado de uso

---

**Versão**: 1.0  
**Data**: 2025-11-24

