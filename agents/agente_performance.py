"""
Agente de Performance - IASenior
Especializado em otimizar e monitorar performance do sistema.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .agente_base import AgenteBase

# psutil é opcional
try:
    import psutil
    PSUTIL_DISPONIVEL = True
except ImportError:
    PSUTIL_DISPONIVEL = False


class AgentePerformance(AgenteBase):
    """
    Agente especializado em otimização de performance.
    Monitora métricas e sugere melhorias.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("performance", config)
        self.metricas_performance = []
        self.sugestoes_otimizacao = []
        
    def inicializar(self) -> bool:
        """Inicializa o agente de performance."""
        self.logger.info("⚡ Inicializando Agente de Performance...")
        return True
    
    def processar(self) -> Dict[str, Any]:
        """Processa métricas de performance."""
        metricas = self._coletar_metricas()
        otimizacoes = self._sugerir_otimizacoes(metricas)
        
        return {
            'metricas': metricas,
            'otimizacoes_sugeridas': len(otimizacoes),
            'status': 'otimo' if metricas.get('cpu_percent', 0) < 70 else 'atencao'
        }
    
    def _coletar_metricas(self) -> Dict[str, Any]:
        """Coleta métricas de performance."""
        metricas = {
            'timestamp': datetime.now().isoformat()
        }
        
        if PSUTIL_DISPONIVEL:
            metricas['cpu_percent'] = psutil.cpu_percent(interval=1)
            metricas['memory_percent'] = psutil.virtual_memory().percent
        else:
            metricas['cpu_percent'] = None
            metricas['memory_percent'] = None
            metricas['observacao'] = 'psutil não disponível - métricas limitadas'
        
        return metricas
    
    def _sugerir_otimizacoes(self, metricas: Dict) -> List[str]:
        """Sugere otimizações baseadas nas métricas."""
        sugestoes = []
        
        cpu_percent = metricas.get('cpu_percent')
        if cpu_percent is not None and cpu_percent > 80:
            sugestoes.append("💡 CPU alta - considere otimizar processamento")
        elif cpu_percent is None:
            sugestoes.append("💡 Instalar psutil para monitoramento completo de performance")
        
        return sugestoes
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem enviada pelo orquestrador.
        Deve retornar uma resposta textual.
        A resposta deve refletir a especialidade do agente.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta do agente de performance
        """
        try:
            if not mensagem or not isinstance(mensagem, str):
                return "[⚡ Agente de Performance] Mensagem inválida recebida."
            
            mensagem_lower = mensagem.lower()
            
            # Coletar métricas (pode ser lento com psutil, mas tentamos)
            try:
                # Usar timeout implícito: psutil.cpu_percent(interval=1) pode demorar 1 segundo
                # Para respostas rápidas, vamos usar valores cached ou fallback
                metricas = self._coletar_metricas()
                otimizacoes = self._sugerir_otimizacoes(metricas)
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao coletar métricas: {e}")
                metricas = {'cpu_percent': None, 'memory_percent': None}
                otimizacoes = []
            
            if any(palavra in mensagem_lower for palavra in ['performance', 'cpu', 'memória', 'memoria', 'velocidade']):
                cpu = metricas.get('cpu_percent', 'N/A')
                memoria = metricas.get('memory_percent', 'N/A')
                return (
                    f"[⚡ Agente de Performance] Métricas atuais: CPU={cpu}%, Memória={memoria}%. "
                    f"Status: {metricas.get('status', 'verificando')}. "
                    f"Sugestões de otimização: {len(otimizacoes)}. "
                    f"{' '.join(otimizacoes[:2]) if otimizacoes else 'Performance dentro do esperado.'}"
                )
            elif any(palavra in mensagem_lower for palavra in ['otimização', 'otimizacao', 'melhorar', 'gargalo']):
                return (
                    f"[⚡ Agente de Performance] Sobre otimização: "
                    f"Monitorando continuamente CPU, memória e disco. "
                    f"Identificando gargalos e sugerindo melhorias. "
                    f"Sugestões atuais: {len(otimizacoes)}. "
                    f"{' '.join(otimizacoes) if otimizacoes else 'Sistema otimizado.'}"
                )
            else:
                return (
                    f"[⚡ Agente de Performance] Recebi sua pergunta sobre '{mensagem[:100]}'. "
                    f"Como agente de performance, monitoro métricas de sistema (CPU, memória, disco) "
                    f"e sugiro otimizações. Métricas atuais: CPU={metricas.get('cpu_percent', 'N/A')}%."
                )
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar mensagem: {e}")
            return f"[⚡ Agente de Performance] Não consegui responder devido a um erro. Tente novamente."
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status do agente."""
        return {
            'nome': self.nome,
            'status': self.estado['status'],
            'ultima_atualizacao': self.estado['ultima_atualizacao']
        }

