# Integração MJPEG com Detecções YOLO

## 📋 Visão Geral

A integração MJPEG permite visualizar o stream de vídeo com detecções YOLO em tempo real no dashboard Streamlit, sem necessidade de salvar frames em disco.

## 🚀 Como Usar

### 1. Iniciar Servidor MJPEG com Detecções

```bash
# Opção 1: Usar script de inicialização
./iniciar_mjpeg_com_deteccoes.sh

# Opção 2: Executar diretamente
python3 mjpeg_server_com_deteccoes.py
```

O servidor será iniciado em:
- **URL do Stream**: `http://localhost:8888/video`
- **Status API**: `http://localhost:8888/status`
- **Health Check**: `http://localhost:8888/health`

### 2. Acessar no Dashboard

1. Inicie o dashboard Streamlit:
   ```bash
   streamlit run painel_IA/app/dashboard.py
   ```

2. Na aba "📺 Monitoramento", selecione **"Stream MJPEG (Tempo Real)"**

3. O stream será exibido automaticamente com todas as detecções YOLO

## 🎯 Funcionalidades

### Servidor MJPEG (`mjpeg_server_com_deteccoes.py`)

- ✅ **Stream RTSP**: Conecta ao stream RTSP configurado em `config.py`
- ✅ **Inferência YOLO**: Processa cada frame com o modelo YOLO
- ✅ **Detecção de Quedas**: Usa modelo customizado quando disponível
- ✅ **Contagem de Pessoas**: Monitora pessoas no quarto e banheiro
- ✅ **Reconexão Automática**: Reconecta automaticamente em caso de falha
- ✅ **API de Status**: Endpoint JSON com informações em tempo real

### Dashboard Streamlit

- ✅ **Modo Stream MJPEG**: Visualização em tempo real via HTTP
- ✅ **Modo Frame Estático**: Visualização tradicional via arquivo
- ✅ **Status em Tempo Real**: Mostra pessoas no quarto, frames processados, etc.
- ✅ **Auto-refresh**: Atualização automática do stream

## 📡 Endpoints da API

### GET `/video`
Stream MJPEG com detecções YOLO em tempo real.

**Uso**: `<img src="http://localhost:8888/video">`

### GET `/status`
Retorna status atual do sistema em JSON.

**Resposta**:
```json
{
  "stream_connected": true,
  "model_loaded": true,
  "pessoas_quarto": 2,
  "status_banheiro": {
    "pessoas_no_banheiro": 1,
    "pessoas": [
      {
        "track_id": "123",
        "tempo_segundos": 45,
        "alerta": false
      }
    ]
  },
  "frame_count": 12345,
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET `/health`
Health check simples.

**Resposta**:
```json
{
  "status": "healthy",
  "stream_connected": true,
  "model_loaded": true
}
```

## ⚙️ Configuração

As configurações estão em `config.py`:

```python
# Servidor MJPEG
MJPEG_HOST = "0.0.0.0"  # Host para bind
MJPEG_PORT = 8888       # Porta do servidor
MJPEG_URL = "http://localhost:8888/video"  # URL completa

# Stream RTSP
RTSP_URL = "rtsp://..."  # URL do stream RTSP

# Modelo YOLO
MODEL_PATH = "modelos/queda_custom.pt"
CONFIDENCE_THRESHOLD = 0.4
```

## 🔧 Troubleshooting

### Stream não aparece no dashboard

1. **Verificar se servidor MJPEG está rodando**:
   ```bash
   curl http://localhost:8888/health
   ```

2. **Verificar logs**:
   ```bash
   tail -f logs/mjpeg_server.log
   ```

3. **Verificar conexão RTSP**:
   - Teste o stream RTSP diretamente com VLC ou ffplay
   - Verifique se `RTSP_URL` em `config.py` está correto

### Modelo não carrega

1. **Verificar se modelo existe**:
   ```bash
   ls -lh modelos/queda_custom.pt
   ```

2. **Verificar dependências**:
   ```bash
   pip install ultralytics torch
   ```

### Performance

- O servidor MJPEG processa frames em tempo real, o que pode ser intensivo
- Para melhor performance, use GPU (CUDA/MPS)
- Ajuste `CONFIDENCE_THRESHOLD` para reduzir processamento

## 🐳 Docker

Para usar com Docker, certifique-se de:

1. Expor a porta 8888:
   ```yaml
   ports:
     - "8888:8888"
   ```

2. Configurar `MJPEG_HOST=0.0.0.0` para aceitar conexões externas

3. Ajustar `MJPEG_URL` no dashboard para o IP do container

## 📊 Comparação: MJPEG vs Frame Estático

| Característica | MJPEG | Frame Estático |
|---------------|-------|----------------|
| Latência | Baixa (~100ms) | Média (~1-2s) |
| Atualização | Contínua | A cada refresh |
| Uso de Disco | Não | Sim (salva frames) |
| Performance | Média-Alta | Baixa |
| Compatibilidade | Navegadores | Todos |

## 🎨 Personalização

### Alterar qualidade JPEG

No arquivo `mjpeg_server_com_deteccoes.py`, linha ~350:

```python
_, buffer = cv2.imencode('.jpg', frame_processado, [cv2.IMWRITE_JPEG_QUALITY, 85])
```

Altere `85` para um valor entre 1-100 (maior = melhor qualidade, mais dados).

### Alterar taxa de atualização

No dashboard, o stream é atualizado a cada 100ms. Para alterar, modifique o intervalo no JavaScript (linha ~570 do `dashboard.py`).

## 📝 Notas

- O stream MJPEG funciona melhor em redes locais
- Para acesso remoto, considere usar HTTPS e autenticação
- O modelo customizado de quedas usa threshold baixo (0.05) para melhor detecção
- O servidor reconecta automaticamente em caso de falha no stream RTSP

