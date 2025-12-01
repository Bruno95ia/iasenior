#!/usr/bin/env python3
"""
Script para testar detecções com diferentes thresholds e mostrar detalhes.
"""

import sys
from pathlib import Path
import cv2

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from inferencia_quedas import DetectorQuedaCustomizado

def testar_com_thresholds(video_path, thresholds=[0.1, 0.2, 0.3, 0.4, 0.5]):
    """Testa detecção com múltiplos thresholds"""
    video_path = Path(video_path)
    
    print("=" * 70)
    print(f"🎬 Testando vídeo: {video_path.name}")
    print("=" * 70)
    print()
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Erro ao abrir vídeo: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"📊 Total de frames: {total_frames}")
    print()
    
    # Testar cada threshold
    for threshold in thresholds:
        print(f"🔍 Testando com threshold: {threshold}")
        print("-" * 70)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Voltar ao início
        detector = DetectorQuedaCustomizado(conf_threshold=threshold)
        
        frame_count = 0
        quedas_detectadas = 0
        deteccoes_por_frame = []
        
        # Processar alguns frames (primeiros 100 ou todos se menos)
        max_frames = min(100, total_frames)
        
        for i in range(max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            tem_queda, deteccoes, _ = detector.detectar(frame)
            
            if tem_queda:
                quedas_detectadas += 1
                confs = [d['confianca'] for d in deteccoes]
                deteccoes_por_frame.append({
                    'frame': frame_count,
                    'deteccoes': len(deteccoes),
                    'confs': confs,
                    'max_conf': max(confs) if confs else 0
                })
            
            frame_count += 1
        
        # Estatísticas
        print(f"   Frames processados: {frame_count}")
        print(f"   Frames com queda detectada: {quedas_detectadas} ({quedas_detectadas/frame_count*100:.1f}%)")
        
        if deteccoes_por_frame:
            confs_todas = [d['max_conf'] for d in deteccoes_por_frame]
            print(f"   Confiança média: {sum(confs_todas)/len(confs_todas):.4f}")
            print(f"   Confiança mínima: {min(confs_todas):.4f}")
            print(f"   Confiança máxima: {max(confs_todas):.4f}")
            print(f"   Primeiras detecções (frame, confiança):")
            for det in deteccoes_por_frame[:5]:
                print(f"      Frame {det['frame']}: {det['max_conf']:.4f}")
        else:
            print(f"   ⚠️  Nenhuma queda detectada com threshold {threshold}")
        
        print()
    
    cap.release()
    
    print("=" * 70)
    print("💡 Recomendação:")
    print("   - Se nenhuma detecção: threshold muito alto ou modelo precisa mais treino")
    print("   - Se muitas detecções falsas: threshold muito baixo")
    print("   - Use o threshold que dá melhor balance entre detecções e precisão")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar detecções com diferentes thresholds")
    parser.add_argument("video", type=str, help="Caminho do vídeo")
    parser.add_argument("--thresholds", type=float, nargs="+", 
                       default=[0.1, 0.2, 0.3, 0.4, 0.5],
                       help="Thresholds para testar")
    
    args = parser.parse_args()
    
    testar_com_thresholds(args.video, args.thresholds)

