#!/usr/bin/env python3
"""
Script para iniciar todos os agentes especializados do sistema IASenior.
Agentes agora em português e especializados por área.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orquestrador import OrquestradorAgentes
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Função principal."""
    logger.info("🚀 Iniciando Sistema de Agentes Especializados IASenior...")
    
    # Configuração dos agentes especializados
    config = {
        'diretorio_dados': 'agents_data',
        'agentes_desabilitados': [],  # Lista de agentes a desabilitar (opcional)
        'incluir_agentes_legados': False,  # Manter False para usar apenas agentes novos
        'agentes': {
            'pesquisa': {
                'intervalo': 300.0,  # Pesquisa a cada 5 minutos
                'areas_pesquisa': [
                    'visao_computacional',
                    'yolo',
                    'operacoes',
                    'performance',
                    'seguranca'
                ]
            },
            'engenharia_visao_computacional': {
                'intervalo': 60.0,  # Analisa a cada 1 minuto
            },
            'operacoes': {
                'intervalo': 30.0,  # Verifica a cada 30 segundos
                'servicos_monitorados': [
                    'stream_inferencia_rtsp.py',
                    'mjpeg_server.py',
                    'mediamtx'
                ],
                'auto_restart': False  # Por segurança, não reiniciar automaticamente
            },
            'seguranca': {
                'intervalo': 60.0,  # Verifica a cada 1 minuto
            },
            'performance': {
                'intervalo': 30.0,  # Verifica a cada 30 segundos
            },
            'predicao_risco_queda': {
                'intervalo': 60.0,  # Analisa a cada 1 minuto
                'janela_temporal': 30,  # Segundos de histórico analisado
                'threshold_risco': 0.7,  # Limite para gerar alerta (70%)
                'modelo_predicao': 'lstm'  # Tipo de modelo: 'lstm', 'transformer', 'temporal_cnn'
            }
        }
    }
    
    # Criar orquestrador
    try:
        orquestrador = OrquestradorAgentes(config)
        
        # Inicializar agentes
        if not orquestrador.inicializar_agentes():
            logger.error("❌ Falha ao inicializar agentes")
            return 1
        
        # Iniciar todos os agentes
        if not orquestrador.iniciar_todos():
            logger.error("❌ Falha ao iniciar agentes")
            return 1
        
        logger.info("✅ Sistema de Agentes Especializados IASenior iniciado com sucesso!")
        logger.info("📊 Use Ctrl+C para parar o sistema")
        
        # Mostrar status inicial
        status = orquestrador.obter_status_sistema()
        logger.info(f"📈 Status: {status['orquestrador']['agentes_rodando']}/{status['orquestrador']['total_agentes']} agentes ativos")
        
        # Listar agentes ativos
        logger.info("\n🤖 Agentes Especializados Ativos:")
        for nome, info_status in status['agentes'].items():
            status_agente = info_status.get('status', 'desconhecido')
            logger.info(f"  • {nome}: {status_agente}")
        
        # Aguardar indefinidamente (até Ctrl+C)
        orquestrador.aguardar()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrompido pelo usuário")
        orquestrador.parar_todos()
        return 0
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
