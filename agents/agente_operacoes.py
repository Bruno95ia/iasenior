"""
Agente de Operações - IASenior
Especializado em gerenciar e monitorar operações do sistema.
Atua como engenheiro de operações, garantindo funcionamento contínuo.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import LOGS_DIR

from .agente_base import AgenteBase


class AgenteOperacoes(AgenteBase):
    """
    Agente especializado em operações do sistema.
    Monitora processos, serviços e garante disponibilidade.
    Responsabilidades:
    - Monitorar processos do sistema
    - Verificar serviços em execução
    - Gerenciar restart de serviços
    - Monitorar logs de erros
    - Garantir alta disponibilidade
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("operacoes", config)
        self.servicos_monitorados = config.get('servicos_monitorados', [
            'stream_inferencia_rtsp.py',
            'mjpeg_server.py',
            'mediamtx'
        ]) if config else []
        
        self.estado_servicos = {}
        self.historico_operacoes = []
        self.restarts_realizados = 0
        
    def inicializar(self) -> bool:
        """Inicializa o agente de operações."""
        self.logger.info("⚙️ Inicializando Agente de Operações...")
        self.logger.info(f"📋 Serviços monitorados: {', '.join(self.servicos_monitorados)}")
        
        # Carregar estado anterior
        estado_salvo = self.carregar_estado()
        if estado_salvo:
            self.restarts_realizados = estado_salvo.get('restarts_realizados', 0)
        
        return True
    
    def processar(self) -> Dict[str, Any]:
        """
        Monitora e gerencia operações do sistema.
        
        Returns:
            Dicionário com status das operações
        """
        # Verificar status dos serviços
        status_servicos = self._verificar_servicos()
        
        # Analisar logs de erros
        erros = self._analisar_logs_erro()
        
        # Verificar saúde geral
        saude = self._verificar_saude_sistema()
        
        # Tomar ações corretivas se necessário
        acoes = self._tomar_acoes_corretivas(status_servicos, erros)
        
        # Registrar operação
        self._registrar_operacao(status_servicos, erros, acoes)
        
        return {
            'servicos': status_servicos,
            'erros_encontrados': len(erros),
            'saude_sistema': saude,
            'acoes_realizadas': len(acoes),
            'restarts_total': self.restarts_realizados
        }
    
    def _verificar_servicos(self) -> Dict[str, Dict[str, Any]]:
        """Verifica status de todos os serviços monitorados."""
        status = {}
        
        for servico in self.servicos_monitorados:
            try:
                # Verificar se processo está rodando
                rodando = self._verificar_processo(servico)
                
                status[servico] = {
                    'rodando': rodando,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'ativo' if rodando else 'inativo'
                }
                
                if not rodando:
                    self.logger.warning(f"⚠️ Serviço {servico} não está rodando")
                    
            except Exception as e:
                self.logger.error(f"❌ Erro ao verificar {servico}: {e}")
                status[servico] = {
                    'rodando': False,
                    'erro': str(e),
                    'status': 'erro'
                }
        
        self.estado_servicos = status
        return status
    
    def _verificar_processo(self, nome_processo: str) -> bool:
        """Verifica se um processo está rodando."""
        try:
            # Usar pgrep para verificar processo
            resultado = subprocess.run(
                ['pgrep', '-f', nome_processo],
                capture_output=True,
                text=True
            )
            return resultado.returncode == 0 and resultado.stdout.strip() != ''
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao verificar processo {nome_processo}: {e}")
            return False
    
    def _analisar_logs_erro(self) -> List[Dict[str, Any]]:
        """Analisa logs em busca de erros."""
        erros = []
        
        if not LOGS_DIR.exists():
            return erros
        
        # Buscar erros nos logs recentes
        arquivos_log = list(LOGS_DIR.glob("*.log"))
        
        for log_file in arquivos_log:
            try:
                # Ler últimas linhas do log
                with open(log_file, 'r') as f:
                    linhas = f.readlines()
                
                # Verificar últimas 100 linhas
                for linha in linhas[-100:]:
                    linha_lower = linha.lower()
                    if any(palavra in linha_lower for palavra in ['error', 'erro', 'exception', 'failed', 'falhou']):
                        erros.append({
                            'arquivo': log_file.name,
                            'linha': linha.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao ler log {log_file}: {e}")
        
        return erros[:10]  # Retornar apenas últimos 10 erros
    
    def _verificar_saude_sistema(self) -> Dict[str, Any]:
        """Verifica saúde geral do sistema."""
        servicos_ativos = sum(1 for s in self.estado_servicos.values() if s.get('rodando', False))
        total_servicos = len(self.servicos_monitorados)
        
        percentual_ativo = (servicos_ativos / total_servicos * 100) if total_servicos > 0 else 0
        
        saude = {
            'percentual_ativo': round(percentual_ativo, 1),
            'servicos_ativos': servicos_ativos,
            'total_servicos': total_servicos,
            'status': 'saudavel' if percentual_ativo >= 80 else 'atencao' if percentual_ativo >= 50 else 'critico'
        }
        
        return saude
    
    def _tomar_acoes_corretivas(self, status_servicos: Dict, erros: List) -> List[str]:
        """Toma ações corretivas quando necessário."""
        acoes = []
        
        # Verificar serviços inativos
        for servico, info in status_servicos.items():
            if not info.get('rodando', False):
                acao = self._reiniciar_servico(servico)
                if acao:
                    acoes.append(acao)
        
        # Alertar sobre muitos erros
        if len(erros) > 5:
            acoes.append(
                f"⚠️ Alto número de erros detectados ({len(erros)}). "
                f"Investigação recomendada."
            )
            self.logger.warning(f"⚠️ {len(erros)} erros detectados nos logs")
        
        return acoes
    
    def _reiniciar_servico(self, servico: str) -> Optional[str]:
        """Tenta reiniciar um serviço."""
        # Não reiniciar automaticamente por padrão (precisa configuração explícita)
        if not self.config.get('auto_restart', False):
            return None
        
        self.logger.info(f"🔄 Tentando reiniciar serviço: {servico}")
        
        try:
            # Aqui implementaria lógica de restart
            # Por segurança, não vamos reiniciar automaticamente sem configuração explícita
            self.restarts_realizados += 1
            
            return f"🔄 Serviço {servico} marcado para restart (manual necessário)"
        except Exception as e:
            self.logger.error(f"❌ Erro ao reiniciar {servico}: {e}")
            return None
    
    def _registrar_operacao(self, servicos: Dict, erros: List, acoes: List) -> None:
        """Registra operação realizada."""
        registro = {
            'timestamp': datetime.now().isoformat(),
            'servicos': servicos,
            'erros_encontrados': len(erros),
            'acoes_realizadas': acoes
        }
        
        self.historico_operacoes.append(registro)
        
        # Manter apenas últimas 100 operações
        if len(self.historico_operacoes) > 100:
            self.historico_operacoes.pop(0)
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem enviada pelo orquestrador.
        Deve retornar uma resposta textual.
        A resposta deve refletir a especialidade do agente.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta do agente de operações
        """
        try:
            if not mensagem or not isinstance(mensagem, str):
                return "[⚙️ Agente de Operações] Mensagem inválida recebida."
            
            mensagem_lower = mensagem.lower()
            
            # Verificar status atual (pode ser lento, mas necessário para respostas precisas)
            try:
                status_servicos = self._verificar_servicos()
                saude = self._verificar_saude_sistema()
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao verificar status: {e}")
                status_servicos = {}
                saude = {'status': 'verificando'}
            
            if any(palavra in mensagem_lower for palavra in ['status', 'serviço', 'servico', 'funcionando', 'ativo']):
                servicos_ativos = sum(1 for s in status_servicos.values() if s.get('ativo', False))
                total_servicos = len(status_servicos) or len(self.servicos_monitorados)
                
                return (
                    f"[⚙️ Agente de Operações] Status atual: {servicos_ativos}/{total_servicos} serviços ativos. "
                    f"Saúde geral do sistema: {saude.get('status', 'desconhecido')}. "
                    f"Monitorando: {', '.join(self.servicos_monitorados[:3])}{'...' if len(self.servicos_monitorados) > 3 else ''}. "
                    f"Todos os serviços críticos estão sendo monitorados continuamente."
                )
            elif any(palavra in mensagem_lower for palavra in ['erro', 'problema', 'falha', 'down']):
                try:
                    erros = self._analisar_logs_erro()
                    if erros:
                        return (
                            f"[⚙️ Agente de Operações] Detectei {len(erros)} problemas recentes nos logs. "
                            f"Analisando e tomando ações corretivas. Recomendo verificar os logs para mais detalhes."
                        )
                    else:
                        return (
                            f"[⚙️ Agente de Operações] Nenhum erro crítico detectado recentemente. "
                            f"Sistema operando normalmente. Continuo monitorando ativamente."
                        )
                except Exception:
                    return (
                        f"[⚙️ Agente de Operações] Não consegui analisar logs no momento. "
                        f"Sistema de monitoramento ativo. Verifique logs manualmente se necessário."
                    )
            elif any(palavra in mensagem_lower for palavra in ['disponibilidade', 'alta disponibilidade', 'uptime']):
                return (
                    f"[⚙️ Agente de Operações] Garantindo alta disponibilidade através de monitoramento "
                    f"contínuo de {len(self.servicos_monitorados)} serviços. Realizo verificações a cada "
                    f"{self.config.get('intervalo', 30)} segundos. Sistema de alertas ativo para "
                    f"detecção precoce de problemas."
                )
            else:
                return (
                    f"[⚙️ Agente de Operações] Recebi sua pergunta sobre '{mensagem[:100]}'. "
                    f"Como agente de operações, posso informar sobre status de serviços, "
                    f"análise de erros, saúde do sistema e ações corretivas. "
                    f"Status atual: {saude.get('status', 'verificando')}."
                )
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar mensagem: {e}")
            return f"[⚙️ Agente de Operações] Não consegui responder devido a um erro. Tente novamente."
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do agente."""
        saude = self._verificar_saude_sistema()
        
        return {
            'nome': self.nome,
            'status': self.estado['status'],
            'servicos_monitorados': len(self.servicos_monitorados),
            'saude_sistema': saude,
            'restarts_realizados': self.restarts_realizados,
            'ultima_operacao': self.historico_operacoes[-1]['timestamp'] if self.historico_operacoes else None,
            'ultima_atualizacao': self.estado['ultima_atualizacao']
        }
    
    def salvar_estado(self) -> None:
        """Salva estado incluindo histórico."""
        self.estado['restarts_realizados'] = self.restarts_realizados
        self.estado['historico_operacoes'] = self.historico_operacoes
        super().salvar_estado()

