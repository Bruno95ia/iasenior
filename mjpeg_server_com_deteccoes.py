"""
Servidor MJPEG com Detecções YOLO - IASenior
Stream MJPEG com inferência YOLO em tempo real, incluindo detecções de quedas.
"""

from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import logging
import time
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    RTSP_URL, MJPEG_HOST, MJPEG_PORT, LOGS_DIR,
    MODEL_PATH, CONFIDENCE_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT,
    PERSON_CLASS_ID, FALL_DETECTION_ENABLED, TRACKING_ENABLED,
    ROOM_COUNT_ENABLED, ROOM_USE_AREA, ROOM_AREA,
    BATHROOM_MONITORING_ENABLED, BATHROOM_TIME_LIMIT_SECONDS, BATHROOM_AREA
)

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics não disponível")

# Importar detector customizado se disponível
try:
    sys.path.insert(0, str(Path(__file__).parent / "datasets" / "quedas"))
    from inferencia_quedas import DetectorQuedaCustomizado
    DETECTOR_CUSTOM_DISPONIVEL = True
except ImportError:
    DETECTOR_CUSTOM_DISPONIVEL = False

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
CORS(app)  # Permitir CORS para acesso do dashboard

# Variáveis globais
cap = None
model = None
detector_queda_custom = None
person_tracker = {}
bathroom_people = {}
room_people_count = 0
frame_count = 0
RECONNECT_DELAY = 5
MAX_RECONNECT_ATTEMPTS = 10

# Calcular áreas em pixels
bathroom_area_px = (
    int(BATHROOM_AREA[0] * FRAME_WIDTH),
    int(BATHROOM_AREA[1] * FRAME_HEIGHT),
    int(BATHROOM_AREA[2] * FRAME_WIDTH),
    int(BATHROOM_AREA[3] * FRAME_HEIGHT)
)
room_area_px = (
    int(ROOM_AREA[0] * FRAME_WIDTH),
    int(ROOM_AREA[1] * FRAME_HEIGHT),
    int(ROOM_AREA[2] * FRAME_WIDTH),
    int(ROOM_AREA[3] * FRAME_HEIGHT)
)


def inicializar_modelo():
    """Inicializa modelo YOLO."""
    global model, detector_queda_custom
    
    if not YOLO_AVAILABLE:
        logger.warning("⚠️ YOLO não disponível, servindo stream sem detecções")
        return False
    
    try:
        logger.info(f"🧠 Carregando modelo YOLO: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        logger.info("✅ Modelo YOLO carregado")
        
        # Tentar carregar detector customizado de quedas
        if DETECTOR_CUSTOM_DISPONIVEL:
            try:
                modelos_dir = Path(__file__).parent / "modelos"
                modelo_custom = modelos_dir / "queda_custom.pt"
                if modelo_custom.exists():
                    detector_queda_custom = DetectorQuedaCustomizado(
                        modelo_path=str(modelo_custom),
                        conf_threshold=0.05  # Threshold baixo para modelo customizado
                    )
                    logger.info("✅ Detector customizado de quedas carregado")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar detector customizado: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao carregar modelo: {e}")
        return False


def inicializar_captura():
    """Inicializa captura RTSP."""
    global cap
    
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    
    try:
        logger.info(f"🎥 Conectando ao stream RTSP: {RTSP_URL}")
        cap = cv2.VideoCapture(RTSP_URL)
        
        if not cap.isOpened():
            logger.error(f"❌ Não foi possível abrir stream: {RTSP_URL}")
            return False
        
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("✅ Stream RTSP conectado")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        return False


def reconectar():
    """Tenta reconectar ao stream."""
    for attempt in range(MAX_RECONNECT_ATTEMPTS):
        logger.info(f"🔄 Tentativa {attempt + 1}/{MAX_RECONNECT_ATTEMPTS}")
        if inicializar_captura():
            return True
        if attempt < MAX_RECONNECT_ATTEMPTS - 1:
            time.sleep(RECONNECT_DELAY)
    return False


def centro_box_na_area(box_xyxy, area):
    """Verifica se centro da bbox está na área."""
    x1, y1, x2, y2 = box_xyxy
    centro_x = (x1 + x2) / 2
    centro_y = (y1 + y2) / 2
    ax1, ay1, ax2, ay2 = area
    return ax1 <= centro_x <= ax2 and ay1 <= centro_y <= ay2


def processar_frame_com_deteccoes(frame):
    """Processa frame com YOLO e retorna frame anotado."""
    global frame_count, room_people_count, bathroom_people
    
    if model is None:
        return frame  # Retornar frame original se modelo não disponível
    
    try:
        # Inferência YOLO
        if TRACKING_ENABLED:
            results = model.track(
                frame,
                conf=CONFIDENCE_THRESHOLD,
                verbose=False,
                persist=True
            )
        else:
            results = model.predict(
                frame,
                conf=CONFIDENCE_THRESHOLD,
                verbose=False,
                stream=False
            )
        
        # Anotar frame com detecções
        annotated = results[0].plot()
        
        # Desenhar áreas
        if ROOM_USE_AREA:
            cv2.rectangle(
                annotated,
                (room_area_px[0], room_area_px[1]),
                (room_area_px[2], room_area_px[3]),
                (0, 255, 0),
                2
            )
            cv2.putText(
                annotated,
                "Quarto",
                (room_area_px[0] + 5, room_area_px[1] + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        
        cv2.rectangle(
            annotated,
            (bathroom_area_px[0], bathroom_area_px[1]),
            (bathroom_area_px[2], bathroom_area_px[3]),
            (255, 0, 0),
            2
        )
        cv2.putText(
            annotated,
            "Banheiro",
            (bathroom_area_px[0] + 5, bathroom_area_px[1] + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )
        
        # Contar pessoas no quarto
        pessoas_quarto = set()
        pessoas_banheiro_atual = {}
        queda_detectada = False
        current_time = time.time()
        
        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue
            
            for box in boxes:
                cls = int(box.cls[0])
                if cls != PERSON_CLASS_ID:
                    continue
                
                conf = float(box.conf[0])
                if conf < CONFIDENCE_THRESHOLD:
                    continue
                
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Detecção de queda (usar detector customizado se disponível)
                if FALL_DETECTION_ENABLED:
                    if detector_queda_custom:
                        tem_queda, _, _ = detector_queda_custom.detectar(frame)
                        if tem_queda:
                            queda_detectada = True
                            cv2.putText(
                                annotated,
                                "QUEDA DETECTADA!",
                                (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255),
                                3
                            )
                
                # Contagem quarto
                if ROOM_COUNT_ENABLED:
                    if not ROOM_USE_AREA or centro_box_na_area((x1, y1, x2, y2), room_area_px):
                        if TRACKING_ENABLED and hasattr(box, 'id') and box.id is not None:
                            track_id = int(box.id[0])
                            pessoas_quarto.add(track_id)
                        else:
                            pos_id = f"{int(x1/10)}_{int(y1/10)}"
                            pessoas_quarto.add(pos_id)
                
                # Monitoramento banheiro
                if BATHROOM_MONITORING_ENABLED:
                    if centro_box_na_area((x1, y1, x2, y2), bathroom_area_px):
                        if TRACKING_ENABLED and hasattr(box, 'id') and box.id is not None:
                            track_id = int(box.id[0])
                        else:
                            track_id = f"temp_{int(x1/10)}_{int(y1/10)}"
                        
                        if track_id not in bathroom_people:
                            bathroom_people[track_id] = current_time
                        
                        pessoas_banheiro_atual[track_id] = bathroom_people[track_id]
        
        # Remover pessoas que saíram do banheiro
        pessoas_sairam = set(bathroom_people.keys()) - set(pessoas_banheiro_atual.keys())
        for track_id in pessoas_sairam:
            del bathroom_people[track_id]
        
        room_people_count = len(pessoas_quarto)
        
        # Adicionar informações no frame
        cv2.putText(
            annotated,
            f"Pessoas no Quarto: {room_people_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        cv2.putText(
            annotated,
            f"Pessoas no Banheiro: {len(pessoas_banheiro_atual)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )
        
        frame_count += 1
        
        return annotated
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar frame: {e}")
        return frame


def gerar_frames():
    """Generator que produz frames MJPEG com detecções."""
    global cap
    
    if not inicializar_captura():
        logger.error("❌ Falha ao inicializar captura")
        yield None
        return
    
    frames_erro = 0
    MAX_FRAMES_ERRO = 10
    
    while True:
        try:
            if cap is None or not cap.isOpened():
                logger.warning("⚠️ Stream desconectado. Reconectando...")
                if not reconectar():
                    break
                frames_erro = 0
            
            sucesso, frame = cap.read()
            
            if not sucesso:
                frames_erro += 1
                if frames_erro >= MAX_FRAMES_ERRO:
                    if not reconectar():
                        break
                    frames_erro = 0
                time.sleep(0.1)
                continue
            
            frames_erro = 0
            
            # Processar frame com detecções
            frame_processado = processar_frame_com_deteccoes(frame)
            
            # Codificar como JPEG
            try:
                _, buffer = cv2.imencode('.jpg', frame_processado, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                logger.error(f"❌ Erro ao codificar frame: {e}")
                time.sleep(0.1)
                continue
                
        except Exception as e:
            logger.error(f"❌ Erro no generator: {e}")
            time.sleep(1)
            if not reconectar():
                break


@app.route('/video')
def video():
    """Endpoint para streaming MJPEG com detecções."""
    return Response(
        gerar_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/status')
def status():
    """Endpoint para obter status atual."""
    global cap, room_people_count, bathroom_people, frame_count
    
    status_banheiro = {
        'pessoas_no_banheiro': len(bathroom_people),
        'pessoas': []
    }
    
    current_time = time.time()
    for track_id, entry_time in bathroom_people.items():
        tempo = current_time - entry_time
        status_banheiro['pessoas'].append({
            'track_id': str(track_id),
            'tempo_segundos': int(tempo),
            'alerta': tempo > BATHROOM_TIME_LIMIT_SECONDS
        })
    
    return jsonify({
        'stream_connected': cap.isOpened() if cap else False,
        'model_loaded': model is not None,
        'pessoas_quarto': room_people_count,
        'status_banheiro': status_banheiro,
        'frame_count': frame_count,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check."""
    global cap, model
    return jsonify({
        'status': 'healthy' if (cap and cap.isOpened() and model) else 'unhealthy',
        'stream_connected': cap.isOpened() if cap else False,
        'model_loaded': model is not None
    }), 200 if (cap and cap.isOpened()) else 503


@app.route('/')
def index():
    """Página inicial."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MJPEG Stream com Detecções - IASenior</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            img { max-width: 100%; border: 2px solid #ddd; border-radius: 5px; }
            .status { margin-top: 20px; padding: 15px; background: #e8f5e9; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎥 MJPEG Stream com Detecções YOLO</h1>
            <p>Stream disponível em: <a href="/video">/video</a></p>
            <p>Status: <a href="/status">/status</a></p>
            <p>Health: <a href="/health">/health</a></p>
            <hr>
            <h2>Stream ao vivo com detecções:</h2>
            <img src="/video" alt="Stream de vídeo">
            <div class="status" id="status">Carregando status...</div>
        </div>
        <script>
            setInterval(async () => {
                try {
                    const res = await fetch('/status');
                    const data = await res.json();
                    document.getElementById('status').innerHTML = `
                        <strong>Status:</strong><br>
                        Stream: ${data.stream_connected ? '✅ Conectado' : '❌ Desconectado'}<br>
                        Modelo: ${data.model_loaded ? '✅ Carregado' : '❌ Não carregado'}<br>
                        Pessoas no Quarto: ${data.pessoas_quarto}<br>
                        Pessoas no Banheiro: ${data.status_banheiro.pessoas_no_banheiro}<br>
                        Frames processados: ${data.frame_count}
                    `;
                } catch (e) {
                    document.getElementById('status').innerHTML = 'Erro ao carregar status';
                }
            }, 2000);
        </script>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor MJPEG com detecções YOLO...")
    
    # Inicializar modelo
    if not inicializar_modelo():
        logger.warning("⚠️ Continuando sem modelo YOLO")
    
    logger.info(f"🌐 Servidor em {MJPEG_HOST}:{MJPEG_PORT}")
    logger.info(f"📡 Stream RTSP: {RTSP_URL}")
    
    try:
        app.run(
            host=MJPEG_HOST,
            port=MJPEG_PORT,
            threaded=True,
            debug=False
        )
    except Exception as e:
        logger.critical(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
    finally:
        if cap:
            cap.release()

