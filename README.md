<div align="center">

![IA Senior Logo](assets/logo/logo.png)

# IA Senior - Sistema de Monitoramento Inteligente com IA

Sistema completo de monitoramento em tempo real com detecção de objetos usando YOLO, transmissão RTSP e dashboard Streamlit.

</div>

## 📋 Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Troubleshooting](#troubleshooting)

## ✨ Características

- **Detecção em Tempo Real**: Usa YOLOv8 para detecção de objetos em tempo real
- **Stream RTSP**: Transmissão de vídeo via RTSP usando MediaMTX
- **Detecção de Quedas**: Algoritmo básico de detecção de quedas baseado em análise de bounding boxes
- **Dashboard Interativo**: Interface web Streamlit para monitoramento
- **Servidor MJPEG**: Streaming HTTP adicional via servidor Flask
- **Logging Estruturado**: Sistema completo de logs estruturados em JSON para debug e monitoramento
- **Reconexão Automática**: Recuperação automática de falhas de conexão
- **Orquestração Avançada**: Padrões de orquestração (paralelo, sequencial, magnético) com retry e timeout
- **Métricas em Tempo Real**: Coleta de métricas de performance (FPS, latência, uso de recursos)
- **Cache Inteligente**: Sistema de cache para frames processados
- **Health Checks Avançados**: Monitoramento robusto da saúde dos agentes

## 📦 Requisitos

### Software

- Python 3.10+
- FFmpeg
- Docker (opcional, para MediaMTX e painel)
- VLC Player (opcional, para visualizar stream)

### Hardware

- MacOS (para captura de tela via avfoundation)
- Apple Silicon (M1/M2) para aceleração de hardware (opcional)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd IASENIOR_FINAL
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Baixe o modelo YOLO

O modelo `yolov8n.pt` será baixado automaticamente na primeira execução. Alternativamente:

```bash
# Baixar manualmente se necessário
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### 5. Configure o MediaMTX

```bash
# Via Docker (recomendado)
docker compose up -d mediamtx

# Ou instale e execute localmente
# brew install mediamtx  # MacOS
```

## 📚 Documentação Completa

A documentação está organizada em `docs/`. Veja o **[Índice Completo](docs/00_INDICE.md)** para navegação.

### 📖 Documentação Rápida

#### Visão Geral
- **[Funcionalidades](docs/01_visao_geral/FUNCIONALIDADES.md)**: Lista completa 

#### Instalação e Configuração
- **[Setup Docker](docs/02_instalacao_configuracao/SETUP_DOCKER.md)**: Guia completo de setup com Docker
- **[Setup PostgreSQL](docs/02_instalacao_configuracao/SETUP_POSTGRESQL.md)**: Configuração do banco de dados
- **[Configurar Notificações](docs/02_instalacao_configuracao/CONFIGURAR_NOTIFICACOES.md)**: Sistema de notificações por email
- **[Autenticação](docs/02_instalacao_configuracao/AUTENTICACAO.md)**: Sistema de autenticação e níveis de acesso
- **[Integração MJPEG](docs/02_instalacao_configuracao/INTEGRACAO_MJPEG.md)**: Configuração do stream MJPEG

#### Funcionalidades
- **[Dashboard Premium](docs/03_funcionalidades/DASHBOARD.md)**: Documentação completa do dashboard
- **[Layout Visual](docs/03_funcionalidades/LAYOUT_VISUAL.md)**: Estrutura visual do dashboard

#### Agentes Inteligentes
- **[Sistema de Agentes](docs/04_agentes/SISTEMA_AGENTES.md)**: Visão geral consolidada dos agentes
- **[Comunicação](docs/04_agentes/COMUNICACAO.md)**: Sistema de comunicação entre agentes
- **[Colaboração](docs/04_agentes/COLABORACAO.md)**: Sessões colaborativas
- **[CLI de Debate](docs/04_agentes/CLI_DEBATE.md)**: Interface de linha de comando

#### Datasets e Treinamento
- **[Guia de Datasets](docs/05_datasets_treinamento/GUIA_DATASETS.md)**: Como criar e gerenciar datasets
- **[Treinamento](docs/05_datasets_treinamento/TREINAMENTO.md)**: Guia completo de treinamento
- **[Criar Datasets](docs/05_datasets_treinamento/CRIAR_DATASETS.md)**: Scripts e workflows

#### Melhorias
- **[Melhorias Implementadas](docs/06_melhorias/MELHORIAS.md)**: Consolidação de todas as melhorias
- **[Melhorias de Produto](docs/06_melhorias/MELHORIAS_PRODUTO.md)**: Melhorias de produto específicas

## 🐳 Setup Rápido com Docker

### PostgreSQL com Docker (Recomendado)

```bash
# 1. Copiar arquivo de ambiente
cp .env.example .env

# 2. Iniciar PostgreSQL
docker-compose up -d postgres

# 3. Pronto! O sistema criará o schema automaticamente
```

Para mais detalhes, veja [DOCKER_SETUP.md](DOCKER_SETUP.md)

## ⚙️ Configuração

Todas as configurações estão centralizadas no arquivo `config.py`. Você pode editar diretamente ou usar variáveis de ambiente:

### Variáveis de Ambiente

```bash
# Configurações de stream RTSP
export RTSP_HOST="localhost"
export RTSP_PORT="8554"
export STREAM_NAME="ia"

# Configurações de captura
export MONITOR_IDX="3"  # Use listar_monitores.py para ver monitores disponíveis
export FRAME_WIDTH="1280"
export FRAME_HEIGHT="720"
export FPS="20"

# Configurações do modelo
export MODEL_PATH="yolov8n.pt"
export CONFIDENCE_THRESHOLD="0.4"
export FALL_DETECTION_ENABLED="true"

# Configurações do painel
export REFRESH_INTERVAL="3"
```

### Listar Monitores Disponíveis

```bash
python listar_monitores.py
```

Use o índice do monitor desejado para configurar `MONITOR_IDX` no `config.py`.

## 📖 Uso

### Iniciar Todos os Serviços

```bash
chmod +x start_tudo.sh
./start_tudo.sh
```

Este script:
1. Inicia o MediaMTX (servidor RTSP)
2. Inicia a transmissão de captura de tela
3. Inicia a inferência com IA
4. Inicia o painel Streamlit
5. Abre o VLC para visualizar o stream

### Parar Todos os Serviços

```bash
chmod +x stop_tudo.sh
./stop_tudo.sh
```

### Iniciar Serviços Individuais

#### Servidor MJPEG

```bash
python mjpeg_server.py
```

Acesse: `http://localhost:8888`

#### Dashboard Streamlit

```bash
cd painel_IA/app
streamlit run dashboard.py
```

Acesse: `http://localhost:8501`

#### Inferência RTSP

```bash
python scripts/stream_inferencia_rtsp.py
```

## 📁 Estrutura do Projeto

```
IASENIOR_FINAL/
├── config.py                      # Configurações centralizadas
├── requirements.txt               # Dependências Python
├── README.md                      # Este arquivo
│
├── scripts/
│   └── stream_inferencia_rtsp.py # Script principal de inferência
│   └── transmitir_gpu_m1.sh      # Script de transmissão (MacOS)
│
├── painel_IA/
│   ├── app/
│   │   └── dashboard.py          # Dashboard Streamlit
│   ├── Dockerfile                # Dockerfile do painel
│   └── docker-compose.yml        # Compose do painel
│
├── resultados/                    # Frames e status salvos
│   ├── ultima_frame.jpg
│   ├── status.txt
│   └── captura_manual/
│
├── logs/                          # Logs do sistema
│   ├── inferencia.log
│   ├── mediamtx.log
│   ├── painel.log
│   └── mjpeg_server.log
│
├── modelos/                       # Modelos YOLO
│   └── yolov8n.pt
│
├── start_tudo.sh                 # Script para iniciar tudo
├── stop_tudo.sh                  # Script para parar tudo
├── mjpeg_server.py               # Servidor MJPEG
└── listar_monitores.py           # Lista monitores disponíveis
```

## 🔍 Detecção de Quedas

O sistema implementa uma detecção básica de quedas baseada em:

1. **Detecção de Pessoas**: Usa YOLO para detectar pessoas (classe 0)
2. **Análise de Proporção**: Calcula a relação altura/largura da bounding box
3. **Posição**: Verifica se a pessoa está na parte inferior do frame
4. **Critério**: Considera queda se:
   - `aspect_ratio < 0.7` (pessoa mais larga que alta)
   - `box_center_y > frame_center_y` (pessoa na metade inferior)

**Nota**: Este é um algoritmo básico. Para produção, considere usar modelos especializados em detecção de quedas ou implementar técnicas mais avançadas (tracking, análise temporal, etc.).

## 🐛 Troubleshooting

### MediaMTX não inicia

```bash
# Verificar se a porta 8554 está livre
lsof -i:8554

# Matar processo na porta
lsof -ti:8554 | xargs kill -9
```

### FFmpeg não encontra o dispositivo

```bash
# Listar dispositivos disponíveis
ffmpeg -f avfoundation -list_devices true -i ""

# Ajustar DEVICE no script transmitir_gpu_m1.sh
```

### Modelo YOLO não encontrado

O modelo será baixado automaticamente na primeira execução. Se houver problemas:

```bash
# Baixar manualmente
python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')"
```

### Stream não aparece no VLC

1. Verifique se o MediaMTX está rodando
2. Verifique os logs em `logs/mediamtx.log`
3. Teste o stream diretamente:
   ```bash
   ffplay rtsp://localhost:8554/ia
   ```

### Dashboard não atualiza

1. Verifique se `results/ultima_frame.jpg` está sendo atualizado
2. Verifique os logs em `logs/inferencia.log`
3. Ajuste `REFRESH_INTERVAL` no `config.py`

## 📝 Logs

Todos os logs são salvos no diretório `logs/`:

- `inferencia.log`: Logs da inferência YOLO
- `mediamtx.log`: Logs do servidor RTSP
- `painel.log`: Logs do dashboard Streamlit
- `mjpeg_server.log`: Logs do servidor MJPEG
- `transmissao.log`: Logs da transmissão de vídeo

## 🔧 Melhorias Futuras

- [ ] Implementar tracking de objetos para melhor detecção de quedas
- [ ] Adicionar notificações (email, SMS) em caso de queda
- [ ] Interface de configuração web
- [ ] Suporte a múltiplas câmeras/streams
- [ ] Banco de dados para histórico de detecções
- [ ] API REST para integração
- [ ] Métricas e estatísticas avançadas

## 📄 Licença



## 👤 Autor

Bruno Nogueira

## 🙏 Agradecimentos



