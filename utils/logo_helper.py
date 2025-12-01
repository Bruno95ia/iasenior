"""
Helper para carregar e exibir a logo do sistema.
"""

from pathlib import Path
from PIL import Image
import streamlit as st

# Caminho base
BASE_DIR = Path(__file__).parent.parent
LOGO_DIR = BASE_DIR / "assets" / "logo"

def get_logo_path():
    """
    Retorna o caminho da logo, tentando diferentes formatos e nomes.
    """
    # Ordem de prioridade
    possiveis_logos = [
        "logo.png",
        "logo.jpg",
        "logo.jpeg",
        "logo.svg",
        "logo_white.png",
        "logo_white.jpg",
    ]
    
    for logo_name in possiveis_logos:
        logo_path = LOGO_DIR / logo_name
        if logo_path.exists():
            return logo_path
    
    return None

def carregar_logo():
    """
    Carrega a logo como objeto PIL Image.
    Retorna None se não encontrar.
    """
    logo_path = get_logo_path()
    if logo_path and logo_path.exists():
        try:
            return Image.open(logo_path)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            return None
    return None

def exibir_logo_streamlit(largura=200, alinhamento="center", margin_bottom="1rem"):
    """
    Exibe a logo no Streamlit.
    
    Args:
        largura: Largura da logo em pixels
        alinhamento: "center", "left", "right"
        margin_bottom: Margem inferior (ex: "1rem", "0")
    """
    logo_path = get_logo_path()
    if logo_path and logo_path.exists():
        try:
            st.image(str(logo_path), width=largura)
        except Exception as e:
            st.warning(f"Erro ao exibir logo: {e}")
    else:
        # Fallback: exibir texto estilizado
        st.markdown(f"""
            <div style="text-align: {alinhamento}; margin-bottom: {margin_bottom};">
                <h1 style="color: #667eea; margin: 0;">🛡️ IA Senior</h1>
            </div>
        """, unsafe_allow_html=True)

def exibir_logo_html(largura=200, alinhamento="center", margin_bottom="1rem"):
    """
    Retorna HTML para exibir a logo.
    
    Args:
        largura: Largura da logo em pixels
        alinhamento: "center", "left", "right"
        margin_bottom: Margem inferior
    """
    logo_path = get_logo_path()
    if logo_path and logo_path.exists():
        # Usar caminho relativo para web
        logo_url = f"/assets/logo/{logo_path.name}"
        return f"""
        <div style="text-align: {alinhamento}; margin-bottom: {margin_bottom};">
            <img src="{logo_url}" alt="IA Senior Logo" width="{largura}" style="max-width: 100%; height: auto;">
        </div>
        """
    else:
        # Fallback
        return f"""
        <div style="text-align: {alinhamento}; margin-bottom: {margin_bottom};">
            <h1 style="color: #667eea; margin: 0;">🛡️ IA Senior</h1>
        </div>
        """

def exibir_logo_com_texto_streamlit(titulo="IA Senior", subtitulo="", largura_logo=150):
    """
    Exibe logo com texto ao lado (layout horizontal).
    """
    logo_path = get_logo_path()
    
    if logo_path and logo_path.exists():
        col1, col2 = st.columns([1, 4])
        with col1:
            try:
                st.image(str(logo_path), width=largura_logo)
            except:
                pass
        with col2:
            st.markdown(f"""
                <div style="padding-top: 1rem;">
                    <h1 style="color: #1a202c; margin: 0;">{titulo}</h1>
                    {f'<p style="color: #2d3748; margin-top: 0.5rem;">{subtitulo}</p>' if subtitulo else ''}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="color: #667eea; margin: 0;">🛡️ {titulo}</h1>
                {f'<p style="color: #2d3748; margin-top: 0.5rem;">{subtitulo}</p>' if subtitulo else ''}
            </div>
        """, unsafe_allow_html=True)

def logo_existe():
    """Verifica se a logo existe."""
    return get_logo_path() is not None

