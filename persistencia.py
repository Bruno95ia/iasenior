"""
Módulo de Persistência - IASenior
Integra o sistema com o banco de dados PostgreSQL para salvar dados automaticamente.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from config import DB_ENABLED, STATUS_PATH, ROOM_COUNT_PATH, BATHROOM_STATUS_PATH
from database import get_db_manager

logger = logging.getLogger(__name__)


class PersistenciaManager:
    """
    Gerenciador de persistência que salva dados do sistema no banco de dados.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de persistência."""
        self.db_enabled = DB_ENABLED
        self.db_manager = None
        
        if self.db_enabled:
            try:
                self.db_manager = get_db_manager()
                logger.info("✅ Persistência habilitada - dados serão salvos no PostgreSQL")
            except Exception as e:
                logger.warning(f"⚠️ Banco de dados não disponível: {e}. Persistência desabilitada.")
                self.db_enabled = False
        else:
            logger.info("ℹ️ Persistência desabilitada (DB_ENABLED=false)")
    
    def salvar_status_sistema(self, status: str, metadata: Dict = None):
        """
        Salva status do sistema (ok, queda, erro).
        
        Args:
            status: Status do sistema
            metadata: Dados adicionais
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            if status == "queda":
                # Salvar como evento crítico
                self.db_manager.inserir_evento(
                    tipo='queda_detectada',
                    mensagem='Queda detectada pelo sistema',
                    severidade='error',
                    metadata=metadata
                )
                
                # Criar alerta
                self.db_manager.inserir_alerta(
                    tipo_alerta='queda',
                    titulo='Queda Detectada',
                    mensagem='O sistema detectou uma possível queda',
                    severidade='critical',
                    metadata=metadata
                )
            elif status == "ok":
                # Evento informativo
                self.db_manager.inserir_evento(
                    tipo='status_ok',
                    mensagem='Sistema operacional normalmente',
                    severidade='info',
                    metadata=metadata
                )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar status: {e}")
    
    def salvar_ocupacao_quarto(self, quantidade: int, metadata: Dict = None):
        """
        Salva ocupação do quarto.
        
        Args:
            quantidade: Número de pessoas no quarto
            metadata: Dados adicionais
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            # Salvar no histórico de ocupação
            self.db_manager.inserir_ocupacao(
                area='quarto',
                quantidade=quantidade,
                metadata=metadata
            )
            
            # Salvar como métrica
            self.db_manager.inserir_metrica(
                tipo_metrica='pessoas_quarto',
                valor=float(quantidade),
                unidade='pessoas',
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar ocupação do quarto: {e}")
    
    def salvar_ocupacao_banheiro(self, quantidade: int, pessoas: list = None, alertas: list = None, metadata: Dict = None):
        """
        Salva ocupação do banheiro e alertas.
        
        Args:
            quantidade: Número de pessoas no banheiro
            pessoas: Lista de pessoas com tempo
            alertas: Lista de alertas ativos
            metadata: Dados adicionais
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            # Salvar no histórico de ocupação
            self.db_manager.inserir_ocupacao(
                area='banheiro',
                quantidade=quantidade,
                metadata=metadata
            )
            
            # Salvar como métrica
            self.db_manager.inserir_metrica(
                tipo_metrica='pessoas_banheiro',
                valor=float(quantidade),
                unidade='pessoas',
                metadata=metadata
            )
            
            # Salvar alertas de banheiro
            if alertas:
                for alerta in alertas:
                    track_id = alerta.get('track_id', 'desconhecido')
                    tempo_min = alerta.get('tempo_minutos', 0)
                    tempo_sec = alerta.get('tempo_segundos', 0)
                    
                    # Salvar no monitoramento de banheiro
                    self.db_manager.inserir_evento(
                        tipo='alerta_banheiro',
                        mensagem=f'Pessoa {track_id} no banheiro há {tempo_min}min {tempo_sec}s',
                        severidade='warning',
                        metadata=alerta
                    )
                    
                    # Criar alerta se ainda não existir
                    self.db_manager.inserir_alerta(
                        tipo_alerta='banheiro_tempo',
                        titulo=f'Tempo no Banheiro Excedido',
                        mensagem=f'Pessoa {track_id} está no banheiro há mais de {tempo_min} minutos',
                        severidade='warning',
                        metadata=alerta
                    )
            
            # Salvar informações de pessoas no banheiro
            if pessoas:
                for pessoa in pessoas:
                    track_id = pessoa.get('track_id', 'desconhecido')
                    tempo_segundos = pessoa.get('tempo_minutos', 0) * 60 + pessoa.get('tempo_segundos', 0)
                    tem_alerta = pessoa.get('alerta', False)
                    
                    # Salvar no monitoramento de banheiro
                    try:
                        conn = self.db_manager.get_connection()
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO monitoramento_banheiro (track_id, tempo_segundos, alerta, metadata, timestamp)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                str(track_id),
                                tempo_segundos,
                                tem_alerta,
                                str(pessoa),
                                datetime.now()
                            ))
                            conn.commit()
                        self.db_manager.return_connection(conn)
                    except Exception as e:
                        logger.error(f"❌ Erro ao salvar monitoramento de banheiro: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Erro ao salvar ocupação do banheiro: {e}")
    
    def salvar_metrica(self, tipo: str, valor: float, unidade: str = None, metadata: Dict = None):
        """
        Salva uma métrica genérica.
        
        Args:
            tipo: Tipo da métrica (ex: 'fps', 'latencia', 'cpu')
            valor: Valor da métrica
            unidade: Unidade (ex: 'fps', 'ms', '%')
            metadata: Dados adicionais
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            self.db_manager.inserir_metrica(
                tipo_metrica=tipo,
                valor=valor,
                unidade=unidade,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métrica: {e}")
    
    def salvar_evento(self, tipo: str, mensagem: str, severidade: str = 'info', metadata: Dict = None):
        """
        Salva um evento genérico.
        
        Args:
            tipo: Tipo do evento
            mensagem: Mensagem do evento
            severidade: Severidade ('info', 'warning', 'error')
            metadata: Dados adicionais
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            self.db_manager.inserir_evento(
                tipo=tipo,
                mensagem=mensagem,
                severidade=severidade,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar evento: {e}")
    
    def sincronizar_arquivos_existentes(self):
        """
        Sincroniza dados dos arquivos existentes para o banco de dados.
        Útil para migração inicial.
        """
        if not self.db_enabled or not self.db_manager:
            return
        
        try:
            # Ler status atual
            if Path(STATUS_PATH).exists():
                with open(STATUS_PATH, 'r') as f:
                    status = f.read().strip().lower()
                    if status:
                        self.salvar_status_sistema(status)
            
            # Ler contagem do quarto
            if Path(ROOM_COUNT_PATH).exists():
                try:
                    with open(ROOM_COUNT_PATH, 'r') as f:
                        quantidade = int(f.read().strip())
                        self.salvar_ocupacao_quarto(quantidade)
                except (ValueError, FileNotFoundError):
                    pass
            
            # Ler status do banheiro
            if Path(BATHROOM_STATUS_PATH).exists():
                try:
                    import json
                    with open(BATHROOM_STATUS_PATH, 'r') as f:
                        status_banheiro = json.load(f)
                        pessoas_banheiro = status_banheiro.get('pessoas_no_banheiro', 0)
                        pessoas = status_banheiro.get('pessoas', [])
                        alertas = status_banheiro.get('alertas', [])
                        self.salvar_ocupacao_banheiro(pessoas_banheiro, pessoas, alertas)
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            logger.info("✅ Sincronização de arquivos concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar arquivos: {e}")


# Instância global
_persistencia_manager = None


def get_persistencia_manager() -> PersistenciaManager:
    """
    Obtém instância global do gerenciador de persistência.
    
    Returns:
        Instância de PersistenciaManager
    """
    global _persistencia_manager
    if _persistencia_manager is None:
        _persistencia_manager = PersistenciaManager()
    return _persistencia_manager

