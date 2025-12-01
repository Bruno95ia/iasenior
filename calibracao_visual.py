"""
Wizard de Calibração Visual - IASenior
Interface visual para configurar áreas de monitoramento (quarto/banheiro).
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import ROOM_AREA, BATHROOM_AREA, FRAME_PATH, FRAME_WIDTH, FRAME_HEIGHT


class CalibracaoVisual:
    """
    Wizard de calibração visual para configurar áreas de monitoramento.
    """
    
    def __init__(self):
        """Inicializa o wizard de calibração."""
        self.frame_path = FRAME_PATH
        self.frame_width = FRAME_WIDTH
        self.frame_height = FRAME_HEIGHT
    
    def desenhar_area(self, frame: np.ndarray, area: Tuple[float, float, float, float], 
                     cor: Tuple[int, int, int] = (0, 255, 0), label: str = "") -> np.ndarray:
        """
        Desenha uma área retangular no frame.
        
        Args:
            frame: Frame numpy
            area: Área em coordenadas normalizadas (x1, y1, x2, y2)
            cor: Cor RGB
            label: Label para exibir
        
        Returns:
            Frame com área desenhada
        """
        frame_copy = frame.copy()
        x1, y1, x2, y2 = area
        
        # Converter para pixels
        x1_px = int(x1 * self.frame_width)
        y1_px = int(y1 * self.frame_height)
        x2_px = int(x2 * self.frame_width)
        y2_px = int(y2 * self.frame_height)
        
        # Desenhar retângulo
        cv2.rectangle(frame_copy, (x1_px, y1_px), (x2_px, y2_px), cor, 3)
        
        # Desenhar label
        if label:
            cv2.putText(
                frame_copy, label,
                (x1_px, y1_px - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, cor, 2
            )
        
        return frame_copy
    
    def criar_interface_calibracao(self):
        """
        Cria interface Streamlit para calibração visual.
        """
        st.title("🎯 Calibração Visual de Áreas")
        st.markdown("Configure as áreas de monitoramento arrastando os sliders abaixo.")
        
        # Carregar frame atual
        frame_atual = None
        if Path(self.frame_path).exists():
            try:
                frame_atual = cv2.imread(self.frame_path)
                if frame_atual is not None:
                    frame_atual = cv2.cvtColor(frame_atual, cv2.COLOR_BGR2RGB)
            except Exception as e:
                st.error(f"Erro ao carregar frame: {e}")
        
        if frame_atual is None:
            st.warning("⚠️ Nenhum frame disponível. Inicie o sistema de inferência primeiro.")
            return
        
        # Tabs para quarto e banheiro
        tab_quarto, tab_banheiro = st.tabs(["🏠 Quarto", "🚿 Banheiro"])
        
        with tab_quarto:
            st.subheader("Configurar Área do Quarto")
            
            col_config, col_preview = st.columns([1, 2])
            
            with col_config:
                st.markdown("### 📐 Coordenadas")
                st.info("Coordenadas normalizadas (0.0 a 1.0)")
                
                room_x1 = st.slider("X1 (esquerda)", 0.0, 1.0, ROOM_AREA[0], 0.01, key="room_x1")
                room_y1 = st.slider("Y1 (topo)", 0.0, 1.0, ROOM_AREA[1], 0.01, key="room_y1")
                room_x2 = st.slider("X2 (direita)", 0.0, 1.0, ROOM_AREA[2], 0.01, key="room_x2")
                room_y2 = st.slider("Y2 (fundo)", 0.0, 1.0, ROOM_AREA[3], 0.01, key="room_y2")
                
                # Validar
                if room_x1 >= room_x2:
                    st.error("⚠️ X1 deve ser menor que X2")
                if room_y1 >= room_y2:
                    st.error("⚠️ Y1 deve ser menor que Y2")
                
                nova_area_quarto = [room_x1, room_y1, room_x2, room_y2]
                
                st.markdown("---")
                if st.button("💾 Salvar Configuração do Quarto", use_container_width=True):
                    self.salvar_configuracao_quarto(nova_area_quarto)
                    st.success("✅ Configuração do quarto salva!")
            
            with col_preview:
                st.markdown("### 👁️ Preview")
                frame_preview = self.desenhar_area(
                    frame_atual.copy(),
                    nova_area_quarto,
                    cor=(0, 255, 0),
                    label="QUARTO"
                )
                st.image(frame_preview, use_container_width=True)
                st.caption(f"Área: ({room_x1:.2f}, {room_y1:.2f}) a ({room_x2:.2f}, {room_y2:.2f})")
        
        with tab_banheiro:
            st.subheader("Configurar Área do Banheiro")
            
            col_config, col_preview = st.columns([1, 2])
            
            with col_config:
                st.markdown("### 📐 Coordenadas")
                st.info("Coordenadas normalizadas (0.0 a 1.0)")
                
                bath_x1 = st.slider("X1 (esquerda)", 0.0, 1.0, BATHROOM_AREA[0], 0.01, key="bath_x1")
                bath_y1 = st.slider("Y1 (topo)", 0.0, 1.0, BATHROOM_AREA[1], 0.01, key="bath_y1")
                bath_x2 = st.slider("X2 (direita)", 0.0, 1.0, BATHROOM_AREA[2], 0.01, key="bath_x2")
                bath_y2 = st.slider("Y2 (fundo)", 0.0, 1.0, BATHROOM_AREA[3], 0.01, key="bath_y2")
                
                # Validar
                if bath_x1 >= bath_x2:
                    st.error("⚠️ X1 deve ser menor que X2")
                if bath_y1 >= bath_y2:
                    st.error("⚠️ Y1 deve ser menor que Y2")
                
                nova_area_banheiro = [bath_x1, bath_y1, bath_x2, bath_y2]
                
                st.markdown("---")
                if st.button("💾 Salvar Configuração do Banheiro", use_container_width=True):
                    self.salvar_configuracao_banheiro(nova_area_banheiro)
                    st.success("✅ Configuração do banheiro salva!")
            
            with col_preview:
                st.markdown("### 👁️ Preview")
                frame_preview = self.desenhar_area(
                    frame_atual.copy(),
                    nova_area_banheiro,
                    cor=(255, 0, 0),
                    label="BANHEIRO"
                )
                st.image(frame_preview, use_container_width=True)
                st.caption(f"Área: ({bath_x1:.2f}, {bath_y1:.2f}) a ({bath_x2:.2f}, {bath_y2:.2f})")
        
        # Preview combinado
        st.markdown("---")
        st.subheader("📊 Preview Combinado")
        
        frame_combinado = frame_atual.copy()
        frame_combinado = self.desenhar_area(
            frame_combinado,
            nova_area_quarto,
            cor=(0, 255, 0),
            label="QUARTO"
        )
        frame_combinado = self.desenhar_area(
            frame_combinado,
            nova_area_banheiro,
            cor=(255, 0, 0),
            label="BANHEIRO"
        )
        
        st.image(frame_combinado, use_container_width=True)
        st.caption("Verde = Quarto | Vermelho = Banheiro")
        
        # Exportar configuração
        st.markdown("---")
        if st.button("📥 Exportar Configuração", use_container_width=True):
            config = {
                'room_area': nova_area_quarto,
                'bathroom_area': nova_area_banheiro,
                'timestamp': str(datetime.now())
            }
            st.download_button(
                "⬇️ Baixar JSON",
                json.dumps(config, indent=2),
                file_name="calibracao_areas.json",
                mime="application/json"
            )
    
    def salvar_configuracao_quarto(self, area: list):
        """Salva configuração do quarto em arquivo."""
        config_file = Path("config_areas.json")
        config = {}
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config['room_area'] = area
        config['room_area_updated'] = datetime.now().isoformat()
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def salvar_configuracao_banheiro(self, area: list):
        """Salva configuração do banheiro em arquivo."""
        config_file = Path("config_areas.json")
        config = {}
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        config['bathroom_area'] = area
        config['bathroom_area_updated'] = datetime.now().isoformat()
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)


def criar_pagina_calibracao():
    """Cria página Streamlit para calibração."""
    calibracao = CalibracaoVisual()
    calibracao.criar_interface_calibracao()

