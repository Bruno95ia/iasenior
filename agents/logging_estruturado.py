"""
Sistema de Logging Estruturado - IASenior
Baseado em melhores práticas de produção.
Fornece logging estruturado em formato JSON para análise e monitoramento.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class StructuredLogger:
    """
    Logger estruturado baseado em melhores práticas de produção.
    Gera logs em formato JSON para facilitar análise e integração com sistemas de monitoramento.
    """
    
    def __init__(self, name: str, log_dir: Path = None, console_output: bool = True):
        """
        Inicializa o logger estruturado.
        
        Args:
            name: Nome do logger
            log_dir: Diretório para salvar logs (padrão: logs/)
            console_output: Se True, também imprime no console
        """
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self.console_output = console_output
        
        # Configurar logger padrão
        self.logger = logging.getLogger(f"structured.{name}")
        self.logger.setLevel(logging.INFO)
        
        # Remover handlers existentes para evitar duplicação
        self.logger.handlers.clear()
        
        # Handler de arquivo JSON (JSONL format - uma linha por log)
        json_handler = logging.FileHandler(
            self.log_dir / f"{name}_structured.jsonl",
            encoding='utf-8',
            mode='a'
        )
        
        # Formatter simples (mensagem já será JSON)
        formatter = logging.Formatter('%(message)s')
        json_handler.setFormatter(formatter)
        self.logger.addHandler(json_handler)
        
        # Handler de console (opcional)
        if console_output:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def log_structured(self, level: str, message: str, **kwargs):
        """
        Log estruturado em formato JSON.
        
        Args:
            level: Nível do log ('INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL')
            message: Mensagem principal
            **kwargs: Campos adicionais para incluir no log
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level.upper(),
            'logger': self.name,
            'message': message,
            **kwargs
        }
        
        # Serializar para JSON
        log_json = json.dumps(log_entry, ensure_ascii=False, default=str)
        
        # Logar usando nível apropriado
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, log_json)
    
    def info(self, message: str, **kwargs):
        """Log de informação."""
        self.log_structured('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso."""
        self.log_structured('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro."""
        self.log_structured('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self.log_structured('DEBUG', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self.log_structured('CRITICAL', message, **kwargs)
    
    def log_metric(self, metric_name: str, value: float, unit: str = None, **kwargs):
        """
        Log específico para métricas.
        
        Args:
            metric_name: Nome da métrica
            value: Valor da métrica
            unit: Unidade da métrica (opcional)
            **kwargs: Campos adicionais
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'logger': self.name,
            'type': 'metric',
            'metric_name': metric_name,
            'value': value,
            **kwargs
        }
        
        if unit:
            log_entry['unit'] = unit
        
        log_json = json.dumps(log_entry, ensure_ascii=False, default=str)
        self.logger.info(log_json)
    
    def log_event(self, event_type: str, description: str, **kwargs):
        """
        Log específico para eventos.
        
        Args:
            event_type: Tipo do evento
            description: Descrição do evento
            **kwargs: Campos adicionais
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'logger': self.name,
            'type': 'event',
            'event_type': event_type,
            'description': description,
            **kwargs
        }
        
        log_json = json.dumps(log_entry, ensure_ascii=False, default=str)
        self.logger.info(log_json)


def criar_logger_estruturado(name: str, log_dir: Path = None, console_output: bool = True) -> StructuredLogger:
    """
    Função auxiliar para criar um logger estruturado.
    
    Args:
        name: Nome do logger
        log_dir: Diretório para logs
        console_output: Se True, também imprime no console
    
    Returns:
        Instância de StructuredLogger
    """
    return StructuredLogger(name, log_dir, console_output)

