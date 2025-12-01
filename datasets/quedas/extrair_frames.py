"""
Extrai frames de vídeos de quedas para anotação.
"""

import cv2
import os
from pathlib import Path
from tqdm import tqdm
import json

VIDEOS_DIR = Path(__file__).parent / "videos"
FRAMES_DIR = Path(__file__).parent / "frames"
FRAMES_DIR.mkdir(exist_ok=True)

def extrair_frames(video_path, output_dir, intervalo_segundos=1.0, max_frames=None):
    """
    Extrai frames de um vídeo.
    
    Args:
        video_path: Caminho do vídeo
        output_dir: Diretório de saída
        intervalo_segundos: Intervalo entre frames (segundos)
        max_frames: Máximo de frames a extrair (None = todos)
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"❌ Erro ao abrir vídeo: {video_path}")
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracao = total_frames / fps if fps > 0 else 0
    
    intervalo_frames = int(fps * intervalo_segundos) if fps > 0 else 30
    
    video_name = video_path.stem
    frames_extraidos = []
    frame_count = 0
    frames_salvos = 0
    
    print(f"\n📹 Processando: {video_path.name}")
    print(f"   FPS: {fps:.2f}, Duração: {duracao:.2f}s, Total frames: {total_frames}")
    
    with tqdm(total=min(total_frames, max_frames * intervalo_frames) if max_frames else total_frames, 
              desc=f"Extraindo frames") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % intervalo_frames == 0:
                timestamp = frame_count / fps if fps > 0 else frame_count
                frame_filename = f"{video_name}_frame_{frames_salvos:05d}_t{timestamp:.2f}s.jpg"
                frame_path = output_dir / frame_filename
                
                cv2.imwrite(str(frame_path), frame)
                frames_extraidos.append({
                    'frame_path': str(frame_path),
                    'video': video_path.name,
                    'frame_number': frame_count,
                    'timestamp': timestamp
                })
                
                frames_salvos += 1
                if max_frames and frames_salvos >= max_frames:
                    break
            
            frame_count += 1
            pbar.update(1)
    
    cap.release()
    return frames_extraidos

def processar_todos_videos():
    """Processa todos os vídeos na pasta videos/"""
    videos = list(VIDEOS_DIR.glob("*.mp4")) + list(VIDEOS_DIR.glob("*.avi")) + list(VIDEOS_DIR.glob("*.mov"))
    
    if not videos:
        print("❌ Nenhum vídeo encontrado em", VIDEOS_DIR)
        return
    
    print(f"📹 Encontrados {len(videos)} vídeos")
    
    todos_frames = []
    
    for video in videos:
        frames = extrair_frames(
            video, 
            FRAMES_DIR, 
            intervalo_segundos=0.5,  # Frame a cada 0.5 segundos
            max_frames=200  # Máximo 200 frames por vídeo
        )
        todos_frames.extend(frames)
    
    # Salvar índice de frames
    index_path = FRAMES_DIR / "frames_index.json"
    with open(index_path, 'w') as f:
        json.dump(todos_frames, f, indent=2)
    
    print(f"\n✅ Extraídos {len(todos_frames)} frames totais")
    print(f"📁 Frames salvos em: {FRAMES_DIR}")
    print(f"📋 Índice salvo em: {index_path}")

if __name__ == "__main__":
    processar_todos_videos()

