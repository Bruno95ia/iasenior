"""
Arquivo de configuração centralizado para o sistema de monitoramento com IA.
Suporta variáveis de ambiente e arquivo .env (se python-dotenv estiver instalado).
"""

import os
from pathlib import Path

# Tentar carregar variáveis de ambiente de arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv não instalado, usar apenas variáveis de ambiente do sistema

# Diretórios
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "resultados"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "modelos"

# Criar diretórios se não existirem
RESULTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Configurações do stream RTSP
RTSP_HOST = os.getenv("RTSP_HOST", "localhost")
RTSP_PORT = int(os.getenv("RTSP_PORT", "8554"))
STREAM_NAME = os.getenv("STREAM_NAME", "ia")
RTSP_URL = f"rtsp://{RTSP_HOST}:{RTSP_PORT}/{STREAM_NAME}"

# Configurações de captura de tela
MONITOR_IDX = int(os.getenv("MONITOR_IDX", "3"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "1280"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "720"))
FPS = int(os.getenv("FPS", "20"))

# Configurações do modelo YOLO
# Modelo customizado treinado para detecção de quedas
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "modelos" / "queda_custom.pt"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.4"))

# Configurações de detecção
# Classes COCO: person=0
PERSON_CLASS_ID = 0
FALL_DETECTION_ENABLED = os.getenv("FALL_DETECTION_ENABLED", "true").lower() == "true"

# Configurações de tracking de pessoas
TRACKING_ENABLED = os.getenv("TRACKING_ENABLED", "true").lower() == "true"

# Configurações de contagem de pessoas no quarto
ROOM_COUNT_ENABLED = os.getenv("ROOM_COUNT_ENABLED", "true").lower() == "true"
# Se False, conta todas as pessoas detectadas. Se True, usa área definida
ROOM_USE_AREA = os.getenv("ROOM_USE_AREA", "false").lower() == "true"
# Área do quarto em coordenadas normalizadas (x1, y1, x2, y2) de 0.0 a 1.0
# Exemplo: [0.0, 0.0, 0.6, 1.0] = lado esquerdo da tela
ROOM_AREA = [
    float(os.getenv("ROOM_X1", "0.0")),
    float(os.getenv("ROOM_Y1", "0.0")),
    float(os.getenv("ROOM_X2", "1.0")),
    float(os.getenv("ROOM_Y2", "1.0"))
]

# Configurações de detecção de tempo no banheiro
BATHROOM_MONITORING_ENABLED = os.getenv("BATHROOM_MONITORING_ENABLED", "true").lower() == "true"
BATHROOM_TIME_LIMIT_MINUTES = int(os.getenv("BATHROOM_TIME_LIMIT_MINUTES", "10"))
BATHROOM_TIME_LIMIT_SECONDS = BATHROOM_TIME_LIMIT_MINUTES * 60
# Área do banheiro em coordenadas normalizadas (x1, y1, x2, y2) de 0.0 a 1.0
# Exemplo: [0.6, 0.0, 1.0, 1.0] = lado direito da tela
BATHROOM_AREA = [
    float(os.getenv("BATHROOM_X1", "0.6")),
    float(os.getenv("BATHROOM_Y1", "0.0")),
    float(os.getenv("BATHROOM_X2", "1.0")),
    float(os.getenv("BATHROOM_Y2", "1.0"))
]

# Configurações do FFmpeg
FFMPEG_PRESET = os.getenv("FFMPEG_PRESET", "ultrafast")
FFMPEG_TUNE = os.getenv("FFMPEG_TUNE", "zerolatency")

# Configurações do painel
FRAME_PATH = str(RESULTS_DIR / "ultima_frame.jpg")
STATUS_PATH = str(RESULTS_DIR / "status.txt")
ROOM_COUNT_PATH = str(RESULTS_DIR / "contagem_quarto.txt")
BATHROOM_STATUS_PATH = str(RESULTS_DIR / "status_banheiro.txt")

# Configurações do servidor MJPEG
MJPEG_HOST = os.getenv("MJPEG_HOST", "0.0.0.0")
MJPEG_PORT = int(os.getenv("MJPEG_PORT", "8888"))
MJPEG_URL = os.getenv("MJPEG_URL", f"http://localhost:{MJPEG_PORT}/video")

# Configurações do Streamlit
STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "0.0.0.0")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "3"))  # segundos

# Configurações do Banco de Dados PostgreSQL
DB_NAME = os.getenv("DB_NAME", "iasenior")
DB_USER = os.getenv("DB_USER", "iasenior")
DB_PASSWORD = os.getenv("DB_PASSWORD", "iasenior")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_ENABLED = os.getenv("DB_ENABLED", "true").lower() == "true"

# Configurações de Notificações
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
NOTIFICATION_EMAILS = os.getenv("NOTIFICATION_EMAILS", "")  # Separado por vírgula

