"""
Agente de Predição Pró-Ativa de Risco de Queda - IASenior
Especializado em antecipar padrões de risco antes que uma queda ocorra.
Usa aprendizado preditivo para prevenir incidentes.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque
import sys
import math

# numpy é opcional
try:
    import numpy as np
    NUMPY_DISPONIVEL = True
except ImportError:
    NUMPY_DISPONIVEL = False
    # Funções básicas de fallback
    def np_std(values):
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def np_mean(values):
        return sum(values) / len(values) if values else 0.0
    
    def np_sqrt(x):
        return math.sqrt(x)
    
    def np_random_uniform(low, high):
        import random
        return random.uniform(low, high)
    
    # Criar namespace fake
    class FakeNP:
        @staticmethod
        def std(values):
            return np_std(values)
        @staticmethod
        def mean(values):
            return np_mean(values)
        @staticmethod
        def sqrt(x):
            return np_sqrt(x)
        @staticmethod
        def random():
            class Random:
                uniform = staticmethod(np_random_uniform)
            return Random()
    
    np = FakeNP()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import FRAME_PATH, STATUS_PATH, RESULTS_DIR

from .agente_base import AgenteBase


class AgentePredicaoQueda(AgenteBase):
    """
    Agente especializado em predição pró-ativa de risco de queda.
    Analisa padrões temporais para antecipar quedas antes que ocorram.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("predicao_risco_queda", config)
        
        # Configurações de predição
        self.janela_temporal = config.get('janela_temporal', 30) if config else 30  # segundos
        self.threshold_risco = config.get('threshold_risco', 0.7) if config else 0.7
        self.tipo_modelo = config.get('modelo_predicao', 'lstm') if config else 'lstm'
        self.integrar_tracking = config.get('integrar_tracking', True) if config else True
        
        # Histórico de padrões de movimento
        self.historico_posicoes = deque(maxlen=1000)  # Últimas 1000 posições
        self.historico_comportamento = deque(maxlen=500)
        
        # Alertas gerados
        self.alertas_proativos = []
        self.risco_atual = 0.0
        
        # Modelo de predição (pode ser implementado com LSTM/Transformer)
        self.modelo_predicao = None
        
    def inicializar(self) -> bool:
        """Inicializa o agente de predição."""
        self.logger.info("🧠 Inicializando Agente de Predição Pró-Ativa de Risco de Queda...")
        self.logger.info(f"📊 Janela temporal: {self.janela_temporal} segundos")
        self.logger.info(f"⚠️ Threshold de risco: {self.threshold_risco}")
        self.logger.info(f"🤖 Modelo de predição: {self.tipo_modelo}")
        
        # Carregar histórico anterior
        estado_salvo = self.carregar_estado()
        if estado_salvo:
            self.historico_posicoes = deque(
                estado_salvo.get('historico_posicoes', []),
                maxlen=1000
            )
            self.risco_atual = estado_salvo.get('risco_atual', 0.0)
        
        # Inicializar modelo de predição simples (pode ser expandido)
        self._inicializar_modelo_predicao()
        
        return True
    
    def _inicializar_modelo_predicao(self):
        """Inicializa modelo de predição simples."""
        # Por enquanto, usa heurísticas baseadas em padrões
        # Pode ser expandido para LSTM/Transformer real
        self.logger.info("🤖 Modelo de predição inicializado (heurístico)")
    
    def processar(self) -> Dict[str, Any]:
        """
        Processa padrões temporais e prediz risco de queda.
        
        Returns:
            Dicionário com análise preditiva e alertas
        """
        # Coletar dados atuais
        dados_atuais = self._coletar_dados_movimento()
        
        if dados_atuais:
            # Adicionar ao histórico
            self.historico_posicoes.append(dados_atuais)
            
            # Analisar padrões temporais
            padroes = self._analisar_padroes_temporais()
            
            # Predizer risco
            risco_predito = self._predizer_risco(padroes)
            self.risco_atual = risco_predito
            
            # Gerar alertas se necessário
            alertas = self._gerar_alertas_proativos(risco_predito, padroes)
            
            # Recomendações preventivas
            recomendacoes = self._gerar_recomendacoes_preventivas(padroes, risco_predito)
            
            return {
                'risco_predito': risco_predito,
                'padroes_detectados': padroes,
                'alertas_gerados': len(alertas),
                'recomendacoes': recomendacoes,
                'historico_tamanho': len(self.historico_posicoes)
            }
        
        return {
            'risco_predito': 0.0,
            'status': 'sem_dados'
        }
    
    def _coletar_dados_movimento(self) -> Optional[Dict[str, Any]]:
        """Coleta dados de movimento do frame atual."""
        # Tentar usar tracking primeiro se habilitado
        if self.integrar_tracking:
            dados_tracking = self._coletar_dados_com_tracking()
            if dados_tracking:
                return dados_tracking
        
        # Fallback para método básico
        try:
            # Ler status atual
            status = "unknown"
            if Path(STATUS_PATH).exists():
                with open(STATUS_PATH, 'r') as f:
                    status = f.read().strip().lower()
            
            # Tentar extrair informações do frame (se disponível)
            # Por enquanto, usa heurísticas baseadas em status e histórico
            dados = {
                'timestamp': datetime.now().isoformat(),
                'status_sistema': status,
                'tempo_unix': datetime.now().timestamp()
            }
            
            # Adicionar informações de posição (simulado - pode ser expandido)
            # Em implementação real, analisaria posições de pessoas no frame
            dados['posicao_x'] = np.random.uniform(0.0, 1.0)  # Simulado
            dados['posicao_y'] = np.random.uniform(0.0, 1.0)  # Simulado
            
            return dados
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao coletar dados de movimento: {e}")
            return None
    
    def _coletar_dados_com_tracking(self) -> Optional[Dict[str, Any]]:
        """
        Coleta dados integrando com sistema de tracking (ByteTrack).
        Baseado em melhores práticas de detecção de quedas.
        """
        try:
            # Tentar ler dados de tracking se disponível
            tracking_file = Path("resultados/tracking_data.json")
            if tracking_file.exists():
                with open(tracking_file, 'r') as f:
                    tracking_data = json.load(f)
                
                # Extrair informações de posição e velocidade do tracking
                if tracking_data.get('tracks') and len(tracking_data['tracks']) > 0:
                    track = tracking_data['tracks'][0]  # Primeiro track
                    
                    # Calcular razão altura/largura da bbox
                    bbox_width = track.get('width', 0)
                    bbox_height = track.get('height', 0)
                    razao_bbox = bbox_height / bbox_width if bbox_width > 0 else 1.0
                    
                    return {
                        'timestamp': datetime.now().isoformat(),
                        'posicao_x': track.get('center_x', 0.5),
                        'posicao_y': track.get('center_y', 0.5),
                        'velocidade_x': track.get('velocity_x', 0.0),
                        'velocidade_y': track.get('velocity_y', 0.0),
                        'bbox_width': bbox_width,
                        'bbox_height': bbox_height,
                        'razao_bbox': razao_bbox,
                        'track_id': track.get('id', -1),
                        'confianca': track.get('confidence', 0.0),
                        'tempo_unix': datetime.now().timestamp(),
                        'fonte': 'tracking'
                    }
        except Exception as e:
            self.logger.debug(f"⚠️ Erro ao coletar dados de tracking: {e}")
        
        return None
    
    def _analisar_padroes_temporais(self) -> Dict[str, Any]:
        """Analisa padrões temporais no histórico."""
        if len(self.historico_posicoes) < 10:
            return {'status': 'dados_insuficientes'}
        
        # Obter último registro para informações de tracking
        ultimo_registro = list(self.historico_posicoes)[-1] if self.historico_posicoes else {}
        
        # Calcular métricas temporais
        padroes = {
            'estabilidade_postural': self._calcular_estabilidade(),
            'velocidade_movimento': self._calcular_velocidade(),
            'variacao_posicao': self._calcular_variacao_posicao(),
            'anomalias_detectadas': self._detectar_anomalias()
        }
        
        # Adicionar informações de tracking se disponíveis
        if ultimo_registro.get('fonte') == 'tracking':
            padroes['velocidade_x'] = ultimo_registro.get('velocidade_x', 0.0)
            padroes['velocidade_y'] = ultimo_registro.get('velocidade_y', 0.0)
            padroes['bbox_width'] = ultimo_registro.get('bbox_width', 0)
            padroes['bbox_height'] = ultimo_registro.get('bbox_height', 0)
            padroes['razao_bbox'] = ultimo_registro.get('razao_bbox', 1.0)
            padroes['posicao_y'] = ultimo_registro.get('posicao_y', 0.5)
        
        return padroes
    
    def _calcular_estabilidade(self) -> float:
        """Calcula estabilidade postural baseada em variação de posições."""
        if len(self.historico_posicoes) < 5:
            return 1.0  # Estável por padrão
        
        # Calcular variação de posições Y (altura)
        posicoes_y = [d.get('posicao_y', 0.5) for d in list(self.historico_posicoes)[-20:]]
        
        if len(posicoes_y) < 2:
            return 1.0
        
        variacao = np.std(posicoes_y)
        estabilidade = max(0.0, 1.0 - variacao * 2)  # Normalizado 0-1
        
        return round(estabilidade, 3)
    
    def _calcular_velocidade(self) -> float:
        """Calcula velocidade média de movimento."""
        if len(self.historico_posicoes) < 2:
            return 0.0
        
        posicoes_recentes = list(self.historico_posicoes)[-10:]
        
        distancias = []
        for i in range(1, len(posicoes_recentes)):
            p1 = posicoes_recentes[i-1]
            p2 = posicoes_recentes[i]
            
            x1, y1 = p1.get('posicao_x', 0.5), p1.get('posicao_y', 0.5)
            x2, y2 = p2.get('posicao_x', 0.5), p2.get('posicao_y', 0.5)
            
            distancia = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            tempo = p2.get('tempo_unix', 0) - p1.get('tempo_unix', 0)
            
            if tempo > 0:
                velocidade = distancia / tempo
                distancias.append(velocidade)
        
        velocidade_media = np.mean(distancias) if distancias else 0.0
        return round(velocidade_media, 4)
    
    def _calcular_variacao_posicao(self) -> float:
        """Calcula variação total de posição."""
        if len(self.historico_posicoes) < 2:
            return 0.0
        
        posicoes_recentes = list(self.historico_posicoes)[-20:]
        posicoes_x = [d.get('posicao_x', 0.5) for d in posicoes_recentes]
        posicoes_y = [d.get('posicao_y', 0.5) for d in posicoes_recentes]
        
        var_x = np.std(posicoes_x) if len(posicoes_x) > 1 else 0.0
        var_y = np.std(posicoes_y) if len(posicoes_y) > 1 else 0.0
        
        variacao_total = np.sqrt(var_x**2 + var_y**2)
        return round(variacao_total, 4)
    
    def _detectar_anomalias(self) -> List[str]:
        """Detecta anomalias comportamentais."""
        anomalias = []
        
        # Verificar estabilidade
        estabilidade = self._calcular_estabilidade()
        if estabilidade < 0.5:
            anomalias.append("Instabilidade postural detectada")
        
        # Verificar velocidade
        velocidade = self._calcular_velocidade()
        if velocidade > 0.1:  # Movimento muito rápido
            anomalias.append("Movimento rápido detectado")
        
        # Verificar variação
        variacao = self._calcular_variacao_posicao()
        if variacao > 0.3:
            anomalias.append("Grande variação de posição")
        
        return anomalias
    
    def _predizer_risco(self, padroes: Dict[str, Any]) -> float:
        """
        Prediz risco de queda baseado em padrões.
        Usa heurísticas melhoradas baseadas em pesquisas sobre detecção de quedas.
        
        Returns:
            Risco entre 0.0 (baixo) e 1.0 (alto)
        """
        if padroes.get('status') == 'dados_insuficientes':
            return 0.0
        
        risco = 0.0
        
        # Fatores de risco baseados em pesquisas sobre detecção de quedas
        
        # 1. Estabilidade postural (menor estabilidade = maior risco)
        estabilidade = padroes.get('estabilidade_postural', 1.0)
        risco_estabilidade = (1.0 - estabilidade) * 0.3  # Peso de 30%
        
        # 2. Velocidade de movimento (maior velocidade = maior risco)
        velocidade = padroes.get('velocidade_movimento', 0.0)
        risco_velocidade = min(1.0, velocidade * 10) * 0.2  # Peso de 20%
        
        # 3. Variação de posição (maior variação = maior risco)
        variacao = padroes.get('variacao_posicao', 0.0)
        risco_variacao = min(1.0, variacao * 3) * 0.15  # Peso de 15%
        
        # 4. Anomalias (cada anomalia aumenta risco)
        anomalias = padroes.get('anomalias_detectadas', [])
        risco_anomalias = min(1.0, len(anomalias) * 0.1) * 0.1  # Peso de 10%
        
        # 5. Fatores adicionais baseados em tracking (se disponível)
        risco_tracking = self._calcular_risco_com_ml(padroes) * 0.25  # Peso de 25%
        
        # Calcular risco total
        risco = risco_estabilidade + risco_velocidade + risco_variacao + risco_anomalias + risco_tracking
        
        # Normalizar para 0-1
        risco = max(0.0, min(1.0, risco))
        
        return round(risco, 3)
    
    def _calcular_risco_com_ml(self, padroes: Dict[str, Any]) -> float:
        """
        Calcula risco usando heurísticas melhoradas baseadas em ML.
        Por enquanto, usa heurísticas baseadas em pesquisas sobre detecção de quedas.
        Fatores baseados em pesquisas:
        1. Razão altura/largura da bbox (pessoa deitada = maior risco)
        2. Velocidade vertical descendente
        3. Aceleração negativa
        4. Proximidade do chão
        """
        risco = 0.0
        
        # Fator 1: Razão bbox (altura/largura)
        # Se temos dados de tracking, usar razão real
        if 'razao_bbox' in padroes:
            razao = padroes['razao_bbox']
            # Razão < 1.2 indica pessoa possivelmente deitada
            if razao < 1.2:
                risco += 0.4
            elif razao < 1.5:
                risco += 0.2
        elif 'bbox_height' in padroes and 'bbox_width' in padroes:
            altura = padroes.get('bbox_height', 1.0)
            largura = padroes.get('bbox_width', 1.0)
            if largura > 0:
                razao = altura / largura
                if razao < 1.2:
                    risco += 0.4
                elif razao < 1.5:
                    risco += 0.2
        
        # Fator 2: Velocidade vertical
        velocidade_y = padroes.get('velocidade_y', 0.0)
        if velocidade_y < -0.05:  # Movimento descendente rápido
            risco += 0.3
        elif velocidade_y < -0.02:  # Movimento descendente moderado
            risco += 0.15
        
        # Fator 3: Velocidade horizontal (movimento lateral rápido pode indicar perda de equilíbrio)
        velocidade_x = abs(padroes.get('velocidade_x', 0.0))
        if velocidade_x > 0.1:
            risco += 0.2
        elif velocidade_x > 0.05:
            risco += 0.1
        
        # Fator 4: Proximidade do chão (posição Y alta = próximo do chão)
        posicao_y = padroes.get('posicao_y', 0.5)
        if posicao_y > 0.8:  # Próximo do chão
            risco += 0.1
        
        return min(1.0, risco)
    
    def _gerar_alertas_proativos(self, risco: float, padroes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera alertas proativos se risco exceder threshold."""
        alertas = []
        
        if risco >= self.threshold_risco:
            alerta = {
                'tipo': 'risco_queda_alto',
                'timestamp': datetime.now().isoformat(),
                'risco_predito': risco,
                'threshold': self.threshold_risco,
                'padroes': padroes,
                'severidade': 'alta',
                'mensagem': f"⚠️ Risco de queda detectado: {risco*100:.1f}%"
            }
            
            alertas.append(alerta)
            self.alertas_proativos.append(alerta)
            
            # Salvar alerta
            self._salvar_alerta(alerta)
            
            self.logger.warning(
                f"🚨 ALERTA PRÓ-ATIVO: Risco de queda predito: {risco*100:.1f}% "
                f"(threshold: {self.threshold_risco*100}%)"
            )
        
        return alertas
    
    def _gerar_recomendacoes_preventivas(self, padroes: Dict[str, Any], risco: float) -> List[str]:
        """Gera recomendações preventivas baseadas em análise."""
        recomendacoes = []
        
        if risco > 0.5:
            recomendacoes.append("💡 Verificar área ao redor da pessoa - possíveis obstáculos")
            recomendacoes.append("💡 Considerar ajuste de iluminação para melhor visibilidade")
        
        estabilidade = padroes.get('estabilidade_postural', 1.0)
        if estabilidade < 0.6:
            recomendacoes.append("💡 Monitorar padrões de movimento - instabilidade detectada")
        
        anomalias = padroes.get('anomalias_detectadas', [])
        if len(anomalias) > 0:
            recomendacoes.append(f"💡 Investigar anomalias comportamentais: {', '.join(anomalias)}")
        
        return recomendacoes
    
    def _salvar_alerta(self, alerta: Dict[str, Any]):
        """Salva alerta em arquivo."""
        try:
            alertas_dir = self.diretorio_dados / "alertas"
            alertas_dir.mkdir(exist_ok=True)
            
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            alerta_file = alertas_dir / f"alerta_risco_{timestamp_str}.json"
            
            with open(alerta_file, 'w') as f:
                json.dump(alerta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar alerta: {e}")
    
    def obter_risco_atual(self) -> float:
        """Retorna risco atual predito."""
        return self.risco_atual
    
    def obter_historico_risco(self, ultimos_minutos: int = 60) -> List[Dict[str, Any]]:
        """Retorna histórico de risco dos últimos minutos."""
        cutoff_time = datetime.now() - timedelta(minutes=ultimos_minutos)
        
        historico = []
        for alerta in self.alertas_proativos:
            try:
                alerta_time = datetime.fromisoformat(alerta['timestamp'])
                if alerta_time >= cutoff_time:
                    historico.append(alerta)
            except:
                continue
        
        return historico
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem enviada pelo orquestrador.
        Deve retornar uma resposta textual.
        A resposta deve refletir a especialidade do agente.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta do agente de predição de queda
        """
        try:
            if not mensagem or not isinstance(mensagem, str):
                return "[🧠 Agente de Predição de Queda] Mensagem inválida recebida."
            
            mensagem_lower = mensagem.lower()
            
            # Analisar padrões apenas se houver dados suficientes (pode ser lento)
            try:
                if len(self.historico_posicoes) >= 10:
                    padroes = self._analisar_padroes_temporais()
                else:
                    padroes = {}
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao analisar padrões: {e}")
                padroes = {}
            
            if any(palavra in mensagem_lower for palavra in ['risco', 'queda', 'predição', 'predicao', 'prevenção', 'prevencao']):
                risco_pct = self.risco_atual * 100
                return (
                    f"[🧠 Agente de Predição de Queda] Risco atual predito: {risco_pct:.1f}% "
                    f"(threshold: {self.threshold_risco*100}%). "
                    f"Analisando padrões temporais de movimento, estabilidade postural e anomalias. "
                    f"Alertas proativos gerados: {len(self.alertas_proativos)}. "
                    f"Histórico analisado: {len(self.historico_posicoes)} pontos de dados."
                )
            elif any(palavra in mensagem_lower for palavra in ['padrão', 'padrao', 'comportamento', 'movimento']):
                return (
                    f"[🧠 Agente de Predição de Queda] Sobre padrões: "
                    f"Analisando estabilidade postural, velocidade de movimento, variação de posição "
                    f"e anomalias comportamentais. Janela temporal: {self.janela_temporal}s. "
                    f"Modelo: {self.tipo_modelo}. Padrões atuais: {len(padroes)} métricas."
                )
            else:
                return (
                    f"[🧠 Agente de Predição de Queda] Recebi sua pergunta sobre '{mensagem[:100]}'. "
                    f"Como agente de predição, analiso padrões temporais para antecipar riscos de queda. "
                    f"Risco atual: {self.risco_atual*100:.1f}%."
                )
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar mensagem: {e}")
            return f"[🧠 Agente de Predição de Queda] Não consegui responder devido a um erro. Tente novamente."
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do agente."""
        padroes = self._analisar_padroes_temporais() if len(self.historico_posicoes) >= 10 else {}
        
        return {
            'nome': self.nome,
            'status': self.estado['status'],
            'risco_atual': self.risco_atual,
            'threshold_risco': self.threshold_risco,
            'janela_temporal': self.janela_temporal,
            'modelo_predicao': self.tipo_modelo,
            'historico_tamanho': len(self.historico_posicoes),
            'alertas_proativos_total': len(self.alertas_proativos),
            'padroes_atuais': padroes,
            'ultima_atualizacao': self.estado['ultima_atualizacao']
        }
    
    def salvar_estado(self) -> None:
        """Salva estado incluindo histórico."""
        self.estado['historico_posicoes'] = list(self.historico_posicoes)
        self.estado['risco_atual'] = self.risco_atual
        super().salvar_estado()

