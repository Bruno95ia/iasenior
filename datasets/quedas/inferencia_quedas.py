"""
Sistema de inferência com modelo treinado customizado.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ultralytics import YOLO
from config import MODEL_PATH

MODELOS_DIR = Path(__file__).parent.parent.parent / "modelos"
MODELO_CUSTOM = MODELOS_DIR / "queda_custom.pt"

class DetectorQuedaCustomizado:
    """
    Detector de quedas usando modelo YOLOv8 customizado treinado.
    """
    
    def __init__(self, modelo_path=None, conf_threshold=0.05):
        """
        Inicializa detector.
        
        Args:
            modelo_path: Caminho do modelo customizado (None = usar padrão)
            conf_threshold: Threshold de confiança
        """
        if modelo_path is None:
            modelo_path = MODELO_CUSTOM
        
        if not Path(modelo_path).exists():
            print(f"⚠️  Modelo customizado não encontrado: {modelo_path}")
            print(f"   Usando modelo padrão: {MODEL_PATH}")
            modelo_path = MODEL_PATH
        
        self.model = YOLO(str(modelo_path))
        self.conf_threshold = conf_threshold
        self.modelo_custom = Path(modelo_path) == MODELO_CUSTOM
        
        if self.modelo_custom:
            print(f"✅ Usando modelo customizado: {modelo_path}")
        else:
            print(f"ℹ️  Usando modelo padrão: {modelo_path}")
    
    def detectar(self, frame, mostrar_todas_deteccoes=False):
        """
        Detecta quedas em um frame.
        
        Args:
            frame: Frame numpy (BGR)
            mostrar_todas_deteccoes: Se True, mostra todas as detecções mesmo abaixo do threshold
        
        Returns:
            (tem_queda, deteccoes, frame_anotado)
            - tem_queda: bool
            - deteccoes: lista de detecções
            - frame_anotado: frame com anotações
        """
        # Converter BGR para RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Inferência com threshold baixo para ver todas as detecções
        threshold_inferencia = 0.1 if mostrar_todas_deteccoes else self.conf_threshold
        results = self.model.predict(
            frame_rgb,
            conf=threshold_inferencia,
            verbose=False
        )
        
        deteccoes = []
        tem_queda = False
        
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    # Filtrar por threshold se não mostrar todas
                    if not mostrar_todas_deteccoes and conf < self.conf_threshold:
                        continue
                    
                    # Classe 0 = queda (no modelo customizado)
                    if cls == 0 or (not self.modelo_custom and self._eh_queda_heuristica(box, frame)):
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        deteccoes.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confianca': conf,
                            'classe': cls
                        })
                        tem_queda = True
        
        # Anotar frame
        frame_anotado = frame.copy()
        for det in deteccoes:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confianca']
            
            # Desenhar bbox
            cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(
                frame_anotado,
                f"Queda {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
        
        return tem_queda, deteccoes, frame_anotado
    
    def _eh_queda_heuristica(self, box, frame):
        """Heurística de queda (fallback se não usar modelo customizado)"""
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        height = y2 - y1
        width = x2 - x1
        
        if width > 0:
            aspect_ratio = height / width
            # Pessoa caída geralmente tem aspect_ratio < 0.7
            return aspect_ratio < 0.7
        
        return False

def testar_video(video_path, modelo_path=None, conf_threshold=0.5):
    """Testa detecção em um vídeo"""
    # Converter para Path se for string
    video_path = Path(video_path)
    
    detector = DetectorQuedaCustomizado(modelo_path, conf_threshold)
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Erro ao abrir vídeo: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    output_path = video_path.parent / f"{video_path.stem}_detectado.mp4"
    out = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )
    
    frame_count = 0
    quedas_detectadas = 0
    
    print(f"🎬 Processando vídeo: {video_path.name}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        tem_queda, deteccoes, frame_anotado = detector.detectar(frame)
        
        if tem_queda:
            quedas_detectadas += 1
            cv2.putText(
                frame_anotado,
                "QUEDA DETECTADA!",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )
        
        out.write(frame_anotado)
        frame_count += 1
        
        if frame_count % 30 == 0:
            print(f"   Frame {frame_count} - Quedas: {quedas_detectadas}")
    
    cap.release()
    out.release()
    
    print(f"\n✅ Vídeo processado: {output_path}")
    print(f"   Total frames: {frame_count}")
    print(f"   Quedas detectadas: {quedas_detectadas}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar detecção de quedas em vídeo")
    parser.add_argument("video", type=str, help="Caminho do vídeo")
    parser.add_argument("--modelo", type=str, default=None, help="Caminho do modelo")
    parser.add_argument("--conf", type=float, default=0.05, help="Threshold de confiança (padrão: 0.05 para modelo customizado)")
    
    args = parser.parse_args()
    
    testar_video(args.video, args.modelo, args.conf)

