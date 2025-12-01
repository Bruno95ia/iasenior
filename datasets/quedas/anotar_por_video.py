"""
Anotação por Vídeo - Timeline interativa MELHORADA.
Anota quedas marcando início/fim no vídeo, muito mais rápido!
Com detecção automática de bbox e timeline visual aprimorada.
"""

import streamlit as st
import cv2
import json
from pathlib import Path
import numpy as np
from PIL import Image
import shutil
import sys
import plotly.graph_objects as go
import plotly.express as px

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

st.set_page_config(page_title="Anotação por Vídeo", layout="wide")

# Carregar modelo YOLO para detecção automática
@st.cache_resource
def carregar_modelo():
    """Carrega modelo YOLO para detecção automática de pessoas"""
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

# Agrupar frames por vídeo
@st.cache_data
def agrupar_por_video():
    videos = {}
    for frame in frames:
        video_name = frame['video']
        if video_name not in videos:
            videos[video_name] = []
        videos[video_name].append(frame)
    
    # Ordenar frames por timestamp
    for video_name in videos:
        videos[video_name].sort(key=lambda x: x['timestamp'])
    
    return videos

videos_dict = agrupar_por_video()

# Estado da sessão
if 'video_selecionado' not in st.session_state:
    st.session_state.video_selecionado = list(videos_dict.keys())[0] if videos_dict else None
if 'anotacoes_video' not in st.session_state:
    st.session_state.anotacoes_video = {}
if 'carregar_anotacoes' not in st.session_state:
    st.session_state.carregar_anotacoes = True
if 'auto_detectar_bbox' not in st.session_state:
    st.session_state.auto_detectar_bbox = True
if 'editar_intervalo_idx' not in st.session_state:
    st.session_state.editar_intervalo_idx = None

# Carregar anotações existentes
if st.session_state.carregar_anotacoes:
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    if annotations_file.exists():
        with open(annotations_file, 'r') as f:
            anotacoes_existentes = json.load(f)
            # Converter para formato de vídeo
            for frame_name, anotacao in anotacoes_existentes.items():
                video = anotacao.get('video')
                if video not in st.session_state.anotacoes_video:
                    st.session_state.anotacoes_video[video] = []
                st.session_state.anotacoes_video[video].append({
                    'timestamp': anotacao.get('timestamp', 0),
                    'tem_queda': anotacao.get('tem_queda', False),
                    'bbox': anotacao.get('bbox')
                })
    st.session_state.carregar_anotacoes = False

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
        return []

def obter_bbox_para_intervalo(video, inicio, fim):
    """
    Obtém bbox automática para um intervalo de queda.
    Usa o frame do meio do intervalo.
    """
    frames_video = videos_dict[video]
    timestamp_meio = (inicio + fim) / 2
    
    # Encontrar frame mais próximo do meio
    frame_meio = min(frames_video, key=lambda x: abs(x['timestamp'] - timestamp_meio))
    
    if frame_meio:
        frame_path = Path(frame_meio['frame_path'])
        if frame_path.exists():
            bboxes = detectar_pessoas_automatico(frame_path)
            if bboxes:
                # Retornar bbox com maior confiança
                bbox_maior_conf = max(bboxes, key=lambda x: x['confianca'])
                return bbox_maior_conf['bbox']
    
    return None

def salvar_anotacoes_video():
    """Salva todas as anotações do vídeo atual"""
    video = st.session_state.video_selecionado
    frames_video = videos_dict[video]
    
    for frame_info in frames_video:
        frame_path = Path(frame_info['frame_path'])
        frame_name = frame_path.stem
        timestamp = frame_info['timestamp']
        
        # Verificar se está em algum intervalo de queda
        tem_queda = False
        bbox = None
        
        if video in st.session_state.anotacoes_video:
            for intervalo in st.session_state.anotacoes_video[video]:
                if isinstance(intervalo, dict) and 'inicio' in intervalo:
                    if intervalo['inicio'] <= timestamp <= intervalo['fim']:
                        tem_queda = True
                        bbox = intervalo.get('bbox')
                        break
        
        # Salvar frame
        img_dest = IMAGES_DIR / f"{frame_name}.jpg"
        if not img_dest.exists():
            shutil.copy(frame_path, img_dest)
        
        # Salvar label
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
    
    # Salvar JSON
    annotations_file = ANNOTATIONS_DIR / "anotacoes.json"
    anotacoes_completas = {}
    for frame_info in frames:
        frame_name = Path(frame_info['frame_path']).stem
        video = frame_info['video']
        timestamp = frame_info['timestamp']
        
        tem_queda = False
        bbox = None
        
        if video in st.session_state.anotacoes_video:
            for intervalo in st.session_state.anotacoes_video[video]:
                if isinstance(intervalo, dict) and 'inicio' in intervalo:
                    if intervalo['inicio'] <= timestamp <= intervalo['fim']:
                        tem_queda = True
                        bbox = intervalo.get('bbox')
                        break
        
        anotacoes_completas[frame_name] = {
            'tem_queda': tem_queda,
            'bbox': bbox,
            'video': video,
            'timestamp': timestamp
        }
    
    with open(annotations_file, 'w') as f:
        json.dump(anotacoes_completas, f, indent=2)

# Interface
if LOGO_AVAILABLE:
    col_header1, col_header2 = st.columns([1, 4])
    with col_header1:
        exibir_logo_streamlit(largura=100, margin_bottom="0")
    with col_header2:
        st.title("🎬 Anotação por Vídeo - Timeline Melhorada")
        st.markdown("**Método Ultra-Rápido**: Marque início/fim das quedas no vídeo com detecção automática!")
else:
    st.title("🎬 Anotação por Vídeo - Timeline Melhorada")
    st.markdown("**Método Ultra-Rápido**: Marque início/fim das quedas no vídeo com detecção automática!")

# Configurações
col_config1, col_config2 = st.columns(2)
with col_config1:
    st.session_state.auto_detectar_bbox = st.checkbox(
        "🤖 Detecção automática de bbox", 
        value=st.session_state.auto_detectar_bbox,
        help="Detecta automaticamente bounding boxes para os intervalos"
    )
with col_config2:
    preview_multiplos = st.checkbox(
        "👁️ Preview múltiplos frames", 
        value=True,
        help="Mostra preview de vários frames do intervalo"
    )

# Seleção de vídeo
video_selecionado = st.selectbox(
    "📹 Selecionar Vídeo",
    list(videos_dict.keys()),
    index=0 if st.session_state.video_selecionado else 0,
    key="select_video"
)
st.session_state.video_selecionado = video_selecionado

frames_video = videos_dict[video_selecionado]
duracao_total = max(f['timestamp'] for f in frames_video) if frames_video else 0

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("Frames", len(frames_video))
with col_info2:
    st.metric("Duração", f"{duracao_total:.1f}s")
with col_info3:
    st.metric("FPS Médio", f"{len(frames_video)/duracao_total:.1f}" if duracao_total > 0 else "N/A")

# Gerenciar intervalos de queda
st.subheader("⏱️ Intervalos de Queda")

if video_selecionado not in st.session_state.anotacoes_video:
    st.session_state.anotacoes_video[video_selecionado] = []

intervalos = st.session_state.anotacoes_video[video_selecionado]

# Adicionar novo intervalo
with st.expander("➕ Adicionar Intervalo de Queda", expanded=True):
    col_int1, col_int2, col_int3, col_int4 = st.columns([2, 2, 2, 1])
    
    with col_int1:
        inicio = st.number_input("Início (segundos)", min_value=0.0, max_value=float(duracao_total), 
                                value=0.0, step=0.1, key="novo_inicio")
    with col_int2:
        fim = st.number_input("Fim (segundos)", min_value=0.0, max_value=float(duracao_total),
                             value=min(5.0, duracao_total), step=0.1, key="novo_fim")
    with col_int3:
        duracao_intervalo = fim - inicio
        st.metric("Duração", f"{duracao_intervalo:.1f}s")
    with col_int4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Adicionar", type="primary", use_container_width=True):
            if inicio >= fim:
                st.error("❌ Início deve ser menor que fim!")
            else:
                # Detectar bbox automaticamente se habilitado
                bbox_auto = None
                if st.session_state.auto_detectar_bbox and modelo_yolo:
                    with st.spinner("🤖 Detectando pessoa..."):
                        bbox_auto = obter_bbox_para_intervalo(video_selecionado, inicio, fim)
                
                novo_intervalo = {
                    'inicio': inicio,
                    'fim': fim,
                    'bbox': bbox_auto,
                    'auto_detectado': bbox_auto is not None
                }
                intervalos.append(novo_intervalo)
                st.session_state.anotacoes_video[video_selecionado] = intervalos
                st.success(f"✅ Intervalo adicionado: {inicio:.1f}s - {fim:.1f}s" + 
                          (f" (bbox detectada)" if bbox_auto else ""))
                st.rerun()

# Listar intervalos existentes
if intervalos:
    st.markdown("### 📋 Intervalos Cadastrados")
    for i, intervalo in enumerate(intervalos):
        if isinstance(intervalo, dict) and 'inicio' in intervalo:
            with st.container():
                col_list1, col_list2, col_list3, col_list4 = st.columns([4, 1, 1, 1])
                with col_list1:
                    duracao = intervalo['fim'] - intervalo['inicio']
                    bbox_info = "🤖 Auto" if intervalo.get('auto_detectado') else "✋ Manual"
                    st.markdown(f"**⏱️ {intervalo['inicio']:.1f}s - {intervalo['fim']:.1f}s** "
                              f"({duracao:.1f}s) | {bbox_info}")
                with col_list2:
                    if st.button("✏️ Editar", key=f"edit_{i}", use_container_width=True):
                        st.session_state.editar_intervalo_idx = i
                        st.rerun()
                with col_list3:
                    if st.button("🔄 Re-detect", key=f"redetect_{i}", use_container_width=True,
                               help="Re-detectar bbox automaticamente"):
                        if modelo_yolo:
                            bbox_auto = obter_bbox_para_intervalo(
                                video_selecionado, intervalo['inicio'], intervalo['fim']
                            )
                            if bbox_auto:
                                intervalo['bbox'] = bbox_auto
                                intervalo['auto_detectado'] = True
                                st.session_state.anotacoes_video[video_selecionado] = intervalos
                                st.success("✅ Bbox re-detectada!")
                                st.rerun()
                with col_list4:
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                        intervalos.pop(i)
                        st.session_state.anotacoes_video[video_selecionado] = intervalos
                        st.rerun()
    
    # Edição de intervalo
    if st.session_state.editar_intervalo_idx is not None:
        idx_edit = st.session_state.editar_intervalo_idx
        if 0 <= idx_edit < len(intervalos):
            intervalo_edit = intervalos[idx_edit]
            with st.expander(f"✏️ Editando Intervalo {idx_edit + 1}", expanded=True):
                col_edit1, col_edit2, col_edit3 = st.columns(3)
                with col_edit1:
                    novo_inicio = st.number_input("Novo Início", 
                                                 value=float(intervalo_edit['inicio']),
                                                 min_value=0.0, max_value=float(duracao_total),
                                                 step=0.1, key="edit_inicio")
                with col_edit2:
                    novo_fim = st.number_input("Novo Fim",
                                              value=float(intervalo_edit['fim']),
                                              min_value=0.0, max_value=float(duracao_total),
                                              step=0.1, key="edit_fim")
                with col_edit3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 Salvar", key="save_edit"):
                        if novo_inicio < novo_fim:
                            intervalo_edit['inicio'] = novo_inicio
                            intervalo_edit['fim'] = novo_fim
                            st.session_state.anotacoes_video[video_selecionado] = intervalos
                            st.session_state.editar_intervalo_idx = None
                            st.success("✅ Intervalo atualizado!")
                            st.rerun()
                        else:
                            st.error("❌ Início deve ser menor que fim!")
                    if st.button("❌ Cancelar", key="cancel_edit"):
                        st.session_state.editar_intervalo_idx = None
                        st.rerun()
else:
    st.info("ℹ️ Nenhum intervalo cadastrado. Adicione um intervalo acima.")

# Visualização de timeline MELHORADA
st.markdown("---")
st.subheader("📊 Timeline Visual Interativa")

# Criar timeline com Plotly
if intervalos:
    fig = go.Figure()
    
    # Adicionar barras para cada intervalo
    cores = px.colors.qualitative.Set3
    for i, intervalo in enumerate(intervalos):
        if isinstance(intervalo, dict) and 'inicio' in intervalo:
            inicio = intervalo['inicio']
            fim = intervalo['fim']
            cor = cores[i % len(cores)]
            
            fig.add_trace(go.Scatter(
                x=[inicio, fim, fim, inicio, inicio],
                y=[i, i, i+0.8, i+0.8, i],
                fill='toself',
                fillcolor=cor,
                line=dict(color=cor, width=2),
                mode='lines',
                name=f"Queda {i+1}",
                hovertemplate=f"Queda {i+1}<br>Início: {inicio:.1f}s<br>Fim: {fim:.1f}s<br>Duração: {fim-inicio:.1f}s<extra></extra>"
            ))
    
    # Adicionar linha de tempo
    fig.add_trace(go.Scatter(
        x=[0, duracao_total],
        y=[-0.2, -0.2],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Configurar layout
    fig.update_layout(
        title="Timeline de Quedas",
        xaxis_title="Tempo (segundos)",
        yaxis_title="Intervalos",
        height=200,
        hovermode='closest',
        showlegend=True,
        yaxis=dict(
            range=[-0.5, len(intervalos) + 0.5],
            showticklabels=False
        ),
        xaxis=dict(
            range=[0, duracao_total]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas da timeline
    col_tl1, col_tl2, col_tl3 = st.columns(3)
    total_queda_tempo = sum(i['fim'] - i['inicio'] for i in intervalos if isinstance(i, dict) and 'inicio' in i)
    with col_tl1:
        st.metric("Intervalos", len(intervalos))
    with col_tl2:
        st.metric("Tempo Total de Quedas", f"{total_queda_tempo:.1f}s")
    with col_tl3:
        st.metric("% do Vídeo", f"{total_queda_tempo/duracao_total*100:.1f}%" if duracao_total > 0 else "0%")
else:
    st.info("Adicione intervalos para ver a timeline visual.")

# Preview de frames MELHORADO
st.markdown("---")
st.subheader("👁️ Preview de Frames")

# Selecionar intervalo para preview
if intervalos:
    intervalo_preview_idx = st.selectbox(
        "Selecionar Intervalo para Preview",
        options=[f"Intervalo {i+1} ({int['inicio']:.1f}s - {int['fim']:.1f}s)" 
                for i, int in enumerate(intervalos) if isinstance(int, dict) and 'inicio' in int],
        key="select_intervalo_preview"
    )
    
    if intervalo_preview_idx:
        idx = int(intervalo_preview_idx.split()[1]) - 1
        intervalo_preview = intervalos[idx]
        inicio_preview = intervalo_preview['inicio']
        fim_preview = intervalo_preview['fim']
        bbox_preview = intervalo_preview.get('bbox')
        
        if preview_multiplos:
            # Preview de múltiplos frames
            num_frames_preview = st.slider("Número de frames no preview", 3, 9, 5, key="num_frames")
            
            # Selecionar frames distribuídos no intervalo
            timestamps_preview = np.linspace(inicio_preview, fim_preview, num_frames_preview)
            
            cols_preview = st.columns(num_frames_preview)
            for col_idx, timestamp in enumerate(timestamps_preview):
                frame_preview = min(frames_video, key=lambda x: abs(x['timestamp'] - timestamp))
                
                if frame_preview:
                    frame_path = Path(frame_preview['frame_path'])
                    if frame_path.exists():
                        img = cv2.imread(str(frame_path))
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        
                        # Desenhar bbox se disponível
                        if bbox_preview:
                            x1, y1, x2, y2 = bbox_preview
                            cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
                            cv2.putText(img_rgb, "QUEDA", (int(x1), int(y1) - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        with cols_preview[col_idx]:
                            st.image(img_rgb, caption=f"{timestamp:.1f}s", use_container_width=True)
        else:
            # Preview de um frame (meio do intervalo)
            timestamp_meio = (inicio_preview + fim_preview) / 2
            frame_preview = min(frames_video, key=lambda x: abs(x['timestamp'] - timestamp_meio))
            
            if frame_preview:
                frame_path = Path(frame_preview['frame_path'])
                if frame_path.exists():
                    img = cv2.imread(str(frame_path))
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # Desenhar bbox se disponível
                    if bbox_preview:
                        x1, y1, x2, y2 = bbox_preview
                        cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
                        cv2.putText(img_rgb, "QUEDA", (int(x1), int(y1) - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    st.image(img_rgb, caption=f"Frame em {frame_preview['timestamp']:.2f}s (meio do intervalo)", 
                            use_container_width=True)
                    if bbox_preview:
                        st.success(f"✅ Bbox: {bbox_preview}")
                    else:
                        st.warning("⚠️ Nenhuma bbox definida. Use 'Re-detect' ou defina manualmente.")
    
    # Preview manual por timestamp
    st.markdown("**Ou selecione timestamp manualmente:**")
    timestamp_preview = st.slider(
        "Timestamp (segundos)",
        min_value=0.0,
        max_value=float(duracao_total),
        value=0.0,
        step=0.1,
        key="preview_timestamp_manual"
    )
    
    frame_preview = min(frames_video, key=lambda x: abs(x['timestamp'] - timestamp_preview))
    
    if frame_preview:
        frame_path = Path(frame_preview['frame_path'])
        if frame_path.exists():
            img = cv2.imread(str(frame_path))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Verificar se está em intervalo de queda
            em_queda = False
            intervalo_atual = None
            for intervalo in intervalos:
                if isinstance(intervalo, dict) and 'inicio' in intervalo:
                    if intervalo['inicio'] <= frame_preview['timestamp'] <= intervalo['fim']:
                        em_queda = True
                        intervalo_atual = intervalo
                        break
            
            if em_queda and intervalo_atual and intervalo_atual.get('bbox'):
                x1, y1, x2, y2 = intervalo_atual['bbox']
                cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 3)
                cv2.putText(img_rgb, "QUEDA", (int(x1), int(y1) - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            st.image(img_rgb, caption=f"Frame em {frame_preview['timestamp']:.2f}s", use_container_width=True)
            st.caption(f"Status: {'🚨 QUEDA' if em_queda else '✅ OK'}")
else:
    st.info("Adicione intervalos para ver preview.")

# Salvar
st.markdown("---")
col_save1, col_save2 = st.columns([2, 1])
with col_save1:
    if st.button("💾 Salvar Todas as Anotações do Vídeo", type="primary", use_container_width=True):
        with st.spinner("Salvando anotações..."):
            salvar_anotacoes_video()
            frames_com_queda = sum(1 for f in frames_video 
                                  if any(i.get('inicio', 0) <= f['timestamp'] <= i.get('fim', 0) 
                                        for i in intervalos if isinstance(i, dict)))
            st.success(f"✅ Anotações salvas! {frames_com_queda} frames com queda processados")
            st.rerun()
with col_save2:
    if st.button("📊 Ver Estatísticas", use_container_width=True):
        st.rerun()

# Estatísticas
st.markdown("---")
st.subheader("📊 Estatísticas do Vídeo")

frames_com_queda = sum(1 for f in frames_video 
                      if any(i.get('inicio', 0) <= f['timestamp'] <= i.get('fim', 0) 
                            for i in intervalos if isinstance(i, dict)))

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("Frames com Queda", f"{frames_com_queda}/{len(frames_video)}")
with col_stat2:
    st.metric("% Frames Anotados", f"{frames_com_queda/len(frames_video)*100:.1f}%" if frames_video else "0%")
with col_stat3:
    intervalos_com_bbox = sum(1 for i in intervalos if isinstance(i, dict) and i.get('bbox'))
    st.metric("Intervalos com BBox", f"{intervalos_com_bbox}/{len(intervalos)}")
with col_stat4:
    total_bbox_auto = sum(1 for i in intervalos if isinstance(i, dict) and i.get('auto_detectado'))
    st.metric("BBox Auto-Detectadas", total_bbox_auto)

