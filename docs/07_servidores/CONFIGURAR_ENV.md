# ⚙️ Guia: Configurar Arquivos .env

## 📋 Informações Necessárias

Antes de configurar, você precisa dos IPs de cada servidor:

```bash
# Execute em cada servidor para obter o IP
hostname -I | awk '{print $1}'
```

**Anotar**:
- Server BD: `___________`
- Server STR: `___________`
- Server PROCESS: `___________`
- Server API: `___________`

---

## 🔧 Server PROCESS - Configurar .env

### Localização
```bash
/opt/iasenior/.env
```

### Conteúdo Completo
```env
# ============================================================================
# Server PROCESS - Inferência YOLO
# ============================================================================

# Stream RTSP
RTSP_HOST=localhost
RTSP_PORT=8554
STREAM_NAME=ia

# Modelo YOLO
MODEL_PATH=modelos/queda_custom.pt
CONFIDENCE_THRESHOLD=0.4
FALL_DETECTION_ENABLED=true
TRACKING_ENABLED=true

# Banco de Dados (Server BD)
DB_HOST=IP_DO_SERVER_BD
DB_PORT=5432
DB_NAME=iasenior
DB_USER=iasenior
DB_PASSWORD=iasenior2366

# Storage (Server STR)
STORAGE_HOST=IP_DO_SERVER_STR
STORAGE_PATH=/mnt/iasenior

# Captura de tela (ajustar conforme necessário)
MONITOR_IDX=0
FRAME_WIDTH=1280
FRAME_HEIGHT=720
FPS=20

# MJPEG
MJPEG_PORT=8888
MJPEG_HOST=0.0.0.0
```

### Como Configurar
```bash
# No Server PROCESS
cd /opt/iasenior
nano .env

# Substituir:
# IP_DO_SERVER_BD pelo IP real do Server BD
# IP_DO_SERVER_STR pelo IP real do Server STR

# Salvar: Ctrl+O, Enter, Ctrl+X
```

---

## 🔧 Server API - Configurar .env

### Localização
```bash
/opt/iasenior/.env
```

### Conteúdo Completo
```env
# ============================================================================
# Server API - Dashboard Streamlit
# ============================================================================

# Banco de Dados (Server BD)
DB_HOST=IP_DO_SERVER_BD
DB_PORT=5432
DB_NAME=iasenior
DB_USER=iasenior
DB_PASSWORD=iasenior2366

# Stream MJPEG (Server PROCESS)
STREAM_HOST=IP_DO_SERVER_PROCESS
STREAM_PORT=8888

# Dashboard Streamlit
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0

# Portal Cliente
PORTAL_PORT=8080
PORTAL_HOST=0.0.0.0

# Autenticação
ADMIN_USER=admin
ADMIN_PASSWORD=admin123  # ALTERE ESTA SENHA!

# Refresh
REFRESH_INTERVAL=3
```

### Como Configurar
```bash
# No Server API
cd /opt/iasenior
nano .env

# Substituir:
# IP_DO_SERVER_BD pelo IP real do Server BD
# IP_DO_SERVER_PROCESS pelo IP real do Server PROCESS

# Salvar: Ctrl+O, Enter, Ctrl+X
```

---

## ✅ Verificar Configuração

### No Server PROCESS
```bash
cd /opt/iasenior
source venv/bin/activate

# Testar se consegue ler .env
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('DB_HOST:', os.getenv('DB_HOST'))
print('DB_NAME:', os.getenv('DB_NAME'))
"
```

### No Server API
```bash
cd /opt/iasenior
source venv/bin/activate

# Testar se consegue ler .env
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('DB_HOST:', os.getenv('DB_HOST'))
print('STREAM_HOST:', os.getenv('STREAM_HOST'))
"
```

---

## 🧪 Testar Conexões

### Testar BD (do PROCESS ou API)
```bash
# Instalar cliente se necessário
apt-get install -y postgresql-client

# Testar conexão
psql -h IP_DO_SERVER_BD -U iasenior -d iasenior -c "SELECT version();"
# Senha: iasenior2366
```

### Testar BD via Python (do PROCESS)
```bash
cd /opt/iasenior
source venv/bin/activate

python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print('✅ Conexão BD OK')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### Testar BD via Python (do API)
```bash
cd /opt/iasenior
source venv/bin/activate

python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print('✅ Conexão BD OK')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

## 📝 Checklist

- [ ] IPs de todos os servidores anotados
- [ ] Server PROCESS: `.env` configurado com IPs corretos
- [ ] Server API: `.env` configurado com IPs corretos
- [ ] Conexão BD testada do PROCESS
- [ ] Conexão BD testada do API
- [ ] Senhas alteradas (especialmente admin do dashboard)

---

## 🔒 Segurança

⚠️ **IMPORTANTE**: Após configurar, considere:

1. Alterar senha do admin do dashboard
2. Restringir acesso ao `.env`:
   ```bash
   chmod 600 /opt/iasenior/.env
   ```
3. Não commitar `.env` no Git (já está no .gitignore)

---

**Próximo passo**: Após configurar os `.env`, testar os serviços manualmente antes de iniciar com systemd.

