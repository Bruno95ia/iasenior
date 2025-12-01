"""
Interface Streamlit para anotar quedas nos frames extraídos.
"""

import streamlit as st
import cv2
import json
from pathlib import Path
import numpy as np
from PIL import Image
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar helper de logo
try:
    from utils.logo_helper import exibir_logo_streamlit, logo_existe
    LOGO_AVAILABLE = logo_existe()
except ImportError:
    LOGO_AVAILABLE = False

FRAMES_DIR = Path(__file__).parent / "frames"
ANNOTATIONS_DIR = Path(__file__).parent / "annotations"
ANNOTATIONS_DIR.mkdir(exist_ok=True)

IMAGES_DIR = ANNOTATIONS_DIR / "images"
LABELS_DIR = ANNOTATIONS_DIR / "labels"
IMAGES_DIR.mkdir(exist_ok=True)
LABELS_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Anotação de Quedas", layout="wide")

# Carregar índice de frames
@st.cache_data
def carregar_frames():
    index_path = FRAMES_DIR / "frames_index.json"
    if not index_path.exists():
        return []
    
    with open(index_path, 'r') as f:
        return json.load(f)

frames = carregar_frames()

if not frames:
    st.error("❌ Nenhum frame encontrado. Execute primeiro: python extrair_frames.py")
    st.stop()

# Estado da sessão
if 'frame_index' not in st.session_state:
    st.session_state.frame_index = 0
if 'anotacoes' not in st.session_state:
    st.session_state.anotacoes = {}
if 'carregar_anotacoes_existentes' not in st.session_state:
    st.session_state.carregar_anotacoes_existentes = True

# Carregar anotações existentes
if st.session_state.carregar_anotacoes_existentes:
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    if annotations_file.exists():
        with open(annotations_file, 'r') as f:
            st.session_state.anotacoes = json.load(f)
    st.session_state.carregar_anotacoes_existentes = False

def salvar_anotacao(frame_info, tem_queda, bbox=None):
    """Salva anotação no formato YOLO"""
    frame_path = Path(frame_info['frame_path'])
    frame_name = frame_path.stem
    
    # Copiar frame para pasta de imagens
    img_dest = IMAGES_DIR / f"{frame_name}.jpg"
    if not img_dest.exists():
        shutil.copy(frame_path, img_dest)
    
    # Criar label YOLO
    label_path = LABELS_DIR / f"{frame_name}.txt"
    
    if tem_queda and bbox:
        # Formato YOLO: class x_center y_center width height (normalizado)
        img = cv2.imread(str(img_dest))
        h, w = img.shape[:2]
        
        x1, y1, x2, y2 = bbox
        x_center = ((x1 + x2) / 2) / w
        y_center = ((y1 + y2) / 2) / h
        width = (x2 - x1) / w
        height = (y2 - y1) / h
        
        # Classe 0 = queda
        with open(label_path, 'w') as f:
            f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    else:
        # Sem queda - arquivo vazio ou não criar
        if label_path.exists():
            label_path.unlink()
    
    # Salvar anotação no JSON
    st.session_state.anotacoes[frame_name] = {
        'tem_queda': tem_queda,
        'bbox': bbox,
        'video': frame_info['video'],
        'timestamp': frame_info['timestamp']
    }
    
    # Salvar JSON
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    with open(annotations_file, 'w') as f:
        json.dump(st.session_state.anotacoes, f, indent=2)

# Interface
# Interface
if LOGO_AVAILABLE:
    col_header1, col_header2 = st.columns([1, 4])
    with col_header1:
        exibir_logo_streamlit(largura=100, margin_bottom="0")
    with col_header2:
        st.title("🎯 Anotação de Quedas")
else:
    st.title("🎯 Anotação de Quedas")
st.markdown("Marque os frames que contêm quedas")

# Estatísticas
total_frames = len(frames)
anotados = len(st.session_state.anotacoes)
quedas = sum(1 for a in st.session_state.anotacoes.values() if a.get('tem_queda'))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Frames", total_frames)
with col2:
    st.metric("Anotados", anotados)
with col3:
    st.metric("Com Queda", quedas)
with col4:
    st.metric("Progresso", f"{anotados/total_frames*100:.1f}%")

# Navegação
frame_info = frames[st.session_state.frame_index]
frame_path = Path(frame_info['frame_path'])

col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
with col_nav1:
    if st.button("⬅️ Anterior", disabled=st.session_state.frame_index == 0):
        st.session_state.frame_index -= 1
        st.rerun()

with col_nav2:
    st.markdown(f"**Frame {st.session_state.frame_index + 1}/{total_frames}** - {frame_info['video']} - {frame_info['timestamp']:.2f}s")

with col_nav3:
    if st.button("Próximo ➡️", disabled=st.session_state.frame_index == total_frames - 1):
        st.session_state.frame_index += 1
        st.rerun()

# Pular para frame específico
col_skip1, col_skip2 = st.columns([1, 3])
with col_skip1:
    frame_num = st.number_input("Ir para frame:", min_value=1, max_value=total_frames, value=st.session_state.frame_index + 1)
    if st.button("Ir"):
        st.session_state.frame_index = frame_num - 1
        st.rerun()

# Carregar e exibir frame
if frame_path.exists():
    img = cv2.imread(str(frame_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Verificar se já tem anotação
    frame_name = frame_path.stem
    anotacao_existente = st.session_state.anotacoes.get(frame_name, {})
    tem_queda_existente = anotacao_existente.get('tem_queda', False)
    bbox_existente = anotacao_existente.get('bbox')
    
    # Desenhar bbox existente se houver
    if bbox_existente:
        x1, y1, x2, y2 = bbox_existente
        cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)
        cv2.putText(img_rgb, "QUEDA", (int(x1), int(y1) - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    st.image(img_rgb, use_container_width=True)
    
    # Anotação
    st.markdown("---")
    col_anot1, col_anot2 = st.columns(2)
    
    with col_anot1:
        tem_queda = st.checkbox("Tem queda neste frame", value=tem_queda_existente)
    
    if tem_queda:
        with col_anot2:
            st.info("💡 Use o modo de desenho abaixo para marcar a bounding box da queda")
        
        # Bounding box manual (simplificado - pode melhorar com canvas)
        st.markdown("**Coordenadas da Bounding Box (pixels):**")
        col_bbox1, col_bbox2, col_bbox3, col_bbox4 = st.columns(4)
        
        if bbox_existente:
            x1, y1, x2, y2 = bbox_existente
        else:
            h, w = img.shape[:2]
            x1, y1 = int(w * 0.2), int(h * 0.2)
            x2, y2 = int(w * 0.8), int(h * 0.8)
        
        with col_bbox1:
            x1 = st.number_input("X1 (esquerda)", value=int(x1), min_value=0, max_value=img.shape[1])
        with col_bbox2:
            y1 = st.number_input("Y1 (topo)", value=int(y1), min_value=0, max_value=img.shape[0])
        with col_bbox3:
            x2 = st.number_input("X2 (direita)", value=int(x2), min_value=0, max_value=img.shape[1])
        with col_bbox4:
            y2 = st.number_input("Y2 (fundo)", value=int(y2), min_value=0, max_value=img.shape[0])
        
        bbox = [x1, y1, x2, y2]
    else:
        bbox = None
    
    # Botão salvar
    if st.button("💾 Salvar Anotação", type="primary", use_container_width=True):
        salvar_anotacao(frame_info, tem_queda, bbox)
        st.success("✅ Anotação salva!")
        st.rerun()
    
    # Preview da anotação
    if tem_queda and bbox:
        img_preview = img_rgb.copy()
        x1, y1, x2, y2 = bbox
        cv2.rectangle(img_preview, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
        cv2.putText(img_preview, "QUEDA", (int(x1), int(y1) - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        st.image(img_preview, caption="Preview da anotação", use_container_width=True)

else:
    st.error(f"❌ Frame não encontrado: {frame_path}")

# Exportar dataset
st.markdown("---")
st.subheader("📦 Exportar Dataset")
if st.button("📥 Exportar Dataset YOLO", use_container_width=True):
    st.info("✅ Dataset já está em formato YOLO nas pastas images/ e labels/")
    st.code(f"Images: {IMAGES_DIR}\nLabels: {LABELS_DIR}")

