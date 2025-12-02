# 🔧 Corrigir Erro: $DISPLAY not set

## ⚠️ Problema

O script `stream_inferencia_rtsp.py` está tentando capturar a tela usando `mss`, mas em servidores Linux sem display isso não funciona.

**Erro**: `mss.exception.ScreenShotError: $DISPLAY not set.`

## ✅ Solução: Modificar Script para Usar RTSP/Câmera

### Opção 1: Correção Manual Rápida

No Server PROCESS, execute:

```bash
cd /opt/iasenior
source venv/bin/activate

# Editar o script
nano scripts/stream_inferencia_rtsp.py
```

**Localizar a função `inicializar_captura` (linha ~119)** e substituir por:

```python
def inicializar_captura(self):
    """Inicializa a captura de vídeo (RTSP ou câmera)."""
    import os
    try:
        # Tentar usar RTSP stream primeiro
        rtsp_source = os.getenv("RTSP_INPUT", None)
        camera_index = int(os.getenv("CAMERA_INDEX", "-1"))
        
        if rtsp_source:
            logger.info(f"📺 Conectando ao stream RTSP: {rtsp_source}")
            self.cap = cv2.VideoCapture(rtsp_source)
            if not self.cap.isOpened():
                raise ValueError(f"Não foi possível conectar ao stream RTSP: {rtsp_source}")
            logger.info("✅ Conectado ao stream RTSP")
        elif camera_index >= 0:
            logger.info(f"📺 Abrindo câmera {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise ValueError(f"Não foi possível abrir câmera {camera_index}")
            logger.info(f"✅ Câmera {camera_index} aberta")
        else:
            # Fallback: tentar câmera padrão (0)
            logger.info("📺 Tentando abrir câmera padrão (índice 0)...")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise ValueError("Não foi possível abrir câmera. Configure RTSP_INPUT ou CAMERA_INDEX no .env")
            logger.info("✅ Câmera padrão aberta")
        
        # Configurar resolução
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        
        # Calcular áreas em pixels
        self.bathroom_area_px = (
            int(BATHROOM_AREA[0] * FRAME_WIDTH),
            int(BATHROOM_AREA[1] * FRAME_HEIGHT),
            int(BATHROOM_AREA[2] * FRAME_WIDTH),
            int(BATHROOM_AREA[3] * FRAME_HEIGHT)
        )
        
        self.room_area_px = (
            int(ROOM_AREA[0] * FRAME_WIDTH),
            int(ROOM_AREA[1] * FRAME_HEIGHT),
            int(ROOM_AREA[2] * FRAME_WIDTH),
            int(ROOM_AREA[3] * FRAME_HEIGHT)
        )
        
        logger.info(f"📍 Área do quarto: {self.room_area_px}")
        logger.info(f"🚿 Área do banheiro: {self.bathroom_area_px}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar captura: {e}", exc_info=True)
        raise
```

**Também precisa modificar onde captura o frame**. Procurar por `self.sct.grab` e substituir por:

```python
# ANTES (linha ~600):
frame = np.array(self.sct.grab(self.monitor))

# DEPOIS:
ret, frame = self.cap.read()
if not ret:
    logger.warning("⚠️  Não foi possível ler frame")
    continue  # ou return None dependendo do contexto
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

**E no cleanup** (final do script), substituir:

```python
# ANTES:
if self.sct:
    self.sct.close()

# DEPOIS:
if hasattr(self, "cap") and self.cap:
    self.cap.release()
```

### Opção 2: Adicionar Variáveis no .env

Adicione no arquivo `.env`:

```bash
# No Server PROCESS
nano /opt/iasenior/.env
```

Adicionar:

```env
# Fonte de vídeo (escolha uma opção)
# Opção 1: Stream RTSP
RTSP_INPUT=rtsp://IP_CAMERA:554/stream

# Opção 2: Câmera USB (índice)
# CAMERA_INDEX=0

# Se não configurar nenhum, tentará câmera 0 por padrão
```

### Opção 3: Usar Script de Teste Simples

Crie um script de teste primeiro:

```bash
cd /opt/iasenior
source venv/bin/activate

cat > test_camera.py <<'EOF'
import cv2
import os

# Testar RTSP
rtsp = os.getenv("RTSP_INPUT")
if rtsp:
    print(f"Testando RTSP: {rtsp}")
    cap = cv2.VideoCapture(rtsp)
else:
    print("Testando câmera 0...")
    cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("✅ Câmera/Stream OK!")
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame capturado: {frame.shape}")
    else:
        print("⚠️  Não conseguiu ler frame")
    cap.release()
else:
    print("❌ Não foi possível abrir")
EOF

python test_camera.py
```

## 🧪 Testar Após Correção

```bash
cd /opt/iasenior
source venv/bin/activate

# Configurar variável de ambiente (se usar RTSP)
export RTSP_INPUT=rtsp://IP_CAMERA:554/stream

# Ou para câmera USB
export CAMERA_INDEX=0

# Testar
python scripts/stream_inferencia_rtsp.py
```

## 📝 Resumo das Mudanças

1. ✅ Substituir `mss.mss()` por `cv2.VideoCapture()`
2. ✅ Adicionar suporte para RTSP_INPUT ou CAMERA_INDEX
3. ✅ Modificar captura de frame de `mss.grab()` para `cap.read()`
4. ✅ Ajustar cleanup para `cap.release()`

## ⚠️ Importante

- **Remover import mss** se não for mais usado (ou deixar para compatibilidade)
- **Adicionar import os** se não existir
- **Testar com câmera ou stream RTSP** antes de iniciar serviço

---

**Após corrigir, teste manualmente antes de iniciar o serviço systemd!**

