"""
Script de inferência com YOLO para detecção em tempo real via RTSP.
Melhorado com logging, tratamento de erros e configuração centralizada.
"""

import cv2
import mss
import numpy as np
import subprocess
import time
import logging
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from ultralytics import YOLO

# Adicionar diretório raiz ao path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    MONITOR_IDX, FRAME_WIDTH, FRAME_HEIGHT, FPS, RTSP_URL,
    MODEL_PATH, CONFIDENCE_THRESHOLD, RESULTS_DIR, LOGS_DIR,
    FRAME_PATH, STATUS_PATH, PERSON_CLASS_ID, FALL_DETECTION_ENABLED,
    TRACKING_ENABLED, ROOM_COUNT_ENABLED, ROOM_USE_AREA, ROOM_AREA,
    BATHROOM_MONITORING_ENABLED, BATHROOM_TIME_LIMIT_SECONDS, BATHROOM_AREA,
    ROOM_COUNT_PATH, BATHROOM_STATUS_PATH, NOTIFICATIONS_ENABLED
)

# Importar detector customizado se disponível
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "datasets" / "quedas"))
    from inferencia_quedas import DetectorQuedaCustomizado
    DETECTOR_CUSTOM_DISPONIVEL = True
except ImportError:
    DETECTOR_CUSTOM_DISPONIVEL = False
    logger.info("Detector customizado não disponível, usando heurística padrão")

# Importar sistema de notificações
if NOTIFICATIONS_ENABLED:
    try:
        from notificacoes import get_notificacao_manager
        notificacao_manager = get_notificacao_manager()
    except ImportError:
        notificacao_manager = None
        logger.warning("Sistema de notificações não disponível")
else:
    notificacao_manager = None

# Configurar logging
log_file = LOGS_DIR / "inferencia.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class StreamInferenciaRTSP:
    """Classe para gerenciar inferência e transmissão RTSP."""
    
    def __init__(self):
        self.model = None
        self.process = None
        self.sct = None
        self.monitor = None
        self.frame_count = 0
        
        # Detector customizado de quedas (se disponível)
        self.detector_queda_custom = None
        if DETECTOR_CUSTOM_DISPONIVEL:
            try:
                modelos_dir = Path(__file__).parent.parent.parent / "modelos"
                modelo_custom = modelos_dir / "queda_custom.pt"
                if modelo_custom.exists():
                    self.detector_queda_custom = DetectorQuedaCustomizado(
                        modelo_path=str(modelo_custom),
                        conf_threshold=CONFIDENCE_THRESHOLD
                    )
                    logger.info(f"✅ Usando detector customizado: {modelo_custom}")
                else:
                    logger.info("ℹ️  Modelo customizado não encontrado, usando heurística padrão")
            except Exception as e:
                logger.warning(f"⚠️  Erro ao carregar detector customizado: {e}")
        self.start_time = None
        self.running = False
        
        # Tracking de pessoas
        self.person_tracker = {}  # {track_id: {entry_time, area, last_seen}}
        self.next_track_id = 1
        
        # Área do banheiro (em pixels)
        self.bathroom_area_px = None
        self.room_area_px = None
        
        # Pessoas atualmente no banheiro
        self.bathroom_people = {}  # {track_id: entry_time}
        
        # Contador de pessoas no quarto
        self.room_people_count = 0
        
    def inicializar_modelo(self):
        """Carrega o modelo YOLO."""
        try:
            logger.info(f"🧠 Carregando modelo YOLO de {MODEL_PATH}...")
            if not Path(MODEL_PATH).exists():
                logger.error(f"❌ Modelo não encontrado em {MODEL_PATH}")
                raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
            
            self.model = YOLO(MODEL_PATH)
            logger.info("✅ Modelo carregado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}", exc_info=True)
            raise
    
    def inicializar_captura(self):
        """Inicializa a captura de tela."""
        try:
            logger.info(f"📺 Inicializando captura do monitor {MONITOR_IDX}...")
            self.sct = mss.mss()
            if MONITOR_IDX >= len(self.sct.monitors):
                logger.error(f"❌ Monitor {MONITOR_IDX} não existe. Monitores disponíveis: {len(self.sct.monitors) - 1}")
                raise ValueError(f"Monitor {MONITOR_IDX} inválido")
            
            self.monitor = self.sct.monitors[MONITOR_IDX]
            logger.info(f"✅ Captura configurada para monitor {MONITOR_IDX}")
            
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
    
    def inicializar_ffmpeg(self):
        """Inicializa o processo FFmpeg para transmissão RTSP."""
        try:
            logger.info(f"🎥 Iniciando transmissão via FFmpeg para {RTSP_URL}...")
            command = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', f'{FRAME_WIDTH}x{FRAME_HEIGHT}',
                '-r', str(FPS),
                '-i', '-',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-tune', 'zerolatency',
                '-f', 'rtsp',
                RTSP_URL
            ]
            
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("✅ FFmpeg iniciado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar FFmpeg: {e}", exc_info=True)
            raise
    
    def detectar_queda(self, results, frame=None):
        """
        Detecta possíveis quedas usando modelo customizado ou heurística.
        Retorna True se uma queda foi detectada.
        """
        if not FALL_DETECTION_ENABLED:
            return False
        
        # Tentar usar detector customizado primeiro
        if self.detector_queda_custom and frame is not None:
            try:
                tem_queda, deteccoes, _ = self.detector_queda_custom.detectar(frame)
                if tem_queda:
                    logger.info(f"🚨 Queda detectada pelo modelo customizado! Confiança: {deteccoes[0]['confianca']:.2f}")
                    return True
            except Exception as e:
                logger.warning(f"⚠️  Erro no detector customizado, usando heurística: {e}")
        
        # Fallback para heurística padrão
        try:
            for result in results:
                boxes = result.boxes
                if boxes is None or len(boxes) == 0:
                    continue
                
                for box in boxes:
                    # Verificar se é uma pessoa
                    cls = int(box.cls[0])
                    if cls != PERSON_CLASS_ID:
                        continue
                    
                    conf = float(box.conf[0])
                    if conf < CONFIDENCE_THRESHOLD:
                        continue
                    
                    # Obter coordenadas da bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Calcular altura e largura
                    height = y2 - y1
                    width = x2 - x1
                    
                    # Calcular proporção (altura/largura)
                    if width > 0:
                        aspect_ratio = height / width
                        
                        # Uma pessoa caída geralmente tem aspect_ratio < 0.7
                        # e está na parte inferior da imagem
                        frame_center_y = FRAME_HEIGHT / 2
                        box_center_y = (y1 + y2) / 2
                        
                        if aspect_ratio < 0.7 and box_center_y > frame_center_y:
                            return True
            
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erro ao detectar queda: {e}")
            return False
    
    def ponto_na_area(self, x, y, area):
        """Verifica se um ponto (x, y) está dentro de uma área."""
        x1, y1, x2, y2 = area
        return x1 <= x <= x2 and y1 <= y <= y2
    
    def centro_box_na_area(self, box_xyxy, area):
        """Verifica se o centro de uma bounding box está dentro de uma área."""
        x1, y1, x2, y2 = box_xyxy
        centro_x = (x1 + x2) / 2
        centro_y = (y1 + y2) / 2
        return self.ponto_na_area(centro_x, centro_y, area)
    
    def contar_pessoas_quarto(self, results):
        """Conta pessoas detectadas no quarto."""
        if not ROOM_COUNT_ENABLED:
            return 0
        
        try:
            pessoas_no_quarto = set()
            
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
                    
                    # Se não usar área específica, conta todas as pessoas
                    if not ROOM_USE_AREA:
                        # Usa track_id se disponível, senão usa posição como identificador temporário
                        if TRACKING_ENABLED and hasattr(box, 'id') and box.id is not None:
                            track_id = int(box.id[0])
                            pessoas_no_quarto.add(track_id)
                        else:
                            # Usa posição aproximada como identificador
                            pos_id = f"{int(x1/10)}_{int(y1/10)}"
                            pessoas_no_quarto.add(pos_id)
                    else:
                        # Verifica se está na área do quarto
                        if self.centro_box_na_area((x1, y1, x2, y2), self.room_area_px):
                            if TRACKING_ENABLED and hasattr(box, 'id') and box.id is not None:
                                track_id = int(box.id[0])
                                pessoas_no_quarto.add(track_id)
                            else:
                                pos_id = f"{int(x1/10)}_{int(y1/10)}"
                                pessoas_no_quarto.add(pos_id)
            
            return len(pessoas_no_quarto)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao contar pessoas no quarto: {e}")
            return 0
    
    def monitorar_banheiro(self, results):
        """Monitora pessoas no banheiro e detecta tempo > limite."""
        if not BATHROOM_MONITORING_ENABLED:
            return {}, []
        
        try:
            pessoas_banheiro_atual = {}
            alertas = []
            current_time = time.time()
            
            # Primeiro, verifica pessoas detectadas no banheiro
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
                    
                    # Verifica se está na área do banheiro
                    if self.centro_box_na_area((x1, y1, x2, y2), self.bathroom_area_px):
                        if TRACKING_ENABLED and hasattr(box, 'id') and box.id is not None:
                            track_id = int(box.id[0])
                        else:
                            # Usa posição como identificador temporário
                            track_id = f"temp_{int(x1/10)}_{int(y1/10)}"
                        
                        # Se é nova pessoa no banheiro
                        if track_id not in self.bathroom_people:
                            self.bathroom_people[track_id] = current_time
                            logger.info(f"🚿 Pessoa {track_id} entrou no banheiro")
                        
                        pessoas_banheiro_atual[track_id] = self.bathroom_people[track_id]
            
            # Verifica pessoas que saíram do banheiro e remove
            pessoas_sairam = set(self.bathroom_people.keys()) - set(pessoas_banheiro_atual.keys())
            for track_id in pessoas_sairam:
                tempo_no_banheiro = current_time - self.bathroom_people[track_id]
                logger.info(f"🚿 Pessoa {track_id} saiu do banheiro após {tempo_no_banheiro:.1f}s")
                del self.bathroom_people[track_id]
            
            # Verifica alertas de tempo excedido
            for track_id, entry_time in pessoas_banheiro_atual.items():
                tempo_no_banheiro = current_time - entry_time
                
                if tempo_no_banheiro > BATHROOM_TIME_LIMIT_SECONDS:
                    minutos = int(tempo_no_banheiro // 60)
                    segundos = int(tempo_no_banheiro % 60)
                    alerta = {
                        'track_id': track_id,
                        'tempo_minutos': minutos,
                        'tempo_segundos': segundos,
                        'timestamp': datetime.now().isoformat()
                    }
                    alertas.append(alerta)
                    
                    if len(alertas) == 1:  # Log apenas uma vez por ciclo
                        logger.warning(
                            f"⚠️ ALERTA: Pessoa {track_id} no banheiro há {minutos}min {segundos}s "
                            f"(limite: {BATHROOM_TIME_LIMIT_SECONDS//60}min)"
                        )
                        
                        # Enviar notificação por email
                        if notificacao_manager:
                            try:
                                # Evitar spam: só enviar se não enviou recentemente para este track_id
                                if not hasattr(self, '_notificacoes_banheiro'):
                                    self._notificacoes_banheiro = {}
                                
                                ultima_notif = self._notificacoes_banheiro.get(track_id, 0)
                                tempo_desde_ultima = time.time() - ultima_notif
                                
                                if tempo_desde_ultima > 600:  # 10 minutos entre notificações para mesmo track_id
                                    notificacao_manager.notificar_banheiro_tempo(
                                        track_id=track_id,
                                        tempo_minutos=minutos,
                                        tempo_segundos=segundos
                                    )
                                    self._notificacoes_banheiro[track_id] = time.time()
                            except Exception as e:
                                logger.error(f"Erro ao enviar notificação de banheiro: {e}")
            
            return pessoas_banheiro_atual, alertas
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao monitorar banheiro: {e}")
            return {}, []
    
    def salvar_informacoes(self, frame, status, contagem_quarto, status_banheiro):
        """Salva frame, status e informações de contagem/tempo."""
        try:
            # Salvar frame
            cv2.imwrite(FRAME_PATH, frame)
            
            # Salvar status geral
            with open(STATUS_PATH, 'w') as f:
                f.write(status)
            
            # Salvar contagem do quarto
            if ROOM_COUNT_ENABLED:
                with open(ROOM_COUNT_PATH, 'w') as f:
                    f.write(str(contagem_quarto))
            
            # Salvar status do banheiro
            if BATHROOM_MONITORING_ENABLED:
                with open(BATHROOM_STATUS_PATH, 'w') as f:
                    import json
                    json.dump(status_banheiro, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar informações: {e}")
    
    def desenhar_areas(self, frame):
        """Desenha áreas do quarto e banheiro no frame."""
        try:
            # Desenhar área do quarto (verde)
            if ROOM_USE_AREA:
                cv2.rectangle(
                    frame,
                    (self.room_area_px[0], self.room_area_px[1]),
                    (self.room_area_px[2], self.room_area_px[3]),
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    "Quarto",
                    (self.room_area_px[0] + 5, self.room_area_px[1] + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
            
            # Desenhar área do banheiro (azul)
            cv2.rectangle(
                frame,
                (self.bathroom_area_px[0], self.bathroom_area_px[1]),
                (self.bathroom_area_px[2], self.bathroom_area_px[3]),
                (255, 0, 0),
                2
            )
            cv2.putText(
                frame,
                "Banheiro",
                (self.bathroom_area_px[0] + 5, self.bathroom_area_px[1] + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )
        except Exception as e:
            logger.warning(f"⚠️ Erro ao desenhar áreas: {e}")
    
    def processar_frame(self, frame):
        """Processa um frame: inferência, detecção e transmissão."""
        try:
            # Inferência YOLO com tracking se habilitado
            if TRACKING_ENABLED:
                results = self.model.track(
                    frame,
                    conf=CONFIDENCE_THRESHOLD,
                    verbose=False,
                    persist=True
                )
            else:
                results = self.model.predict(
                    frame,
                    conf=CONFIDENCE_THRESHOLD,
                    verbose=False,
                    stream=False
                )
            
            # Anotar frame com detecções
            annotated = results[0].plot()
            
            # Desenhar áreas de quarto e banheiro
            self.desenhar_areas(annotated)
            
            # Detecção de queda (passa frame original para detector customizado)
            queda_detectada = self.detectar_queda(results, frame)
            status = "queda" if queda_detectada else "ok"
            
            # Enviar notificação de queda se detectada
            if queda_detectada and notificacao_manager:
                try:
                    # Evitar spam: só enviar se não enviou recentemente
                    if not hasattr(self, '_ultima_notificacao_queda'):
                        self._ultima_notificacao_queda = 0
                    
                    tempo_desde_ultima = time.time() - self._ultima_notificacao_queda
                    if tempo_desde_ultima > 300:  # 5 minutos entre notificações
                        notificacao_manager.notificar_queda(metadata={
                            'frame_count': self.frame_count,
                            'timestamp': datetime.now().isoformat()
                        })
                        self._ultima_notificacao_queda = time.time()
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação de queda: {e}")
            
            # Contagem de pessoas no quarto
            contagem_quarto = self.contar_pessoas_quarto(results)
            self.room_people_count = contagem_quarto
            
            # Monitoramento do banheiro
            pessoas_banheiro, alertas_banheiro = self.monitorar_banheiro(results)
            
            # Preparar status do banheiro
            status_banheiro = {
                'pessoas_no_banheiro': len(pessoas_banheiro),
                'alertas': alertas_banheiro,
                'pessoas': []
            }
            
            current_time = time.time()
            for track_id, entry_time in pessoas_banheiro.items():
                tempo_decorrido = current_time - entry_time
                minutos = int(tempo_decorrido // 60)
                segundos = int(tempo_decorrido % 60)
                
                status_banheiro['pessoas'].append({
                    'track_id': str(track_id),
                    'tempo_minutos': minutos,
                    'tempo_segundos': segundos,
                    'alerta': tempo_decorrido > BATHROOM_TIME_LIMIT_SECONDS
                })
            
            # Adicionar informações no frame
            cv2.putText(
                annotated,
                f"Pessoas no Quarto: {contagem_quarto}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            cv2.putText(
                annotated,
                f"Pessoas no Banheiro: {len(pessoas_banheiro)}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )
            
            if alertas_banheiro:
                for i, alerta in enumerate(alertas_banheiro):
                    cv2.putText(
                        annotated,
                        f"ALERTA: Pessoa no banheiro > {BATHROOM_TIME_LIMIT_SECONDS//60}min!",
                        (10, 90 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
            
            # Salvar informações
            self.salvar_informacoes(annotated, status, contagem_quarto, status_banheiro)
            
            # Transmitir via FFmpeg
            if self.process and self.process.stdin:
                try:
                    self.process.stdin.write(annotated.tobytes())
                    self.process.stdin.flush()
                except BrokenPipeError:
                    logger.error("❌ Pipe do FFmpeg quebrado. Tentando reiniciar...")
                    raise
                except Exception as e:
                    logger.error(f"❌ Erro ao escrever no FFmpeg: {e}")
                    raise
            
            return status, contagem_quarto, len(pessoas_banheiro), len(alertas_banheiro)
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar frame: {e}", exc_info=True)
            return None, 0, 0, 0
    
    def executar(self):
        """Loop principal de captura e inferência."""
        try:
            self.inicializar_modelo()
            self.inicializar_captura()
            self.inicializar_ffmpeg()
            
            self.running = True
            self.start_time = time.time()
            frame_time = 1.0 / FPS
            
            logger.info("🚀 Iniciando loop de inferência...")
            logger.info(f"📊 Configuração: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {FPS}fps")
            
            while self.running:
                loop_start = time.time()
                
                # Capturar screenshot
                screenshot = np.array(self.sct.grab(self.monitor))
                frame = cv2.resize(screenshot[:, :, :3], (FRAME_WIDTH, FRAME_HEIGHT))
                
                # Processar frame
                resultado = self.processar_frame(frame)
                if resultado:
                    status, contagem_quarto, pessoas_banheiro, alertas = resultado
                else:
                    status, contagem_quarto, pessoas_banheiro, alertas = "erro", 0, 0, 0
                
                self.frame_count += 1
                
                # Log periódico
                if self.frame_count % (FPS * 5) == 0:  # A cada 5 segundos
                    elapsed = time.time() - self.start_time
                    fps_actual = self.frame_count / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"✅ {self.frame_count} frames processados | "
                        f"FPS: {fps_actual:.2f} | Status: {status} | "
                        f"Quarto: {contagem_quarto} pessoas | "
                        f"Banheiro: {pessoas_banheiro} pessoas | "
                        f"Alertas: {alertas}"
                    )
                
                # Controlar FPS
                elapsed_frame = time.time() - loop_start
                sleep_time = max(0, frame_time - elapsed_frame)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrompido manualmente pelo usuário.")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}", exc_info=True)
            self.running = False
        finally:
            self.finalizar()
    
    def finalizar(self):
        """Finaliza todos os recursos."""
        logger.info("🚪 Finalizando recursos...")
        self.running = False
        
        if self.process:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("✅ Processo FFmpeg encerrado.")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ FFmpeg não respondeu ao terminate. Forçando kill...")
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.error(f"❌ Erro ao finalizar FFmpeg: {e}")
        
        if self.sct:
            try:
                self.sct.close()
                logger.info("✅ Captura de tela encerrada.")
            except Exception as e:
                logger.error(f"❌ Erro ao finalizar captura: {e}")
        
        logger.info("✅ Transmissão encerrada.")


def main():
    """Função principal."""
    try:
        stream = StreamInferenciaRTSP()
        stream.executar()
    except Exception as e:
        logger.critical(f"❌ Erro crítico: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
