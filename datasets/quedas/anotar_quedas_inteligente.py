"""
Interface Streamlit INTELIGENTE para anotar quedas.
Usa YOLO para detectar pessoas automaticamente e sugerir bounding boxes.
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

st.set_page_config(page_title="Anotação Inteligente de Quedas", layout="wide")

# Carregar modelo YOLO para detecção automática
@st.cache_resource
def carregar_modelo():
    """Carrega modelo YOLO para detecção automática"""
    try:
        return YOLO(str(MODEL_PATH))
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar modelo: {e}")
        return None

modelo_yolo = carregar_modelo()

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
if 'filtro_pessoas' not in st.session_state:
    st.session_state.filtro_pessoas = True
if 'auto_detectar' not in st.session_state:
    st.session_state.auto_detectar = True
if 'carregar_anotacoes_existentes' not in st.session_state:
    st.session_state.carregar_anotacoes_existentes = True

# Carregar anotações existentes
if st.session_state.carregar_anotacoes_existentes:
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    if annotations_file.exists():
        with open(annotations_file, 'r') as f:
            st.session_state.anotacoes = json.load(f)
    st.session_state.carregar_anotacoes_existentes = False

def detectar_pessoas_automatico(frame_path):
    """
    Detecta pessoas automaticamente usando YOLO.
    Retorna lista de bounding boxes sugeridas.
    """
    if modelo_yolo is None:
        return []
    
    try:
        img = cv2.imread(str(frame_path))
        if img is None:
            return []
        
        results = modelo_yolo.predict(img, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        bboxes_sugeridas = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    if cls == PERSON_CLASS_ID:
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        bboxes_sugeridas.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confianca': conf
                        })
        
        return bboxes_sugeridas
    except Exception as e:
        st.warning(f"Erro na detecção automática: {e}")
        return []

def filtrar_frames_com_pessoas(frames_list):
    """Filtra frames que têm pessoas detectadas"""
    if not st.session_state.filtro_pessoas:
        return frames_list
    
    frames_filtrados = []
    for frame_info in frames_list:
        frame_path = Path(frame_info['frame_path'])
        if frame_path.exists():
            bboxes = detectar_pessoas_automatico(frame_path)
            if bboxes:
                frames_filtrados.append(frame_info)
    
    return frames_filtrados if frames_filtrados else frames_list

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
    
    # Salvar anotação no JSON
    st.session_state.anotacoes[frame_name] = {
        'tem_queda': tem_queda,
        'bbox': bbox,
        'video': frame_info['video'],
        'timestamp': frame_info['timestamp']
    }
    
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    with open(annotations_file, 'w') as f:
        json.dump(st.session_state.anotacoes, f, indent=2)

def propagar_anotacao(frame_atual_idx, frames_list, propagar_quantos=5):
    """Propaga anotação para frames próximos do mesmo vídeo"""
    frame_atual = frames_list[frame_atual_idx]
    video_atual = frame_atual['video']
    anotacao = st.session_state.anotacoes.get(Path(frame_atual['frame_path']).stem, {})
    
    if not anotacao.get('tem_queda'):
        return 0
    
    propagados = 0
    # Procurar frames próximos do mesmo vídeo
    for i in range(max(0, frame_atual_idx - propagar_quantos), 
                   min(len(frames_list), frame_atual_idx + propagar_quantos + 1)):
        if i == frame_atual_idx:
            continue
        
        frame_proximo = frames_list[i]
        if frame_proximo['video'] == video_atual:
            frame_name = Path(frame_proximo['frame_path']).stem
            if frame_name not in st.session_state.anotacoes:
                # Copiar anotação (ajustar bbox se necessário)
                st.session_state.anotacoes[frame_name] = {
                    'tem_queda': True,
                    'bbox': anotacao.get('bbox'),  # Pode ajustar depois
                    'video': frame_proximo['video'],
                    'timestamp': frame_proximo['timestamp'],
                    'propagado': True
                }
                propagados += 1
    
    if propagados > 0:
        annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
        with open(annotations_file, 'w') as f:
            json.dump(st.session_state.anotacoes, f, indent=2)
    
    return propagados

# Interface
if LOGO_AVAILABLE:
    col_header1, col_header2 = st.columns([1, 4])
    with col_header1:
        exibir_logo_streamlit(largura=100, margin_bottom="0")
    with col_header2:
        st.title("🤖 Anotação Inteligente de Quedas")
        st.markdown("**IA-Assistida**: Detecta pessoas automaticamente e sugere bounding boxes!")
else:
    st.title("🤖 Anotação Inteligente de Quedas")
    st.markdown("**IA-Assistida**: Detecta pessoas automaticamente e sugere bounding boxes!")

# Filtros e configurações
col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
with col_filtro1:
    st.session_state.filtro_pessoas = st.checkbox(
        "🔍 Filtrar frames com pessoas", 
        value=st.session_state.filtro_pessoas,
        help="Mostra apenas frames onde pessoas foram detectadas"
    )
with col_filtro2:
    st.session_state.auto_detectar = st.checkbox(
        "🤖 Detecção automática", 
        value=st.session_state.auto_detectar,
        help="Usa YOLO para detectar pessoas automaticamente"
    )
with col_filtro3:
    propagar_quantos = st.number_input("📋 Propagação", min_value=0, max_value=20, value=5,
                                      help="Frames próximos para propagar anotação")

# Filtrar frames se necessário
frames_para_anotar = filtrar_frames_com_pessoas(frames) if st.session_state.filtro_pessoas else frames

if not frames_para_anotar:
    st.warning("⚠️ Nenhum frame com pessoas detectado. Desative o filtro ou verifique os frames.")
    frames_para_anotar = frames

# Ajustar índice se necessário
if st.session_state.frame_index >= len(frames_para_anotar):
    st.session_state.frame_index = 0

# Estatísticas
total_frames = len(frames_para_anotar)
anotados = len([f for f in frames_para_anotar if Path(f['frame_path']).stem in st.session_state.anotacoes])
quedas = sum(1 for a in st.session_state.anotacoes.values() if a.get('tem_queda'))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Frames Filtrados", total_frames)
with col2:
    st.metric("Anotados", anotados)
with col3:
    st.metric("Com Queda", quedas)
with col4:
    st.metric("Progresso", f"{anotados/total_frames*100:.1f}%")

# Navegação rápida
st.markdown("---")
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 2, 1, 1])

with col_nav1:
    if st.button("⬅️ Anterior", disabled=st.session_state.frame_index == 0):
        st.session_state.frame_index -= 1
        st.rerun()

with col_nav2:
    frame_info = frames_para_anotar[st.session_state.frame_index]
    st.markdown(f"**Frame {st.session_state.frame_index + 1}/{total_frames}** - {frame_info['video']} - {frame_info['timestamp']:.2f}s")

with col_nav3:
    if st.button("Próximo ➡️", disabled=st.session_state.frame_index == total_frames - 1):
        st.session_state.frame_index += 1
        st.rerun()

with col_nav4:
    frame_num = st.number_input("Ir para:", min_value=1, max_value=total_frames, 
                                value=st.session_state.frame_index + 1, key="nav_frame")
    if st.button("Ir", key="nav_go"):
        st.session_state.frame_index = frame_num - 1
        st.rerun()

# Carregar e exibir frame
frame_path = Path(frame_info['frame_path'])
if frame_path.exists():
    img = cv2.imread(str(frame_path))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    frame_name = frame_path.stem
    anotacao_existente = st.session_state.anotacoes.get(frame_name, {})
    tem_queda_existente = anotacao_existente.get('tem_queda', False)
    bbox_existente = anotacao_existente.get('bbox')
    
    # Detecção automática
    bboxes_sugeridas = []
    if st.session_state.auto_detectar and modelo_yolo:
        with st.spinner("🤖 Detectando pessoas..."):
            bboxes_sugeridas = detectar_pessoas_automatico(frame_path)
    
    # Desenhar detecções automáticas
    if bboxes_sugeridas:
        for i, bbox_sug in enumerate(bboxes_sugeridas):
            x1, y1, x2, y2 = bbox_sug['bbox']
            conf = bbox_sug['confianca']
            cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(img_rgb, f"Pessoa {conf:.2f}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Desenhar bbox existente
    if bbox_existente:
        x1, y1, x2, y2 = bbox_existente
        cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 3)
        cv2.putText(img_rgb, "QUEDA", (int(x1), int(y1) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    col_img1, col_img2 = st.columns([2, 1])
    
    with col_img1:
        st.image(img_rgb, use_container_width=True, caption="Frame com detecções automáticas (amarelo) e anotações (vermelho)")
    
    with col_img2:
        st.markdown("### 💡 Sugestões Automáticas")
        if bboxes_sugeridas:
            for i, bbox_sug in enumerate(bboxes_sugeridas):
                if st.button(f"✅ Usar Sugestão {i+1} (conf: {bbox_sug['confianca']:.2f})", 
                           key=f"sug_{i}", use_container_width=True):
                    bbox_existente = bbox_sug['bbox']
                    tem_queda_existente = True
                    salvar_anotacao(frame_info, True, bbox_existente)
                    st.success("✅ Anotação salva!")
                    st.rerun()
        else:
            st.info("Nenhuma pessoa detectada automaticamente")
    
    # Anotação manual
    st.markdown("---")
    col_anot1, col_anot2 = st.columns(2)
    
    with col_anot1:
        tem_queda = st.checkbox("Tem queda neste frame", value=tem_queda_existente)
    
    if tem_queda:
        # Usar bbox sugerida se disponível
        if bboxes_sugeridas and not bbox_existente:
            bbox_inicial = bboxes_sugeridas[0]['bbox']
            st.info("💡 Bounding box sugerida automaticamente. Ajuste se necessário.")
        elif bbox_existente:
            bbox_inicial = bbox_existente
        else:
            h, w = img.shape[:2]
            bbox_inicial = [int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.8)]
        
        st.markdown("**Coordenadas da Bounding Box:**")
        col_bbox1, col_bbox2, col_bbox3, col_bbox4 = st.columns(4)
        
        with col_bbox1:
            x1 = st.number_input("X1", value=int(bbox_inicial[0]), min_value=0, max_value=img.shape[1], key="x1")
        with col_bbox2:
            y1 = st.number_input("Y1", value=int(bbox_inicial[1]), min_value=0, max_value=img.shape[0], key="y1")
        with col_bbox3:
            x2 = st.number_input("X2", value=int(bbox_inicial[2]), min_value=0, max_value=img.shape[1], key="x2")
        with col_bbox4:
            y2 = st.number_input("Y2", value=int(bbox_inicial[3]), min_value=0, max_value=img.shape[0], key="y2")
        
        bbox = [x1, y1, x2, y2]
    else:
        bbox = None
    
    # Botões de ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            salvar_anotacao(frame_info, tem_queda, bbox)
            st.success("✅ Salvo!")
            st.rerun()
    
    with col_btn2:
        if st.button("📋 Salvar + Propagar", use_container_width=True):
            salvar_anotacao(frame_info, tem_queda, bbox)
            propagados = propagar_anotacao(st.session_state.frame_index, frames_para_anotar, propagar_quantos)
            if propagados > 0:
                st.success(f"✅ Salvo e propagado para {propagados} frames próximos!")
            else:
                st.success("✅ Salvo!")
            st.rerun()
    
    with col_btn3:
        if st.button("⏭️ Pular (sem queda)", use_container_width=True):
            salvar_anotacao(frame_info, False, None)
            st.session_state.frame_index += 1
            st.rerun()
    
    # Preview
    if tem_queda and bbox:
        img_preview = img_rgb.copy()
        x1, y1, x2, y2 = bbox
        cv2.rectangle(img_preview, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
        cv2.putText(img_preview, "QUEDA", (int(x1), int(y1) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        st.image(img_preview, caption="Preview da anotação", use_container_width=True)

else:
    st.error(f"❌ Frame não encontrado: {frame_path}")

# Exportar
st.markdown("---")
if st.button("📥 Exportar Dataset YOLO", use_container_width=True):
    st.info("✅ Dataset já está em formato YOLO nas pastas images/ e labels/")
    st.code(f"Images: {IMAGES_DIR}\nLabels: {LABELS_DIR}")

