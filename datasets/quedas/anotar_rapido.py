"""
Anotação Rápida - Modo acelerado com atalhos e anotação em lote.
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

from ultralytics import YOLO
from config import MODEL_PATH, PERSON_CLASS_ID, CONFIDENCE_THRESHOLD

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

st.set_page_config(page_title="Anotação Rápida", layout="wide")

# Carregar modelo
@st.cache_resource
def carregar_modelo():
    try:
        return YOLO(str(MODEL_PATH))
    except:
        return None

modelo_yolo = carregar_modelo()

# Carregar frames
@st.cache_data
def carregar_frames():
    index_path = FRAMES_DIR / "frames_index.json"
    if not index_path.exists():
        return []
    with open(index_path, 'r') as f:
        return json.load(f)

frames = carregar_frames()

if not frames:
    st.error("❌ Execute primeiro: python extrair_frames.py")
    st.stop()

# Estado
if 'frame_index' not in st.session_state:
    st.session_state.frame_index = 0
if 'anotacoes' not in st.session_state:
    st.session_state.anotacoes = {}
if 'ultima_bbox' not in st.session_state:
    st.session_state.ultima_bbox = None
if 'modo_rapido' not in st.session_state:
    st.session_state.modo_rapido = True

# Carregar anotações
annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
if annotations_file.exists():
    with open(annotations_file, 'r') as f:
        st.session_state.anotacoes = json.load(f)

def detectar_pessoas(frame_path):
    if modelo_yolo is None:
        return []
    try:
        img = cv2.imread(str(frame_path))
        results = modelo_yolo.predict(img, conf=CONFIDENCE_THRESHOLD, verbose=False)
        bboxes = []
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == PERSON_CLASS_ID:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bboxes.append([int(x1), int(y1), int(x2), int(y2)])
        return bboxes
    except:
        return []

def salvar_anotacao(frame_info, tem_queda, bbox=None):
    frame_path = Path(frame_info['frame_path'])
    frame_name = frame_path.stem
    
    img_dest = IMAGES_DIR / f"{frame_name}.jpg"
    if not img_dest.exists():
        shutil.copy(frame_path, img_dest)
    
    label_path = LABELS_DIR / f"{frame_name}.txt"
    if tem_queda and bbox:
        img = cv2.imread(str(img_dest))
        h, w = img.shape[:2]
        x1, y1, x2, y2 = bbox
        x_center = ((x1 + x2) / 2) / w
        y_center = ((y1 + y2) / 2) / h
        width = (x2 - x1) / w
        height = (y2 - y1) / h
        with open(label_path, 'w') as f:
            f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    else:
        if label_path.exists():
            label_path.unlink()
    
    st.session_state.anotacoes[frame_name] = {
        'tem_queda': tem_queda,
        'bbox': bbox,
        'video': frame_info['video'],
        'timestamp': frame_info['timestamp']
    }
    
    with open(annotations_file, 'w') as f:
        json.dump(st.session_state.anotacoes, f, indent=2)

# Interface
if LOGO_AVAILABLE:
    col_header1, col_header2 = st.columns([1, 4])
    with col_header1:
        exibir_logo_streamlit(largura=100, margin_bottom="0")
    with col_header2:
        st.title("⚡ Anotação Rápida")
        st.markdown("**Modo Turbo**: Anote mais rápido com atalhos e detecção automática!")
else:
    st.title("⚡ Anotação Rápida")
    st.markdown("**Modo Turbo**: Anote mais rápido com atalhos e detecção automática!")

# Modo rápido
st.session_state.modo_rapido = st.checkbox("🚀 Modo Rápido", value=True,
                                           help="Usa última bbox automaticamente")

# Estatísticas
total = len(frames)
anotados = len(st.session_state.anotacoes)
quedas = sum(1 for a in st.session_state.anotacoes.values() if a.get('tem_queda'))

col1, col2, col3 = st.columns(3)
col1.metric("Total", total)
col2.metric("Anotados", anotados)
col3.metric("Quedas", quedas)

# Frame atual
frame_info = frames[st.session_state.frame_index]
frame_path = Path(frame_info['frame_path'])

if frame_path.exists():
    img = cv2.imread(str(frame_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    frame_name = frame_path.stem
    anotacao = st.session_state.anotacoes.get(frame_name, {})
    tem_queda = anotacao.get('tem_queda', False)
    bbox = anotacao.get('bbox')
    
    # Detecção automática
    bboxes_auto = detectar_pessoas(frame_path) if modelo_yolo else []
    
    # Usar última bbox se modo rápido
    if st.session_state.modo_rapido and not bbox and st.session_state.ultima_bbox:
        bbox = st.session_state.ultima_bbox
        tem_queda = True
    
    # Usar primeira detecção automática se disponível
    if not bbox and bboxes_auto:
        bbox = bboxes_auto[0]
        tem_queda = True
    
    # Desenhar
    if bbox:
        x1, y1, x2, y2 = bbox
        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.putText(img_rgb, "QUEDA", (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    col_img, col_acoes = st.columns([2, 1])
    
    with col_img:
        st.image(img_rgb, use_container_width=True)
        st.caption(f"Frame {st.session_state.frame_index + 1}/{total} - {frame_info['video']}")
    
    with col_acoes:
        st.markdown("### ⚡ Ações Rápidas")
        
        # Botões de ação rápida
        if st.button("✅ Tem Queda", type="primary", use_container_width=True):
            if not bbox and bboxes_auto:
                bbox = bboxes_auto[0]
            if bbox:
                salvar_anotacao(frame_info, True, bbox)
                st.session_state.ultima_bbox = bbox
                st.session_state.frame_index += 1
                st.rerun()
            else:
                st.warning("Nenhuma bbox disponível. Use detecção automática ou ajuste manualmente.")
        
        if st.button("❌ Sem Queda", use_container_width=True):
            salvar_anotacao(frame_info, False, None)
            st.session_state.frame_index += 1
            st.rerun()
        
        if st.button("⏭️ Pular", use_container_width=True):
            st.session_state.frame_index += 1
            st.rerun()
        
        st.markdown("---")
        
        # Ajuste fino de bbox
        if bbox:
            st.markdown("**Ajustar BBox:**")
            x1, y1, x2, y2 = bbox
            
            col_x1, col_y1 = st.columns(2)
            with col_x1:
                x1_new = st.number_input("X1", value=x1, key="adj_x1")
            with col_y1:
                y1_new = st.number_input("Y1", value=y1, key="adj_y1")
            
            col_x2, col_y2 = st.columns(2)
            with col_x2:
                x2_new = st.number_input("X2", value=x2, key="adj_x2")
            with col_y2:
                y2_new = st.number_input("Y2", value=y2, key="adj_y2")
            
            if st.button("💾 Salvar Ajuste"):
                bbox_ajustado = [x1_new, y1_new, x2_new, y2_new]
                salvar_anotacao(frame_info, True, bbox_ajustado)
                st.session_state.ultima_bbox = bbox_ajustado
                st.success("✅ Ajustado!")
                st.rerun()
        
        # Sugestões automáticas
        if bboxes_auto:
            st.markdown("**Sugestões:**")
            for i, bbox_sug in enumerate(bboxes_auto[:3]):
                if st.button(f"Usar Sugestão {i+1}", key=f"sug_{i}", use_container_width=True):
                    salvar_anotacao(frame_info, True, bbox_sug)
                    st.session_state.ultima_bbox = bbox_sug
                    st.session_state.frame_index += 1
                    st.rerun()
    
    # Navegação
    st.markdown("---")
    col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
    with col_nav1:
        if st.button("⬅️ Anterior"):
            st.session_state.frame_index = max(0, st.session_state.frame_index - 1)
            st.rerun()
    with col_nav2:
        frame_num = st.number_input("Ir para:", min_value=1, max_value=total,
                                   value=st.session_state.frame_index + 1)
        if st.button("Ir"):
            st.session_state.frame_index = frame_num - 1
            st.rerun()
    with col_nav3:
        if st.button("Próximo ➡️"):
            st.session_state.frame_index = min(total - 1, st.session_state.frame_index + 1)
            st.rerun()
    
    # Atalhos de teclado (via JavaScript)
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT') return;
        
        if (e.key === 'ArrowRight' || e.key === ' ') {
            // Próximo frame
            window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'next_frame'}, '*');
        } else if (e.key === 'ArrowLeft') {
            // Frame anterior
            window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'prev_frame'}, '*');
        } else if (e.key === 'q' || e.key === 'Q') {
            // Marcar queda
            window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'mark_fall'}, '*');
        }
    });
    </script>
    """, unsafe_allow_html=True)

else:
    st.error(f"Frame não encontrado: {frame_path}")

