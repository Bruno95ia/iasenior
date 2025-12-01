"""
Agente de Engenharia de Visão Computacional - IASenior
Especialista em YOLO e técnicas de visão computacional.
Monitora, otimiza e melhora o sistema de detecção.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import time
from collections import deque

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import MODEL_PATH, CONFIDENCE_THRESHOLD, FRAME_WIDTH, FRAME_HEIGHT, FPS

from .agente_base import AgenteBase


class AgenteVisaoComputacional(AgenteBase):
    """
    Agente especializado em engenharia de visão computacional.
    Atua como especialista em YOLO e técnicas de detecção.
    Responsabilidades:
    - Monitorar performance do modelo YOLO
    - Sugerir otimizações
    - Analisar qualidade das detecções
    - Recomendar ajustes de parâmetros
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("engenharia_visao_computacional", config)
        self.metricas_modelo = {}
        self.historico_performance = []
        self.sugestoes_otimizacao = []
        
        # Cache de frames processados
        self.cache_frames = {}  # Cache de frames processados
        self.max_cache_size = config.get('max_cache_size', 100) if config else 100
        
        # Métricas em tempo real
        self.metricas_tempo_real = {
            'fps_medio': 0.0,
            'latencia_inferencia': 0.0,
            'uso_memoria': 0.0,
            'gpu_utilization': 0.0,
            'batch_size': 1
        }
        
        # Histórico de métricas para cálculo de médias
        self.historico_fps = deque(maxlen=100)
        self.historico_latencia = deque(maxlen=100)
        
    def inicializar(self) -> bool:
        """Inicializa o agente de visão computacional."""
        self.logger.info("👁️ Inicializando Agente de Engenharia de Visão Computacional...")
        self.logger.info(f"📦 Modelo: {MODEL_PATH}")
        self.logger.info(f"⚙️ Configurações: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {FPS}fps")
        
        # Verificar modelo
        if not Path(MODEL_PATH).exists():
            self.logger.warning(f"⚠️ Modelo não encontrado: {MODEL_PATH}")
        
        # Carregar histórico
        estado_salvo = self.carregar_estado()
        if estado_salvo:
            self.historico_performance = estado_salvo.get('historico_performance', [])
        
        return True
    
    def processar(self) -> Dict[str, Any]:
        """
        Processa e analisa o sistema de visão computacional.
        
        Returns:
            Dicionário com análise e recomendações
        """
        # Coletar métricas do modelo
        metricas = self._coletar_metricas()
        
        # Analisar performance
        analise = self._analisar_performance(metricas)
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(metricas, analise)
        
        # Verificar qualidade das detecções
        qualidade = self._avaliar_qualidade_deteccoes()
        
        # Registrar histórico
        self._registrar_historico(metricas, analise)
        
        return {
            'metricas': metricas,
            'analise': analise,
            'recomendacoes': recomendacoes,
            'qualidade': qualidade,
            'modelo': MODEL_PATH
        }
    
    def _coletar_metricas(self) -> Dict[str, Any]:
        """Coleta métricas do modelo YOLO."""
        metricas = {
            'modelo': MODEL_PATH,
            'confidence_threshold': CONFIDENCE_THRESHOLD,
            'resolucao': f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
            'fps_configurado': FPS,
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar tamanho do modelo
        if Path(MODEL_PATH).exists():
            tamanho_mb = Path(MODEL_PATH).stat().st_size / (1024 * 1024)
            metricas['tamanho_modelo_mb'] = round(tamanho_mb, 2)
        
        # Verificar arquivos de resultados
        resultados_dir = Path("resultados")
        if resultados_dir.exists():
            frame_path = resultados_dir / "ultima_frame.jpg"
            if frame_path.exists():
                metricas['ultima_deteccao'] = datetime.fromtimestamp(
                    frame_path.stat().st_mtime
                ).isoformat()
        
        # Adicionar métricas em tempo real
        metricas.update(self._coletar_metricas_tempo_real())
        
        return metricas
    
    def _coletar_metricas_tempo_real(self) -> Dict[str, Any]:
        """
        Coleta métricas em tempo real do sistema de inferência.
        Baseado em melhores práticas YOLOv8.
        """
        try:
            import psutil
        except ImportError:
            # Se psutil não estiver disponível, retornar métricas básicas
            return {
                'cpu_percent': 0.0,
                'memoria_mb': 0.0,
                'memoria_percent': 0.0
            }
        
        metricas = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memoria_mb': psutil.virtual_memory().used / (1024 * 1024),
            'memoria_percent': psutil.virtual_memory().percent
        }
        
        # Tentar ler métricas de arquivo de status (se existir)
        status_file = Path("resultados/metricas_tempo_real.json")
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    metricas_externas = json.load(f)
                    metricas.update(metricas_externas)
            except Exception:
                pass
        
        # Calcular FPS médio do histórico
        if self.historico_fps:
            metricas['fps_medio'] = sum(self.historico_fps) / len(self.historico_fps)
        
        # Calcular latência média
        if self.historico_latencia:
            metricas['latencia_inferencia_ms'] = (sum(self.historico_latencia) / len(self.historico_latencia)) * 1000
        
        # Atualizar métricas internas
        self.metricas_tempo_real.update({
            'fps_medio': metricas.get('fps_medio', 0.0),
            'latencia_inferencia': metricas.get('latencia_inferencia_ms', 0.0) / 1000,
            'uso_memoria': metricas.get('memoria_percent', 0.0)
        })
        
        return metricas
    
    def _analisar_performance(self, metricas: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa performance do sistema."""
        analise = {
            'status': 'ok',
            'observacoes': [],
            'pontos_atencao': []
        }
        
        # Analisar confidence threshold
        if CONFIDENCE_THRESHOLD < 0.3:
            analise['pontos_atencao'].append(
                'Confidence threshold muito baixo pode gerar falsos positivos'
            )
        elif CONFIDENCE_THRESHOLD > 0.7:
            analise['pontos_atencao'].append(
                'Confidence threshold muito alto pode perder detecções válidas'
            )
        else:
            analise['observacoes'].append(
                f'Confidence threshold adequado ({CONFIDENCE_THRESHOLD})'
            )
        
        # Analisar resolução
        resolucao_total = FRAME_WIDTH * FRAME_HEIGHT
        if resolucao_total < 640 * 480:
            analise['pontos_atencao'].append(
                'Resolução baixa pode afetar qualidade das detecções'
            )
        elif resolucao_total > 1920 * 1080:
            analise['pontos_atencao'].append(
                'Resolução alta pode impactar performance'
            )
        
        # Analisar FPS
        if FPS < 15:
            analise['pontos_atencao'].append(
                'FPS baixo pode afetar detecção de movimentos rápidos'
            )
        elif FPS > 30:
            analise['observacoes'].append(
                f'FPS alto ({FPS}) permite detecção mais precisa'
            )
        
        if analise['pontos_atencao']:
            analise['status'] = 'atencao'
        
        return analise
    
    def _gerar_recomendacoes(self, metricas: Dict, analise: Dict) -> List[str]:
        """Gera recomendações de otimização."""
        recomendacoes = []
        
        # Recomendações baseadas em análise
        if analise['status'] == 'atencao':
            for ponto in analise['pontos_atencao']:
                if 'threshold' in ponto.lower():
                    recomendacoes.append(
                        f"💡 Considere ajustar confidence threshold para 0.4-0.5 "
                        f"para melhor balance entre precisão e recall"
                    )
                elif 'resolução' in ponto.lower():
                    recomendacoes.append(
                        f"💡 Para melhor performance, considere resolução 1280x720 "
                        f"ou balancear conforme hardware disponível"
                    )
                elif 'fps' in ponto.lower():
                    recomendacoes.append(
                        f"💡 Para detecção em tempo real, recomenda-se FPS entre 20-30"
                    )
        
        # Recomendações gerais de YOLO
        recomendacoes.extend([
            "💡 Para melhor performance: usar batch processing quando possível",
            "💡 Considerar usar YOLOv8n para menor latência ou YOLOv8m para maior precisão",
            "💡 Aplicar NMS (Non-Maximum Suppression) adequadamente para evitar duplicações",
            "💡 Monitorar uso de GPU/CPU para otimizar recursos"
        ])
        
        # Adicionar recomendações específicas baseadas em métricas
        recomendacoes.extend(self.sugerir_otimizacao_yolo())
        
        return recomendacoes
    
    def sugerir_otimizacao_yolo(self) -> List[str]:
        """
        Sugestões baseadas em documentação oficial YOLOv8 e métricas atuais.
        """
        sugestoes = []
        metricas = self._coletar_metricas_tempo_real()
        
        # Verificar se está usando batch processing
        batch_size = metricas.get('batch_size', 1)
        if batch_size == 1:
            sugestoes.append(
                "💡 YOLOv8: Considere usar batch processing para melhor throughput. "
                "Exemplo: model.predict(imgs, batch=4)"
            )
        
        # Verificar resolução
        resolucao_total = FRAME_WIDTH * FRAME_HEIGHT
        if resolucao_total > 1920 * 1080:
            sugestoes.append(
                "💡 YOLOv8: Resolução muito alta. Considere usar imgsz=640 para melhor performance "
                "ou imgsz=1280 para melhor precisão."
            )
        elif resolucao_total < 640 * 480:
            sugestoes.append(
                "💡 YOLOv8: Resolução baixa pode afetar precisão. Considere aumentar para pelo menos 640x480."
            )
        
        # Verificar uso de GPU
        gpu_util = metricas.get('gpu_utilization', 0)
        if gpu_util > 0 and gpu_util < 50:
            sugestoes.append(
                "💡 YOLOv8: GPU subutilizada. Considere aumentar batch size ou processar múltiplos streams."
            )
        
        # Sugestões de modelo
        if 'yolov8n' in MODEL_PATH.lower():
            sugestoes.append(
                "💡 YOLOv8: Modelo 'nano' detectado. Para melhor precisão, considere 'yolov8s' ou 'yolov8m'. "
                "Para menor latência, mantenha 'yolov8n'."
            )
        elif 'yolov8m' in MODEL_PATH.lower() or 'yolov8l' in MODEL_PATH.lower():
            fps_medio = metricas.get('fps_medio', 0)
            if fps_medio < 15:
                sugestoes.append(
                    "💡 YOLOv8: FPS baixo com modelo grande. Considere usar 'yolov8s' ou 'yolov8n' para melhor performance."
                )
        
        # Verificar latência
        latencia_ms = metricas.get('latencia_inferencia_ms', 0)
        if latencia_ms > 100:
            sugestoes.append(
                f"💡 YOLOv8: Latência alta ({latencia_ms:.1f}ms). Considere reduzir resolução ou usar modelo menor."
            )
        
        return sugestoes
    
    def adicionar_ao_cache(self, frame_id: str, resultado: Dict[str, Any], max_age: float = 5.0):
        """
        Adiciona resultado processado ao cache.
        
        Args:
            frame_id: Identificador único do frame
            resultado: Resultado do processamento
            max_age: Tempo máximo em segundos que o cache é válido
        """
        if len(self.cache_frames) >= self.max_cache_size:
            # Remover item mais antigo
            oldest_key = min(self.cache_frames.keys(), key=lambda k: self.cache_frames[k]['timestamp'])
            del self.cache_frames[oldest_key]
        
        self.cache_frames[frame_id] = {
            'resultado': resultado,
            'timestamp': time.time(),
            'max_age': max_age
        }
    
    def obter_do_cache(self, frame_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém resultado do cache se ainda válido.
        
        Args:
            frame_id: Identificador do frame
        
        Returns:
            Resultado do cache ou None se não encontrado/expirado
        """
        if frame_id not in self.cache_frames:
            return None
        
        cache_entry = self.cache_frames[frame_id]
        age = time.time() - cache_entry['timestamp']
        
        if age > cache_entry['max_age']:
            # Cache expirado
            del self.cache_frames[frame_id]
            return None
        
        return cache_entry['resultado']
    
    def registrar_metricas_performance(self, fps: float = None, latencia: float = None):
        """
        Registra métricas de performance para cálculo de médias.
        
        Args:
            fps: FPS atual
            latencia: Latência em segundos
        """
        if fps is not None:
            self.historico_fps.append(fps)
        if latencia is not None:
            self.historico_latencia.append(latencia)
    
    def _avaliar_qualidade_deteccoes(self) -> Dict[str, Any]:
        """Avalia qualidade das detecções atuais."""
        qualidade = {
            'status': 'desconhecido',
            'observacoes': []
        }
        
        # Verificar se há arquivos de status
        status_path = Path("resultados/status.txt")
        if status_path.exists():
            try:
                with open(status_path, 'r') as f:
                    status = f.read().strip().lower()
                
                if status == 'ok':
                    qualidade['status'] = 'normal'
                    qualidade['observacoes'].append('Sistema detectando normalmente')
                elif status == 'queda':
                    qualidade['status'] = 'alerta'
                    qualidade['observacoes'].append('Queda detectada - sistema funcionando')
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao avaliar qualidade: {e}")
        
        return qualidade
    
    def _registrar_historico(self, metricas: Dict, analise: Dict) -> None:
        """Registra histórico de performance."""
        registro = {
            'timestamp': datetime.now().isoformat(),
            'metricas': metricas,
            'analise': analise
        }
        
        self.historico_performance.append(registro)
        
        # Manter apenas últimas 100 análises
        if len(self.historico_performance) > 100:
            self.historico_performance.pop(0)
        
        # Salvar periodicamente
        self.salvar_estado()
    
    def sugerir_otimizacao(self, area: str) -> List[str]:
        """Sugere otimizações para uma área específica."""
        sugestoes = {
            'modelo': [
                'Considerar usar modelo YOLOv8s para melhor balance',
                'Avaliar necessidade de fine-tuning para casos específicos'
            ],
            'performance': [
                'Implementar cache de frames processados',
                'Usar processamento assíncrono quando possível',
                'Otimizar tamanho de batch'
            ],
            'precisao': [
                'Ajustar confidence threshold baseado em dados reais',
                'Implementar tracking para reduzir falsos positivos',
                'Usar data augmentation para treinamento'
            ]
        }
        
        return sugestoes.get(area, ['Área não mapeada para otimizações'])
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem enviada pelo orquestrador.
        Deve retornar uma resposta textual.
        A resposta deve refletir a especialidade do agente.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta do agente de visão computacional
        """
        try:
            if not mensagem or not isinstance(mensagem, str):
                return "[👁️ Agente de Visão Computacional] Mensagem inválida recebida."
            
            mensagem_lower = mensagem.lower()
            
            if any(palavra in mensagem_lower for palavra in ['yolo', 'modelo', 'detecção', 'deteccao', 'precisão', 'precisao']):
                return (
                    f"[👁️ Agente de Visão Computacional] Sobre YOLO e detecção: "
                    f"Modelo atual: {MODEL_PATH}. Configuração: confidence={CONFIDENCE_THRESHOLD}, "
                    f"resolução={FRAME_WIDTH}x{FRAME_HEIGHT}, FPS={FPS}. "
                    f"Recomendo ajustar confidence threshold baseado em dados reais e considerar "
                    f"otimizações como batch processing e NMS adequado."
                )
            elif any(palavra in mensagem_lower for palavra in ['performance', 'fps', 'velocidade', 'otimização', 'otimizacao']):
                try:
                    sugestoes = self.sugerir_otimizacao('performance')
                    sugestoes_texto = ', '.join(sugestoes[:2]) if sugestoes else 'Nenhuma sugestão no momento'
                except Exception:
                    sugestoes_texto = 'Verificando otimizações...'
                
                return (
                    f"[👁️ Agente de Visão Computacional] Sobre performance: "
                    f"Configuração atual: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {FPS}fps. "
                    f"Sugestões: {sugestoes_texto}. "
                    f"Posso analisar métricas específicas e sugerir ajustes de parâmetros."
                )
            elif any(palavra in mensagem_lower for palavra in ['qualidade', 'precisão', 'precisao', 'acuracia']):
                return (
                    f"[👁️ Agente de Visão Computacional] Sobre qualidade: "
                    f"Monitoro continuamente a qualidade das detecções. Confidence threshold atual: "
                    f"{CONFIDENCE_THRESHOLD}. Para melhorar precisão, considere fine-tuning do modelo "
                    f"ou ajuste de threshold baseado em validação com dados reais."
                )
            else:
                return (
                    f"[👁️ Agente de Visão Computacional] Recebi sua pergunta sobre '{mensagem[:100]}'. "
                    f"Como especialista em YOLO e visão computacional, posso ajudar com: "
                    f"otimização de modelo, ajuste de parâmetros, análise de performance e "
                    f"sugestões de melhorias. Modelo atual: {MODEL_PATH}."
                )
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar mensagem: {e}")
            return f"[👁️ Agente de Visão Computacional] Não consegui responder devido a um erro. Tente reformular a pergunta."
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do agente."""
        ultima_analise = self.historico_performance[-1] if self.historico_performance else {}
        
        return {
            'nome': self.nome,
            'status': self.estado['status'],
            'modelo_atual': MODEL_PATH,
            'configuracao': {
                'confidence_threshold': CONFIDENCE_THRESHOLD,
                'resolucao': f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
                'fps': FPS
            },
            'total_analises': len(self.historico_performance),
            'ultima_analise': ultima_analise.get('timestamp'),
            'ultima_atualizacao': self.estado['ultima_atualizacao']
        }
    
    def salvar_estado(self) -> None:
        """Salva estado incluindo histórico."""
        self.estado['historico_performance'] = self.historico_performance
        super().salvar_estado()

