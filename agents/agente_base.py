"""
Agente Base - IASenior
Classe base para todos os agentes do sistema.
Fornece estrutura comum e funcionalidades básicas.
"""

import threading
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional


class AgenteBase(ABC):
    """
    Classe base abstrata para todos os agentes do sistema.
    Fornece estrutura comum para inicialização, execução e finalização.
    """
    
    def __init__(self, nome: str, config: Dict[str, Any] = None):
        """
        Inicializa o agente.
        
        Args:
            nome: Nome único do agente em português
            config: Dicionário com configurações específicas do agente
        """
        self.nome = nome
        self.config = config or {}
        self.rodando = False
        self.thread = None
        self.logger = self._configurar_logger()
        
        # Estado do agente
        self.estado = {
            'status': 'parado',
            'iniciado_em': None,
            'ultima_atualizacao': None,
            'metricas': {}
        }
        
        # Diretório de dados do agente
        self.diretorio_dados = Path(self.config.get('diretorio_dados', 'agents_data')) / self.nome
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"🤖 Agente {self.nome} inicializado")
    
    def _configurar_logger(self) -> logging.Logger:
        """Configura logger específico para o agente."""
        logger = logging.getLogger(f"agente.{self.nome}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.nome} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    def processar(self) -> Dict[str, Any]:
        """
        Método principal de processamento do agente.
        Deve ser implementado por cada agente específico.
        
        Returns:
            Dicionário com resultados do processamento
        """
        pass
    
    @abstractmethod
    def obter_status(self) -> Dict[str, Any]:
        """
        Retorna status atual do agente.
        
        Returns:
            Dicionário com informações de status
        """
        pass
    
    def inicializar(self) -> bool:
        """
        Inicializa recursos específicos do agente.
        Pode ser sobrescrito por agentes filhos.
        
        Returns:
            True se inicialização bem-sucedida
        """
        self.logger.info(f"🔧 Inicializando agente {self.nome}...")
        return True
    
    def finalizar(self) -> None:
        """
        Finaliza recursos do agente.
        Pode ser sobrescrito por agentes filhos.
        """
        self.logger.info(f"🛑 Finalizando agente {self.nome}...")
        self.rodando = False
    
    def _loop_execucao(self) -> None:
        """Loop principal de execução do agente."""
        self.logger.info(f"🚀 Agente {self.nome} iniciado")
        self.estado['status'] = 'rodando'
        self.estado['iniciado_em'] = datetime.now().isoformat()
        
        try:
            while self.rodando:
                try:
                    # Processar
                    resultado = self.processar()
                    
                    # Atualizar estado
                    self.estado['ultima_atualizacao'] = datetime.now().isoformat()
                    if resultado:
                        self.estado['metricas'].update(resultado)
                    
                    # Sleep configurável
                    tempo_espera = self.config.get('intervalo', 1.0)
                    time.sleep(tempo_espera)
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro no loop de processamento: {e}", exc_info=True)
                    time.sleep(5)  # Aguardar antes de tentar novamente
                    
        except KeyboardInterrupt:
            self.logger.info(f"🛑 Agente {self.nome} interrompido pelo usuário")
        except Exception as e:
            self.logger.critical(f"❌ Erro crítico no agente {self.nome}: {e}", exc_info=True)
        finally:
            self.estado['status'] = 'parado'
            self.finalizar()
    
    def iniciar(self) -> bool:
        """
        Inicia o agente em uma thread separada.
        
        Returns:
            True se iniciado com sucesso
        """
        if self.rodando:
            self.logger.warning(f"⚠️ Agente {self.nome} já está rodando")
            return False
        
        if not self.inicializar():
            self.logger.error(f"❌ Falha ao inicializar agente {self.nome}")
            return False
        
        self.rodando = True
        self.thread = threading.Thread(target=self._loop_execucao, daemon=True)
        self.thread.start()
        
        self.logger.info(f"✅ Agente {self.nome} iniciado em thread separada")
        return True
    
    def parar(self, timeout: float = 5.0) -> bool:
        """
        Para o agente.
        
        Args:
            timeout: Tempo máximo para aguardar parada (segundos)
        
        Returns:
            True se parado com sucesso
        """
        if not self.rodando:
            return True
        
        self.logger.info(f"🛑 Parando agente {self.nome}...")
        self.rodando = False
        
        if self.thread:
            self.thread.join(timeout=timeout)
            if self.thread.is_alive():
                self.logger.warning(f"⚠️ Thread do agente {self.nome} não parou no tempo")
                return False
        
        return True
    
    def salvar_estado(self) -> None:
        """Salva estado do agente em arquivo."""
        try:
            arquivo_estado = self.diretorio_dados / "estado.json"
            with open(arquivo_estado, 'w') as f:
                json.dump(self.estado, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estado: {e}")
    
    def carregar_estado(self) -> Optional[Dict[str, Any]]:
        """Carrega estado do agente de arquivo."""
        try:
            arquivo_estado = self.diretorio_dados / "estado.json"
            if arquivo_estado.exists():
                with open(arquivo_estado, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar estado: {e}")
        return None
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem/pergunta recebida do orquestrador.
        Método padrão que pode ser sobrescrito por agentes específicos.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta do agente em formato de string
        """
        # Implementação padrão - agentes específicos devem sobrescrever
        return f"[{self.nome}] Recebi sua mensagem: '{mensagem}'. Como agente especializado em minha área, preciso de mais contexto para fornecer uma resposta adequada."
    
    @property
    def running(self) -> bool:
        """Compatibilidade com código existente."""
        return self.rodando
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(nome='{self.nome}', status='{self.estado['status']}')>"

