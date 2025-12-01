# Novas Funcionalidades Implementadas

## 📋 Resumo

Foram adicionadas duas funcionalidades principais ao sistema:

1. **Contagem de Pessoas no Quarto**: Conta pessoas detectadas pelo YOLO na área do quarto
2. **Monitoramento de Tempo no Banheiro**: Detecta quando uma pessoa fica no banheiro por mais de 10 minutos

## 🏠 Contagem de Pessoas no Quarto

### Como Funciona

- O sistema detecta todas as pessoas usando YOLO
- Usa tracking para manter IDs consistentes entre frames
- Conta pessoas que estão dentro da área definida como "quarto" (ou todas as pessoas se não usar área específica)
- Salva a contagem em `resultados/contagem_quarto.txt`

### Configuração

No `config.py` ou via variáveis de ambiente:

```python
ROOM_COUNT_ENABLED = True  # Habilita contagem
ROOM_USE_AREA = False      # Se False, conta todas as pessoas. Se True, usa área definida
ROOM_AREA = [0.0, 0.0, 1.0, 1.0]  # [x1, y1, x2, y2] normalizado (0.0 a 1.0)
```

**Exemplo de área do quarto (lado esquerdo da tela):**
```python
ROOM_AREA = [0.0, 0.0, 0.6, 1.0]  # 60% da largura à esquerda
```

### Visualização

- A contagem é exibida no dashboard Streamlit
- Aparece sobreposta no vídeo transmitido
- Atualizada em tempo real

## 🚿 Monitoramento de Tempo no Banheiro

### Como Funciona

- O sistema detecta pessoas dentro da área definida como "banheiro"
- Usa tracking para manter IDs e rastrear entrada/saída
- Monitora o tempo que cada pessoa permanece no banheiro
- Gera alerta quando o tempo excede 10 minutos (configurável)
- Salva status em `resultados/status_banheiro.txt` (JSON)

### Configuração

No `config.py` ou via variáveis de ambiente:

```python
BATHROOM_MONITORING_ENABLED = True      # Habilita monitoramento
BATHROOM_TIME_LIMIT_MINUTES = 10        # Limite de tempo em minutos
BATHROOM_AREA = [0.6, 0.0, 1.0, 1.0]    # [x1, y1, x2, y2] normalizado (lado direito)
```

**Exemplo de área do banheiro (lado direito da tela):**
```python
BATHROOM_AREA = [0.6, 0.0, 1.0, 1.0]  # 40% da largura à direita
```

### Alertas

- Quando uma pessoa fica mais de 10 minutos no banheiro:
  - Log de alerta é gerado
  - Mensagem aparece no vídeo transmitido
  - Dashboard mostra alerta visual
  - Informações são salvas no arquivo de status

### Visualização

- Número de pessoas no banheiro exibido no dashboard
- Tempo decorrido para cada pessoa
- Alertas destacados em vermelho
- Área do banheiro desenhada no vídeo (retângulo azul)

## 🔧 Tracking de Pessoas

O sistema usa **ByteTrack** (tracker padrão do Ultralytics) para:

- Manter IDs consistentes entre frames
- Rastrear entrada/saída de áreas
- Contar pessoas corretamente mesmo com oclusão temporária
- Monitorar tempo individual de cada pessoa

### Configuração

```python
TRACKING_ENABLED = True  # Habilita tracking (recomendado)
```

## 📁 Arquivos Gerados

### `resultados/contagem_quarto.txt`
Contém apenas o número de pessoas no quarto.

**Exemplo:**
```
2
```

### `resultados/status_banheiro.txt`
Contém JSON com informações detalhadas do banheiro.

**Exemplo:**
```json
{
  "pessoas_no_banheiro": 1,
  "alertas": [
    {
      "track_id": "123",
      "tempo_minutos": 12,
      "tempo_segundos": 34,
      "timestamp": "2025-01-XX 12:34:56"
    }
  ],
  "pessoas": [
    {
      "track_id": "123",
      "tempo_minutos": 12,
      "tempo_segundos": 34,
      "alerta": true
    }
  ]
}
```

## 🎨 Visualizações no Vídeo

O vídeo transmitido mostra:

1. **Retângulo Verde** (se `ROOM_USE_AREA=True`): Área do quarto
2. **Retângulo Azul**: Área do banheiro
3. **Texto no canto superior esquerdo**:
   - "Pessoas no Quarto: X"
   - "Pessoas no Banheiro: Y"
   - "ALERTA: Pessoa no banheiro > 10min!" (se houver alerta)

## 📊 Dashboard Streamlit

### Métricas Principais

- **Pessoas no Quarto**: Contagem atual
- **Pessoas no Banheiro**: Contagem atual
- **Alertas Ativos**: Número de alertas de tempo excedido
- **Status Geral**: OK ou Queda detectada

### Painel Lateral

- **Contagem no Quarto**: Métrica atualizada
- **Status do Banheiro**: 
  - Número de pessoas
  - Tempo de cada pessoa (formato MM:SS)
  - Alertas destacados em vermelho

## ⚙️ Configuração de Áreas

As áreas são definidas em coordenadas normalizadas (0.0 a 1.0):

- `x1, y1`: Canto superior esquerdo (0.0, 0.0 = canto superior esquerdo da tela)
- `x2, y2`: Canto inferior direito (1.0, 1.0 = canto inferior direito da tela)

**Exemplos:**

```python
# Todo o frame (padrão quarto)
ROOM_AREA = [0.0, 0.0, 1.0, 1.0]

# Lado esquerdo (50% da largura)
ROOM_AREA = [0.0, 0.0, 0.5, 1.0]

# Lado direito (50% da largura)
BATHROOM_AREA = [0.5, 0.0, 1.0, 1.0]

# Quadrante superior esquerdo
AREA = [0.0, 0.0, 0.5, 0.5]
```

## 🔍 Detecção de Áreas

O sistema verifica se o **centro da bounding box** da pessoa está dentro da área definida. Isso torna a detecção mais robusta mesmo quando a pessoa está parcialmente dentro/fora da área.

## 🚀 Como Usar

1. **Configure as áreas** no `config.py` ou via variáveis de ambiente
2. **Ajuste o limite de tempo** do banheiro se necessário (padrão: 10 minutos)
3. **Inicie o sistema** com `./start_tudo.sh`
4. **Monitore no dashboard** em `http://localhost:8501`

## 📝 Logs

Os logs incluem informações sobre:

- Pessoas entrando/saindo do banheiro
- Alertas de tempo excedido
- Contagens periódicas (a cada 5 segundos)

**Exemplo de log:**
```
2025-01-XX 12:34:56 - INFO - 🚿 Pessoa 123 entrou no banheiro
2025-01-XX 12:45:00 - WARNING - ⚠️ ALERTA: Pessoa 123 no banheiro há 10min 4s (limite: 10min)
2025-01-XX 12:46:00 - INFO - ✅ 600 frames processados | FPS: 20.00 | Status: ok | Quarto: 2 pessoas | Banheiro: 1 pessoas | Alertas: 1
```

## 🔧 Troubleshooting

### Tracking não funciona

- Verifique se `TRACKING_ENABLED = True` no config
- Certifique-se de que está usando Ultralytics versão >= 8.0.0
- O tracking requer consistência entre frames (FPS adequado)

### Contagem incorreta

- Ajuste `CONFIDENCE_THRESHOLD` se muitas detecções falsas
- Verifique se as áreas estão configuradas corretamente
- Use `ROOM_USE_AREA = False` para contar todas as pessoas detectadas

### Alertas não aparecem

- Verifique se o tempo no banheiro realmente excedeu o limite
- Confira os logs para ver se há pessoas sendo detectadas
- Verifique se `BATHROOM_MONITORING_ENABLED = True`

## 🎯 Próximos Passos Sugeridos

- [ ] Configuração visual de áreas no dashboard
- [ ] Notificações por email/SMS em caso de alerta
- [ ] Histórico de eventos (entrada/saída)
- [ ] Gráficos de tempo no banheiro ao longo do dia
- [ ] Suporte a múltiplas áreas personalizadas

