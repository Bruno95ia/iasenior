"""
Orquestrador de Agentes - Sistema IASenior
Gerencia ciclo de vida, coordenação e comunicação entre agentes especializados.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import signal

from .agente_base import AgenteBase
from .agente_pesquisa import AgentePesquisa
from .agente_visao_computacional import AgenteVisaoComputacional
from .agente_operacoes import AgenteOperacoes
from .agente_seguranca import AgenteSeguranca
from .agente_performance import AgentePerformance
from .agente_predicao_queda import AgentePredicaoQueda
from .agente_mestre_visionario import AgenteMestreVisionario

logger = logging.getLogger(__name__)


class OrquestradorAgentes:
    """
    Orquestrador central para gerenciar todos os agentes especializados.
    """
    
    def __init__(self, 
                 diretorio_dados: str = "agents_data",
                 padrao_orquestracao: str = "paralelo",
                 max_retries: int = 3,
                 timeout_agente: int = 3):
        """
        Inicializa o orquestrador.
        
        Args:
            diretorio_dados: Diretório para dados dos agentes
            padrao_orquestracao: "paralelo", "sequencial" ou "magnetico"
            max_retries: Número máximo de tentativas
            timeout_agente: Timeout em segundos para respostas dos agentes
        """
        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_dados.mkdir(exist_ok=True)
        
        self.padrao_orquestracao = padrao_orquestracao
        self.max_retries = max_retries
        self.timeout_agente = timeout_agente
        
        self.agentes: Dict[str, AgenteBase] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Classes de agentes disponíveis
        self.classes_agentes = {
            'pesquisa': AgentePesquisa,
            'visao_computacional': AgenteVisaoComputacional,
            'operacoes': AgenteOperacoes,
            'seguranca': AgenteSeguranca,
            'performance': AgentePerformance,
            'predicao_queda': AgentePredicaoQueda,
            'mestre_visionario': AgenteMestreVisionario,
        }
    
    def inicializar_agentes(self, agentes_habilitados: Optional[List[str]] = None):
        """
        Inicializa todos os agentes ou apenas os especificados.
        
        Args:
            agentes_habilitados: Lista de nomes de agentes para inicializar.
                                Se None, inicializa todos.
        """
        agentes_para_inicializar = agentes_habilitados or list(self.classes_agentes.keys())
        
        for nome_agente, classe_agente in self.classes_agentes.items():
            if nome_agente in agentes_para_inicializar:
                try:
                    diretorio_agente = self.diretorio_dados / nome_agente
                    diretorio_agente.mkdir(exist_ok=True)
                    
                    agente = classe_agente(diretorio_dados=str(diretorio_agente))
                    self.agentes[nome_agente] = agente
                    
                    logger.info(f"✅ Agente '{nome_agente}' inicializado")
                except Exception as e:
                    logger.error(f"❌ Erro ao inicializar agente '{nome_agente}': {e}")
    
    def iniciar_agentes(self):
        """Inicia todos os agentes em threads separadas."""
        for nome, agente in self.agentes.items():
            try:
                thread = threading.Thread(
                    target=agente.iniciar,
                    name=f"Thread-{nome}",
                    daemon=True
                )
                thread.start()
                self.threads[nome] = thread
                logger.info(f"🚀 Agente '{nome}' iniciado")
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar agente '{nome}': {e}")
    
    def parar_todos(self):
        """Para todos os agentes."""
        for nome, agente in self.agentes.items():
            try:
                agente.parar()
                logger.info(f"🛑 Agente '{nome}' parado")
            except Exception as e:
                logger.error(f"❌ Erro ao parar agente '{nome}': {e}")
    
    def aguardar(self):
        """Aguarda indefinidamente (até interrupção)."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Interrompido pelo usuário")
            self.parar_todos()
    
    def processar_pergunta(self, pergunta: str) -> Dict[str, Any]:
        """
        Processa uma pergunta enviando para todos os agentes.
        
        Args:
            pergunta: Pergunta a ser processada
            
        Returns:
            Dict com respostas de todos os agentes
        """
        respostas = {}
        total_agentes = len(self.agentes)
        agentes_responderam = 0
        
        if self.padrao_orquestracao == "paralelo":
            # Processar em paralelo
            futures = {}
            for nome, agente in self.agentes.items():
                future = self.executor.submit(self._processar_com_timeout, agente, pergunta)
                futures[nome] = future
            
            for nome, future in futures.items():
                try:
                    resultado = future.result(timeout=self.timeout_agente)
                    respostas[nome] = resultado
                    if resultado['status'] == 'sucesso':
                        agentes_responderam += 1
                except FutureTimeoutError:
                    respostas[nome] = {
                        'status': 'timeout',
                        'resposta': 'Timeout ao processar mensagem',
                        'erro': 'Timeout'
                    }
                except Exception as e:
                    respostas[nome] = {
                        'status': 'erro',
                        'resposta': '',
                        'erro': str(e)
                    }
        else:
            # Processar sequencialmente
            for nome, agente in self.agentes.items():
                resultado = self._processar_com_timeout(agente, pergunta)
                respostas[nome] = resultado
                if resultado['status'] == 'sucesso':
                    agentes_responderam += 1
        
        return {
            'pergunta': pergunta,
            'respostas': respostas,
            'total_agentes': total_agentes,
            'agentes_responderam': agentes_responderam
        }
    
    def debate(self, pergunta: str) -> Dict[str, Any]:
        """
        Realiza um debate em 2 rodadas entre agentes.
        
        Args:
            pergunta: Pergunta para debate
            
        Returns:
            Dict com resultados das rodadas
        """
        # Rodada 1: Respostas iniciais
        rodada1 = self.processar_pergunta(pergunta)
        
        # Rodada 2: Comentários sobre as respostas
        comentarios = {}
        for nome_agente, dados in rodada1['respostas'].items():
            if dados['status'] == 'sucesso':
                # Criar contexto com outras respostas
                outras_respostas = [
                    f"{outro_nome}: {outro_dados.get('resposta', '')[:100]}"
                    for outro_nome, outro_dados in rodada1['respostas'].items()
                    if outro_nome != nome_agente and outro_dados.get('status') == 'sucesso'
                ]
                contexto = f"Outras respostas: {' | '.join(outras_respostas)}"
                pergunta_comentario = f"Comente sobre: {pergunta}\n\nContexto: {contexto}"
                
                resultado = self._processar_com_timeout(
                    self.agentes[nome_agente],
                    pergunta_comentario
                )
                comentarios[nome_agente] = resultado
        
        return {
            'pergunta': pergunta,
            'rodada1': rodada1,
            'rodada2': {
                'comentarios': comentarios,
                'total': len(comentarios)
            }
        }
    
    def resposta_final(self, respostas: Dict[str, Any]) -> str:
        """
        Consolida respostas em uma resposta final.
        
        Args:
            respostas: Dict com respostas dos agentes
            
        Returns:
            String com resposta consolidada
        """
        if 'respostas' in respostas:
            # Formato de processar_pergunta
            respostas_dict = respostas['respostas']
        elif 'rodada1' in respostas:
            # Formato de debate
            respostas_dict = respostas['rodada1']['respostas']
        else:
            respostas_dict = respostas
        
        respostas_validas = [
            dados.get('resposta', '')
            for dados in respostas_dict.values()
            if dados.get('status') == 'sucesso' and dados.get('resposta')
        ]
        
        if not respostas_validas:
            return "Não foi possível obter respostas dos agentes."
        
        # Consolidar respostas
        resposta_consolidada = "\n\n".join([
            f"• {resp}" for resp in respostas_validas
        ])
        
        return f"Resposta Consolidada:\n\n{resposta_consolidada}"
    
    def _processar_com_timeout(self, agente: AgenteBase, mensagem: str) -> Dict[str, Any]:
        """
        Processa mensagem com timeout e retry.
        
        Args:
            agente: Agente para processar
            mensagem: Mensagem a processar
            
        Returns:
            Dict com resultado
        """
        for tentativa in range(self.max_retries):
            try:
                resposta = agente.processar_mensagem(mensagem)
                return {
                    'status': 'sucesso',
                    'resposta': resposta,
                    'tentativas': tentativa + 1
                }
            except Exception as e:
                if tentativa == self.max_retries - 1:
                    return {
                        'status': 'erro',
                        'resposta': '',
                        'erro': str(e),
                        'tentativas': tentativa + 1
                    }
                time.sleep(0.1 * (tentativa + 1))  # Backoff exponencial
        
        return {
            'status': 'erro',
            'resposta': 'Erro após múltiplas tentativas',
            'erro': 'Max retries exceeded'
        }
    
    def obter_status_agentes(self) -> Dict[str, Any]:
        """
        Obtém status de todos os agentes.
        
        Returns:
            Dict com status de cada agente
        """
        status = {}
        for nome, agente in self.agentes.items():
            try:
                status[nome] = agente.obter_status()
            except Exception as e:
                status[nome] = {
                    'ativo': False,
                    'erro': str(e)
                }
        return status

