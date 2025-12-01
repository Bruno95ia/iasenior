"""
Página de Calibração Visual - Dashboard IASenior
Wizard para configurar áreas de monitoramento.
"""

import streamlit as st
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from calibracao_visual import criar_pagina_calibracao

# Configuração da página
st.set_page_config(
    page_title="Calibração Visual - IASenior",
    page_icon="🎯",
    layout="wide"
)

# Criar página de calibração
criar_pagina_calibracao()

