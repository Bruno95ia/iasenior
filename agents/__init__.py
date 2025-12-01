"""
Sistema de Agentes IASenior - Arquitetura Modular de Monitoramento
Cada agente é responsável por uma área específica do sistema.
Todos os agentes agora em português e especializados por área.
"""

from .agente_base import AgenteBase
from .agente_pesquisa import AgentePesquisa
from .agente_visao_computacional import AgenteVisaoComputacional
from .agente_operacoes import AgenteOperacoes
from .agente_seguranca import AgenteSeguranca
from .agente_performance import AgentePerformance
from .agente_predicao_queda import AgentePredicaoQueda
from .agente_mestre_visionario import AgenteMestreVisionario
from .orquestrador import OrquestradorAgentes

# Compatibilidade com código legado (imports em inglês mapeados para português)
from .agente_base import AgenteBase as BaseAgent
from .agente_pesquisa import AgentePesquisa as ResearchAgent
from .agente_visao_computacional import AgenteVisaoComputacional as ComputerVisionAgent
from .agente_operacoes import AgenteOperacoes as OperationsAgent
from .agente_seguranca import AgenteSeguranca as SecurityAgent
from .agente_performance import AgentePerformance as PerformanceAgent
from .agente_predicao_queda import AgentePredicaoQueda as FallPredictionAgent
from .agente_mestre_visionario import AgenteMestreVisionario as StrategicVisionAgent

__all__ = [
    # Novos agentes em português
    'AgenteBase',
    'AgentePesquisa',
    'AgenteVisaoComputacional',
    'AgenteOperacoes',
    'AgenteSeguranca',
    'AgentePerformance',
    'AgentePredicaoQueda',
    'AgenteMestreVisionario',
    'OrquestradorAgentes',
    # Compatibilidade (inglês)
    'BaseAgent',
    'ResearchAgent',
    'ComputerVisionAgent',
    'OperationsAgent',
    'SecurityAgent',
    'PerformanceAgent',
    'FallPredictionAgent',
    'StrategicVisionAgent',
]

__version__ = '2.0.0'
