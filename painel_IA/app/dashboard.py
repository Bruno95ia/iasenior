"""
Dashboard Streamlit Premium para monitoramento de detecção de quedas em tempo real.
Design moderno, funcional e visualmente atraente com gráficos e métricas avançadas.
"""

import streamlit as st
from PIL import Image, UnidentifiedImageError
import numpy as np
import os
import shutil
import sys
import logging
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import pandas as pd

# Tentar importar requests para verificar status MJPEG
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Adicionar diretório raiz ao path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
try:
    from config import (
        FRAME_PATH, STATUS_PATH, RESULTS_DIR, REFRESH_INTERVAL,
        STREAMLIT_HOST, STREAMLIT_PORT, ROOM_COUNT_PATH, BATHROOM_STATUS_PATH,
        LOGS_DIR, DB_ENABLED
    )
    # Importar helper de logo
    try:
        from utils.logo_helper import exibir_logo_streamlit, exibir_logo_com_texto_streamlit, logo_existe
        LOGO_AVAILABLE = logo_existe()
    except ImportError:
        LOGO_AVAILABLE = False
    # Importar módulos de banco de dados
    try:
        from persistencia import get_persistencia_manager
        from database import get_db_manager
        DB_AVAILABLE = True
    except ImportError:
        DB_AVAILABLE = False
        logger.warning("Módulos de banco de dados não disponíveis")
    
    # Importar módulo de relatórios
    try:
        from relatorios import get_relatorio_manager
        RELATORIOS_AVAILABLE = True
    except ImportError:
        RELATORIOS_AVAILABLE = False
        logger.warning("Módulo de relatórios não disponível")
except ImportError:
    # Fallback caso config.py não exista
    FRAME_PATH = "resultados/ultima_frame.jpg"
    STATUS_PATH = "resultados/status.txt"
    RESULTS_DIR = Path("resultados")
    REFRESH_INTERVAL = 3
    STREAMLIT_HOST = "0.0.0.0"
    STREAMLIT_PORT = 8501
    ROOM_COUNT_PATH = str(RESULTS_DIR / "contagem_quarto.txt")
    BATHROOM_STATUS_PATH = str(RESULTS_DIR / "status_banheiro.txt")
    LOGS_DIR = Path("logs")
    DB_ENABLED = False
    DB_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Centro de Monitoramento IA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Premium Personalizado
st.markdown("""
    <style>
        /* Tema geral */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
        }
        
        /* Métricas melhoradas */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            color: white;
            text-align: center;
            margin: 0.5rem;
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        /* Cards de status */
        .status-card {
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            background: white;
        }
        
        /* Alertas */
        .alert-box {
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* Sidebar melhorada */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: white;
        }
        
        /* Títulos */
        h1 {
            color: #1a202c;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        h2, h3 {
            color: #2d3748;
            font-weight: 600;
        }
        
        /* Streamlit default overrides */
        .stMetric {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
        }
        
        .stMetric > label {
            color: rgba(255,255,255,0.9) !important;
            font-weight: 600;
        }
        
        .stMetric > div {
            color: white !important;
            font-weight: 700;
            font-size: 1.8rem;
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102,126,234,0.4);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state para histórico
if 'historico_quarto' not in st.session_state:
    st.session_state.historico_quarto = deque(maxlen=100)
if 'historico_banheiro' not in st.session_state:
    st.session_state.historico_banheiro = deque(maxlen=100)
if 'historico_status' not in st.session_state:
    st.session_state.historico_status = deque(maxlen=100)
if 'eventos' not in st.session_state:
    st.session_state.eventos = deque(maxlen=50)


def ler_frame():
    """Lê o último frame salvo."""
    if not os.path.exists(FRAME_PATH):
        return None
    
    try:
        image = Image.open(FRAME_PATH)
        image.load()
        return np.array(image)
    except (UnidentifiedImageError, OSError, IOError) as e:
        logger.warning(f"⚠️ Erro ao ler frame: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao ler frame: {e}")
        return None


def ler_status():
    """Lê o status atual de detecção."""
    if not os.path.exists(STATUS_PATH):
        return "unknown"
    
    try:
        with open(STATUS_PATH, 'r') as f:
            status = f.read().strip().lower()
        return status if status in ["queda", "ok", "unknown"] else "unknown"
    except Exception as e:
        logger.error(f"❌ Erro ao ler status: {e}")
        return "unknown"


def obter_ultima_modificacao_frame():
    """Retorna o timestamp da última modificação do frame."""
    if os.path.exists(FRAME_PATH):
        try:
            return os.path.getmtime(FRAME_PATH)
        except Exception:
            return 0
    return 0


def ler_contagem_quarto():
    """Lê a contagem de pessoas no quarto."""
    if not os.path.exists(ROOM_COUNT_PATH):
        return 0
    
    try:
        with open(ROOM_COUNT_PATH, 'r') as f:
            conteudo = f.read().strip()
            return int(conteudo) if conteudo.isdigit() else 0
    except Exception as e:
        logger.error(f"❌ Erro ao ler contagem do quarto: {e}")
        return 0


def ler_status_banheiro():
    """Lê o status do banheiro (pessoas e alertas)."""
    if not os.path.exists(BATHROOM_STATUS_PATH):
        return {
            'pessoas_no_banheiro': 0,
            'alertas': [],
            'pessoas': []
        }
    
    try:
        with open(BATHROOM_STATUS_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            'pessoas_no_banheiro': 0,
            'alertas': [],
            'pessoas': []
        }
    except Exception as e:
        logger.error(f"❌ Erro ao ler status do banheiro: {e}")
        return {
            'pessoas_no_banheiro': 0,
            'alertas': [],
            'pessoas': []
        }


def salvar_captura_manual():
    """Salva uma captura manual do frame atual."""
    if not os.path.exists(FRAME_PATH):
        return None, "Nenhum frame disponível no momento."
    
    try:
        captura_dir = RESULTS_DIR / "captura_manual"
        captura_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = captura_dir / f"captura_{timestamp}.jpg"
        
        shutil.copyfile(FRAME_PATH, str(destino))
        return str(destino), None
    except Exception as e:
        logger.error(f"❌ Erro ao salvar captura manual: {e}")
        return None, f"Erro ao salvar captura: {e}"


def listar_capturas_manuais():
    """Lista todas as capturas manuais salvas."""
    captura_dir = RESULTS_DIR / "captura_manual"
    if not captura_dir.exists():
        return []
    
    try:
        arquivos = sorted(
            captura_dir.glob("captura_*.jpg"),
            key=os.path.getmtime,
            reverse=True
        )
        return [str(f) for f in arquivos[:20]]  # Últimas 20
    except Exception as e:
        logger.error(f"❌ Erro ao listar capturas: {e}")
        return []


def atualizar_historico():
    """Atualiza histórico de métricas."""
    timestamp = datetime.now()
    
    contagem_quarto = ler_contagem_quarto()
    status_banheiro = ler_status_banheiro()
    status = ler_status()
    
    # Atualizar histórico em memória (para gráficos)
    st.session_state.historico_quarto.append({
        'timestamp': timestamp,
        'valor': contagem_quarto
    })
    
    st.session_state.historico_banheiro.append({
        'timestamp': timestamp,
        'valor': status_banheiro.get('pessoas_no_banheiro', 0)
    })
    
    st.session_state.historico_status.append({
        'timestamp': timestamp,
        'status': status
    })
    
    # Salvar no banco de dados se disponível
    if DB_ENABLED and DB_AVAILABLE:
        try:
            persistencia = get_persistencia_manager()
            
            # Salvar status
            persistencia.salvar_status_sistema(status)
            
            # Salvar ocupação do quarto
            persistencia.salvar_ocupacao_quarto(contagem_quarto)
            
            # Salvar ocupação do banheiro
            pessoas = status_banheiro.get('pessoas', [])
            alertas = status_banheiro.get('alertas', [])
            persistencia.salvar_ocupacao_banheiro(
                status_banheiro.get('pessoas_no_banheiro', 0),
                pessoas,
                alertas
            )
        except Exception as e:
            logger.error(f"Erro ao salvar no banco: {e}")


def adicionar_evento(tipo, mensagem, severidade="info"):
    """Adiciona evento ao histórico."""
    st.session_state.eventos.append({
        'timestamp': datetime.now(),
        'tipo': tipo,
        'mensagem': mensagem,
        'severidade': severidade
    })


# Sidebar Premium
with st.sidebar:
    if LOGO_AVAILABLE:
        st.markdown("<div style='text-align: center; padding: 1rem 0;'>", unsafe_allow_html=True)
        exibir_logo_streamlit(largura=150, margin_bottom="0.5rem")
        st.markdown("""
            <div style="text-align: center;">
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0; font-size: 1.1rem; font-weight: 600;">IA Senior</p>
                <p style="color: rgba(255,255,255,0.7); margin: 0;">Centro de Controle</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="color: white; margin: 0;">🛡️ IA Senior</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0;">Centro de Controle</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("⚙️ Configurações")
    
    auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, key="auto_refresh")
    refresh_rate = st.slider(
        "⏱️ Intervalo (seg)", 
        min_value=1, 
        max_value=10, 
        value=REFRESH_INTERVAL,
        key="refresh_rate"
    )
    
    st.markdown("---")
    
    st.subheader("📊 Estatísticas Rápidas")
    
    last_update = obter_ultima_modificacao_frame()
    if last_update > 0:
        last_update_str = datetime.fromtimestamp(last_update).strftime("%H:%M:%S")
        st.metric("🕐 Última Atualização", last_update_str)
    else:
        st.info("⏳ Aguardando...")
    
    num_capturas = len(listar_capturas_manuais())
    st.metric("📸 Capturas", num_capturas)
    
    contagem_quarto = ler_contagem_quarto()
    st.metric("🏠 No Quarto", contagem_quarto)
    
    status_banheiro = ler_status_banheiro()
    pessoas_banheiro = status_banheiro.get('pessoas_no_banheiro', 0)
    st.metric("🚿 No Banheiro", pessoas_banheiro)
    
    st.markdown("---")
    
    if st.button("🔄 Atualizar Agora", use_container_width=True):
        st.rerun() if hasattr(st, 'rerun') else st.experimental_rerun()
    
    if auto_refresh:
        time.sleep(refresh_rate)
        atualizar_historico()
        st.rerun() if hasattr(st, 'rerun') else st.experimental_rerun()
    else:
        atualizar_historico()

# Título Principal
if LOGO_AVAILABLE:
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
    """, unsafe_allow_html=True)
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        exibir_logo_streamlit(largura=120, margin_bottom="1rem")
    st.markdown("""
            <h1 style="color: white; margin: 0; font-size: 2.5rem;">Centro de Monitoramento Inteligente</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 0.5rem;">
                Sistema de IA para Detecção em Tempo Real
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h1 style="color: white; margin: 0; font-size: 3rem;">🛡️ Centro de Monitoramento Inteligente</h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 0.5rem;">
                Sistema de IA para Detecção em Tempo Real
            </p>
        </div>
    """, unsafe_allow_html=True)

# Métricas Principais com Cards Visuais
col1, col2, col3, col4 = st.columns(4)

with col1:
    contagem_quarto = ler_contagem_quarto()
    st.metric(
        "🏠 Pessoas no Quarto",
        contagem_quarto,
        delta=None
    )

with col2:
    status_banheiro = ler_status_banheiro()
    pessoas_banheiro = status_banheiro.get('pessoas_no_banheiro', 0)
    st.metric(
        "🚿 Pessoas no Banheiro",
        pessoas_banheiro,
        delta=None
    )

with col3:
    alertas_banheiro = len(status_banheiro.get('alertas', []))
    if alertas_banheiro > 0:
        st.metric(
            "⚠️ Alertas Ativos",
            alertas_banheiro,
            delta=None,
            delta_color="inverse"
        )
    else:
        st.metric(
            "✅ Alertas",
            0,
            delta=None
        )

with col4:
    status = ler_status()
    if status == "queda":
        st.metric(
            "🚨 Status Geral",
            "QUEDA!",
            delta=None,
            delta_color="inverse"
        )
    else:
        st.metric(
            "✅ Status Geral",
            "OK",
            delta=None
        )

st.markdown("<br>", unsafe_allow_html=True)

# Tabs para Organização
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📺 Monitoramento", "📊 Análises", "🚨 Alertas", "📁 Galeria", "📄 Relatórios"])

with tab1:
    col_video, col_status = st.columns([2, 1])
    
    with col_video:
        st.subheader("📺 Transmissão ao Vivo")
        
        # Opção para escolher entre stream MJPEG ou frame estático
        modo_exibicao = st.radio(
            "Modo de exibição:",
            ["Stream MJPEG (Tempo Real)", "Frame Estático (Arquivo)"],
            horizontal=True,
            key="modo_video"
        )
        
        if modo_exibicao == "Stream MJPEG (Tempo Real)":
            # Stream MJPEG em tempo real
            mjpeg_url = os.getenv("MJPEG_URL", "http://localhost:8888/video")
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px; margin-bottom: 1rem;">
                <p style="margin: 0; color: #666;">🎥 Stream MJPEG com detecções YOLO em tempo real</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #888;">URL: {mjpeg_url}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Exibir stream MJPEG usando HTML
            # O MJPEG stream funciona automaticamente com multipart/x-mixed-replace
            st.markdown(f"""
            <div style="text-align: center; position: relative;">
                <img src="{mjpeg_url}" 
                     alt="Stream MJPEG" 
                     style="max-width: 100%; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); background: #000; min-height: 400px;">
            </div>
            """, unsafe_allow_html=True)
            
            # Verificar status do servidor MJPEG
            try:
                import requests
                status_url = mjpeg_url.replace('/video', '/status')
                response = requests.get(status_url, timeout=2)
                if response.status_code == 200:
                    status_data = response.json()
                    st.success(f"✅ Stream ativo | Pessoas no quarto: {status_data.get('pessoas_quarto', 0)} | Frames: {status_data.get('frame_count', 0)}")
                else:
                    st.warning("⚠️ Servidor MJPEG não está respondendo. Verifique se está rodando.")
            except Exception as e:
                st.warning(f"⚠️ Não foi possível conectar ao servidor MJPEG: {e}")
                st.info("💡 Para ativar o stream MJPEG, execute: `python mjpeg_server_com_deteccoes.py`")
        else:
            # Frame estático (modo original)
            frame = ler_frame()
            if frame is not None:
                st.image(
                    frame,
                    caption="Feed de vídeo em tempo real com detecções YOLO",
                    use_container_width=True,
                    channels="BGR" if len(frame.shape) == 3 else "RGB"
                )
                
                if len(frame.shape) == 3:
                    st.caption(f"📐 Resolução: {frame.shape[1]}x{frame.shape[0]} | 🎨 Canais: {frame.shape[2]} | 📅 {datetime.now().strftime('%H:%M:%S')}")
            else:
                st.info("⏳ Aguardando o primeiro frame...")
                st.markdown("""
                <div style="padding: 2rem; background: #f0f2f6; border-radius: 10px;">
                    <h4>Verifique:</h4>
                    <ul>
                        <li>✅ Serviço de inferência está rodando</li>
                        <li>✅ Stream RTSP está ativo</li>
                        <li>✅ Diretório de resultados está acessível</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    with col_status:
        st.subheader("📍 Status Detalhado")
        
        # Status de Queda
        status_card = st.container()
        with status_card:
            if status == "queda":
                st.error("""
                <div style="padding: 1rem; border-radius: 10px; background: #fee; border: 2px solid #fcc;">
                    <h3 style="color: #c00; margin: 0;">🚨 QUEDA DETECTADA!</h3>
                    <p style="margin-top: 0.5rem;">Ação imediata necessária!</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            elif status == "ok":
                st.success("""
                <div style="padding: 1rem; border-radius: 10px; background: #efe; border: 2px solid #cfc;">
                    <h3 style="color: #060; margin: 0;">✅ Sistema Operacional</h3>
                    <p style="margin-top: 0.5rem;">Nenhuma queda detectada.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Status desconhecido ou aguardando...")
        
        st.markdown("---")
        
        # Quarto
        st.subheader("🏠 Quarto")
        st.markdown(f"""
        <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">{contagem_quarto}</h2>
            <p style="margin: 0;">pessoa(s) presente(s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Banheiro
        st.subheader("🚿 Banheiro")
        pessoas = status_banheiro.get('pessoas', [])
        
        st.markdown(f"""
        <div style="padding: 1rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    border-radius: 10px; color: white; text-align: center;">
            <h2 style="color: white; margin: 0;">{pessoas_banheiro}</h2>
            <p style="margin: 0;">pessoa(s) presente(s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        if pessoas:
            st.markdown("**⏱️ Tempo no banheiro:**")
            for pessoa in pessoas:
                tempo_min = pessoa.get('tempo_minutos', 0)
                tempo_sec = pessoa.get('tempo_segundos', 0)
                tem_alerta = pessoa.get('alerta', False)
                track_id = pessoa.get('track_id', '?')
                
                tempo_str = f"{tempo_min:02d}:{tempo_sec:02d}"
                
                if tem_alerta:
                    st.error(f"⚠️ Pessoa {track_id}: **{tempo_str}** 🚨")
                else:
                    st.info(f"👤 Pessoa {track_id}: {tempo_str}")
        
        # Botão de captura
        st.markdown("---")
        if st.button("📷 Capturar Frame", use_container_width=True, type="primary"):
            destino, erro = salvar_captura_manual()
            if destino:
                st.success(f"✅ Captura salva!")
                st.code(destino, language=None)
                adicionar_evento("captura", f"Captura manual salva: {os.path.basename(destino)}", "success")
            else:
                st.error(f"❌ {erro}")

with tab2:
    st.subheader("📊 Análises e Estatísticas")
    
    # Opção para carregar dados do banco
    if DB_ENABLED and DB_AVAILABLE:
        st.info("💾 Dados sendo salvos no PostgreSQL. Use o botão abaixo para carregar histórico completo.")
        if st.button("📥 Carregar Histórico do Banco de Dados"):
            try:
                db = get_db_manager()
                
                # Carregar métricas do banco
                metricas_quarto = db.obter_metricas(
                    tipo_metrica='pessoas_quarto',
                    limite=1000
                )
                metricas_banheiro = db.obter_metricas(
                    tipo_metrica='pessoas_banheiro',
                    limite=1000
                )
                
                if metricas_quarto:
                    st.session_state.historico_quarto = [
                        {
                            'timestamp': pd.to_datetime(m['timestamp']),
                            'valor': float(m['valor'])
                        }
                        for m in reversed(metricas_quarto)
                    ]
                
                if metricas_banheiro:
                    st.session_state.historico_banheiro = [
                        {
                            'timestamp': pd.to_datetime(m['timestamp']),
                            'valor': float(m['valor'])
                        }
                        for m in reversed(metricas_banheiro)
                    ]
                
                st.success(f"✅ Carregados {len(metricas_quarto)} registros do quarto e {len(metricas_banheiro)} do banheiro")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao carregar do banco: {e}")
        
        st.markdown("---")
    
    # Gráficos de histórico
    if len(st.session_state.historico_quarto) > 1:
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("**🏠 Histórico - Pessoas no Quarto**")
            df_quarto = pd.DataFrame(list(st.session_state.historico_quarto))
            df_quarto['timestamp'] = pd.to_datetime(df_quarto['timestamp'])
            df_quarto = df_quarto.set_index('timestamp')
            
            st.line_chart(df_quarto['valor'], height=200)
            st.caption(f"Média: {df_quarto['valor'].mean():.1f} | Máx: {df_quarto['valor'].max()} | Min: {df_quarto['valor'].min()}")
        
        with col_graph2:
            st.markdown("**🚿 Histórico - Pessoas no Banheiro**")
            df_banheiro = pd.DataFrame(list(st.session_state.historico_banheiro))
            df_banheiro['timestamp'] = pd.to_datetime(df_banheiro['timestamp'])
            df_banheiro = df_banheiro.set_index('timestamp')
            
            st.line_chart(df_banheiro['valor'], height=200)
            st.caption(f"Média: {df_banheiro['valor'].mean():.1f} | Máx: {df_banheiro['valor'].max()} | Min: {df_banheiro['valor'].min()}")
    
    # Estatísticas detalhadas
    st.markdown("---")
    st.subheader("📈 Estatísticas Detalhadas")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    # Estatísticas do quarto (do banco se disponível)
    stats_quarto = {'media': 0, 'maximo': 0, 'minimo': 0}
    if DB_ENABLED and DB_AVAILABLE:
        try:
            db = get_db_manager()
            stats_quarto = db.obter_estatisticas_ocupacao('quarto')
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
    
    # Fallback para dados em memória
    if stats_quarto.get('maximo', 0) == 0 and st.session_state.historico_quarto:
        stats_quarto['maximo'] = max([h['valor'] for h in st.session_state.historico_quarto], default=0)
        stats_quarto['media'] = sum([h['valor'] for h in st.session_state.historico_quarto]) / len(st.session_state.historico_quarto) if st.session_state.historico_quarto else 0
    
    with stats_col1:
        st.markdown("""
        <div style="padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;">
            <h3>🏠 Quarto</h3>
            <p><strong>Atual:</strong> {}</p>
            <p><strong>Máximo:</strong> {}</p>
            <p><strong>Média:</strong> {:.1f}</p>
        </div>
        """.format(
            contagem_quarto,
            int(stats_quarto.get('maximo', 0)),
            float(stats_quarto.get('media', 0))
        ), unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown("""
        <div style="padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;">
            <h3>🚿 Banheiro</h3>
            <p><strong>Atual:</strong> {}</p>
            <p><strong>Alertas:</strong> {}</p>
        </div>
        """.format(
            pessoas_banheiro,
            len(status_banheiro.get('alertas', []))
        ), unsafe_allow_html=True)
    
    with stats_col3:
        total_eventos = len(st.session_state.eventos)
        # Contar eventos do banco se disponível
        if DB_ENABLED and DB_AVAILABLE:
            try:
                db = get_db_manager()
                eventos_db = db.obter_eventos(limite=10000)
                total_eventos = len(eventos_db)
            except Exception:
                pass
        
        st.markdown(f"""
        <div style="padding: 1rem; background: #f0f2f6; border-radius: 10px; text-align: center;">
            <h3>📊 Eventos</h3>
            <p><strong>Total:</strong> {total_eventos}</p>
            <p><strong>Última hora:</strong> {len([e for e in st.session_state.eventos if (datetime.now() - e['timestamp']).seconds < 3600])}</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.subheader("🚨 Alertas e Eventos")
    
    alertas = status_banheiro.get('alertas', [])
    
    if alertas:
        st.error("### ⚠️ ALERTAS ATIVOS")
        for i, alerta in enumerate(alertas):
            tempo_min = alerta.get('tempo_minutos', 0)
            tempo_sec = alerta.get('tempo_segundos', 0)
            track_id = alerta.get('track_id', '?')
            timestamp_str = alerta.get('timestamp', datetime.now().isoformat())
            
            st.markdown(f"""
            <div style="padding: 1rem; background: #fee; border-left: 5px solid #c00; 
                        border-radius: 5px; margin: 0.5rem 0;">
                <h4 style="color: #c00; margin: 0;">🚨 Alerta #{i+1}</h4>
                <p><strong>Pessoa:</strong> {track_id}</p>
                <p><strong>Tempo no banheiro:</strong> {tempo_min}min {tempo_sec}s</p>
                <p><strong>Horário:</strong> {timestamp_str}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Nenhum alerta ativo no momento.")
    
    st.markdown("---")
    st.subheader("📋 Histórico de Eventos")
    
    eventos_recentes = list(st.session_state.eventos)[-10:]
    if eventos_recentes:
        for evento in reversed(eventos_recentes):
            timestamp_str = evento['timestamp'].strftime("%H:%M:%S")
            severidade = evento['severidade']
            
            if severidade == "error":
                st.error(f"🚨 [{timestamp_str}] {evento['mensagem']}")
            elif severidade == "warning":
                st.warning(f"⚠️ [{timestamp_str}] {evento['mensagem']}")
            else:
                st.info(f"ℹ️ [{timestamp_str}] {evento['mensagem']}")
    else:
        st.info("Nenhum evento registrado ainda.")

with tab4:
    st.subheader("📁 Galeria de Capturas")
    
    capturas = listar_capturas_manuais()
    
    if capturas:
        # Grid de imagens
        num_cols = 3
        for i in range(0, len(capturas), num_cols):
            cols = st.columns(num_cols)
            for j, col in enumerate(cols):
                if i + j < len(capturas):
                    captura_path = capturas[i + j]
                    nome_arquivo = os.path.basename(captura_path)
                    timestamp = os.path.getmtime(captura_path)
                    data_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    
                    try:
                        img = Image.open(captura_path)
                        with col:
                            st.image(img, caption=f"{nome_arquivo}\n{data_str}", use_container_width=True)
                            if st.button(f"🗑️ Deletar", key=f"del_{i+j}"):
                                try:
                                    os.remove(captura_path)
                                    st.success(f"✅ Deletado: {nome_arquivo}")
                                    adicionar_evento("deletar", f"Captura deletada: {nome_arquivo}", "info")
                                    
                                    # Salvar evento no banco se disponível
                                    if DB_ENABLED and DB_AVAILABLE:
                                        try:
                                            persistencia = get_persistencia_manager()
                                            persistencia.salvar_evento(
                                                tipo='captura_deletada',
                                                mensagem=f'Captura deletada: {nome_arquivo}',
                                                severidade='info'
                                            )
                                        except Exception:
                                            pass
                                    
                                    st.rerun() if hasattr(st, 'rerun') else st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao deletar: {e}")
                    except Exception as e:
                        with col:
                            st.error(f"Erro ao carregar: {nome_arquivo}")
    else:
        st.info("📭 Nenhuma captura manual ainda. Use o botão 'Capturar Frame' na aba Monitoramento.")
    
with tab5:
    st.subheader("📄 Relatórios e Exportação")
    
    if not RELATORIOS_AVAILABLE:
        st.warning("⚠️ Módulo de relatórios não disponível. Instale: pip install reportlab openpyxl")
    else:
        col_periodo, col_acoes = st.columns([2, 1])
        
        with col_periodo:
            periodo = st.selectbox(
                "📅 Período do Relatório",
                ['diario', 'semanal', 'mensal'],
                index=0
            )
        
        with col_acoes:
            st.markdown("<br>", unsafe_allow_html=True)
            gerar_relatorio = st.button("📊 Gerar Relatório", use_container_width=True, type="primary")
        
        if gerar_relatorio:
            with st.spinner("Gerando relatórios..."):
                try:
                    relatorio_manager = get_relatorio_manager()
                    
                    # Obter dados do banco se disponível
                    db_manager = None
                    if DB_ENABLED and DB_AVAILABLE:
                        db_manager = get_db_manager()
                    
                    # Gerar relatórios
                    resultado = relatorio_manager.gerar_relatorio_completo(
                        periodo=periodo,
                        db_manager=db_manager
                    )
                    
                    # Mostrar resultados
                    st.success("✅ Relatórios gerados com sucesso!")
                    
                    col_pdf, col_csv, col_excel = st.columns(3)
                    
                    with col_pdf:
                        if resultado['pdf']:
                            st.markdown("**📄 PDF**")
                            st.code(resultado['pdf'], language=None)
                            with open(resultado['pdf'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Baixar PDF",
                                    f.read(),
                                    file_name=Path(resultado['pdf']).name,
                                    mime="application/pdf"
                                )
                    
                    with col_csv:
                        if resultado['csv']:
                            st.markdown("**📊 CSV**")
                            st.code(resultado['csv'], language=None)
                            with open(resultado['csv'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Baixar CSV",
                                    f.read(),
                                    file_name=Path(resultado['csv']).name,
                                    mime="text/csv"
                                )
                    
                    with col_excel:
                        if resultado['excel']:
                            st.markdown("**📈 Excel**")
                            st.code(resultado['excel'], language=None)
                            with open(resultado['excel'], 'rb') as f:
                                st.download_button(
                                    "⬇️ Baixar Excel",
                                    f.read(),
                                    file_name=Path(resultado['excel']).name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatórios: {e}")
                    logger.error(f"Erro ao gerar relatórios: {e}", exc_info=True)
        
        st.markdown("---")
        st.info("💡 Os relatórios incluem eventos, métricas, alertas e estatísticas do período selecionado.")

# Rodapé Premium
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; margin-top: 2rem;">
        <h4 style="color: white; margin: 0;">🛡️ Sistema de Monitoramento Inteligente</h4>
        <p style="margin: 0.5rem 0; opacity: 0.9;">
            Powered by YOLO AI • Streamlit Dashboard Premium
        </p>
        <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
            Última atualização: {} | Versão 2.0
        </p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Adicionar eventos baseados no status
status_atual = ler_status()
if status_atual == "queda":
    # Evitar duplicar eventos
    if not any(e['mensagem'] == "Queda detectada!" for e in st.session_state.eventos[-5:]):
        adicionar_evento("queda", "Queda detectada!", "error")

alertas_atual = len(status_banheiro.get('alertas', []))
if alertas_atual > 0:
    if not any("banheiro" in e['mensagem'].lower() for e in st.session_state.eventos[-5:]):
        adicionar_evento("alerta_banheiro", f"{alertas_atual} alerta(s) ativo(s) no banheiro", "warning")
