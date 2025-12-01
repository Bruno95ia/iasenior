#!/bin/bash

echo "🟢 Ativando ambiente do painel (venv)..."
source venv/bin/activate

echo "📺 Subindo painel Streamlit..."
cd painel_IA/app
streamlit run dashboard.py --server.port=8501 --server.enableCORS=false

deactivate
