"""
Servidor MJPEG para streaming de vídeo via HTTP.
Melhorado com reconexão automática, logging e tratamento de erros.
"""

from flask import Flask, Response
import cv2
import logging
import time
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importar config
sys.path.insert(0, str(Path(__file__).parent))
from config import RTSP_URL, MJPEG_HOST, MJPEG_PORT, LOGS_DIR

# Configurar logging
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / "mjpeg_server.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variáveis globais para gerenciar a conexão
cap = None
RECONNECT_DELAY = 5  # segundos
MAX_RECONNECT_ATTEMPTS = 10


def inicializar_captura():
    """Inicializa ou reinicializa a captura RTSP."""
    global cap
    
    if cap is not None:
        try:
            cap.release()
        except Exception as e:
            logger.warning(f"⚠️ Erro ao liberar captura anterior: {e}")
    
    try:
        logger.info(f"🎥 Conectando ao stream RTSP: {RTSP_URL}")
        cap = cv2.VideoCapture(RTSP_URL)
        
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir o stream: {RTSP_URL}")
            return False
        
        # Configurar buffer mínimo para reduzir latência
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("✅ Stream RTSP conectado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao stream: {e}", exc_info=True)
        return False


def reconectar():
    """Tenta reconectar ao stream RTSP."""
    global cap
    
    for attempt in range(MAX_RECONNECT_ATTEMPTS):
        logger.info(f"🔄 Tentativa de reconexão {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}...")
        
        if inicializar_captura():
            return True
        
        if attempt < MAX_RECONNECT_ATTEMPTS - 1:
            time.sleep(RECONNECT_DELAY)
    
    logger.error("❌ Falha ao reconectar após todas as tentativas")
    return False


def gerar_frames():
    """
    Generator que produz frames do stream RTSP.
    Implementa reconexão automática em caso de falha.
    """
    global cap
    
    # Inicializar captura
    if not inicializar_captura():
        logger.error("❌ Falha ao inicializar captura na primeira tentativa")
        yield None
        return
    
    frames_erro = 0
    MAX_FRAMES_ERRO = 10
    
    while True:
        try:
            if cap is None or not cap.isOpened():
                logger.warning("⚠️ Stream desconectado. Tentando reconectar...")
                if not reconectar():
                    logger.error("❌ Não foi possível reconectar. Parando stream.")
                    break
                frames_erro = 0
            
            sucesso, frame = cap.read()
            
            if not sucesso:
                frames_erro += 1
                logger.warning(f"⚠️ Erro ao ler frame ({frames_erro}/{MAX_FRAMES_ERRO})")
                
                if frames_erro >= MAX_FRAMES_ERRO:
                    logger.error("❌ Muitos frames com erro. Tentando reconectar...")
                    if not reconectar():
                        break
                    frames_erro = 0
                
                time.sleep(0.1)  # Pequeno delay antes de tentar novamente
                continue
            
            frames_erro = 0  # Reset contador de erros
            
            # Codificar frame como JPEG
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
            except Exception as e:
                logger.error(f"❌ Erro ao codificar frame: {e}")
                time.sleep(0.1)
                continue
            
        except Exception as e:
            logger.error(f"❌ Erro no generator de frames: {e}", exc_info=True)
            time.sleep(1)
            
            # Tentar reconectar em caso de erro crítico
            if not reconectar():
                break


@app.route('/video')
def video():
    """Endpoint para streaming MJPEG."""
    return Response(
        gerar_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/health')
def health():
    """Endpoint de health check."""
    global cap
    
    status = {
        'status': 'healthy' if cap and cap.isOpened() else 'unhealthy',
        'stream_url': RTSP_URL,
        'connected': cap.isOpened() if cap else False
    }
    
    return status, 200 if status['connected'] else 503


@app.route('/')
def index():
    """Página inicial com instruções."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MJPEG Stream Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            img {{ max-width: 100%; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>🎥 MJPEG Stream Server</h1>
        <p>Stream disponível em: <a href="/video">/video</a></p>
        <p>Health check: <a href="/health">/health</a></p>
        <hr>
        <h2>Stream ao vivo:</h2>
        <img src="/video" alt="Stream de vídeo">
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    logger.info(f"🚀 Iniciando servidor MJPEG em {MJPEG_HOST}:{MJPEG_PORT}")
    logger.info(f"📡 Stream RTSP: {RTSP_URL}")
    
    try:
        app.run(
            host=MJPEG_HOST,
            port=MJPEG_PORT,
            threaded=True,
            debug=False
        )
    except Exception as e:
        logger.critical(f"❌ Erro ao iniciar servidor: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Limpeza final
        global cap
        if cap is not None:
            try:
                cap.release()
                logger.info("✅ Recursos liberados.")
            except Exception as e:
                logger.error(f"❌ Erro ao liberar recursos: {e}")
