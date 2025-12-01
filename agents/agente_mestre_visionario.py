"""
Agente Mestre Visionário - IASenior
Especializado em estratégia, negócios, crescimento e tomada de decisão.
Atua como mentor de alto nível, fornecendo visão estratégica e clareza operacional.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from .agente_base import AgenteBase


class AgenteMestreVisionario(AgenteBase):
    """
    Agente especializado em estratégia e negócios.
    Focado em:
    - Visão estratégica e tomada de decisão
    - Crescimento e escalabilidade
    - Clareza operacional
    - Frameworks de análise
    - Planejamento e execução
    
    Estilo: Direto, objetivo, estratégico. Usa humor quando apropriado.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("mestre_visionario", config)
        self.decisoes_analisadas = []
        self.estrategias_propostas = []
        self.frameworks_aplicados = []
        self.historico_consultas = []
        
        # Frameworks estratégicos disponíveis
        self.frameworks = {
            'swot': {
                'nome': 'SWOT Analysis',
                'descricao': 'Forças, Fraquezas, Oportunidades, Ameaças',
                'uso': 'Análise estratégica de posicionamento'
            },
            'okr': {
                'nome': 'OKR (Objectives and Key Results)',
                'descricao': 'Objetivos claros com resultados mensuráveis',
                'uso': 'Definição de metas e acompanhamento'
            },
            'priorizacao': {
                'nome': 'Matriz de Priorização',
                'descricao': 'Impacto vs Esforço',
                'uso': 'Decidir o que fazer primeiro'
            },
            'canvas': {
                'nome': 'Business Model Canvas',
                'descricao': 'Modelo de negócio estruturado',
                'uso': 'Estruturar modelo de negócio'
            },
            'pestel': {
                'nome': 'PESTEL Analysis',
                'descricao': 'Político, Econômico, Social, Tecnológico, Ambiental, Legal',
                'uso': 'Análise de ambiente externo'
            }
        }
        
    def inicializar(self) -> bool:
        """Inicializa o agente Mestre Visionário."""
        self.logger.info("🎯 Inicializando Mestre Visionário...")
        self.logger.info("💡 Foco: Estratégia, Negócios, Crescimento, Tomada de Decisão")
        
        # Carregar histórico
        estado_salvo = self.carregar_estado()
        if estado_salvo:
            self.historico_consultas = estado_salvo.get('historico_consultas', [])
            self.estrategias_propostas = estado_salvo.get('estrategias_propostas', [])
        
        return True
    
    def processar(self) -> Dict[str, Any]:
        """
        Processa análises estratégicas e mantém visão do sistema.
        
        Returns:
            Dicionário com resultados do processamento
        """
        # Analisar estado atual do sistema
        analise_sistema = self._analisar_estado_sistema()
        
        # Identificar oportunidades estratégicas
        oportunidades = self._identificar_oportunidades(analise_sistema)
        
        # Gerar insights estratégicos
        insights = self._gerar_insights_estrategicos(analise_sistema, oportunidades)
        
        # Salvar análise
        self._salvar_analise(analise_sistema, oportunidades, insights)
        
        return {
            'analises_realizadas': len(self.historico_consultas),
            'oportunidades_identificadas': len(oportunidades),
            'insights_gerados': len(insights),
            'ultima_analise': datetime.now().isoformat()
        }
    
    def _analisar_estado_sistema(self) -> Dict[str, Any]:
        """Analisa o estado atual do sistema do ponto de vista estratégico."""
        # Em um sistema real, isso analisaria métricas, performance, etc.
        # Por enquanto, retorna estrutura básica
        return {
            'timestamp': datetime.now().isoformat(),
            'fase': 'operacional',  # startup, crescimento, maturidade, declínio
            'indicadores': {
                'estabilidade': 'alta',
                'crescimento': 'moderado',
                'inovacao': 'ativa'
            }
        }
    
    def _identificar_oportunidades(self, analise: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica oportunidades estratégicas baseadas na análise."""
        oportunidades = []
        
        # Oportunidades genéricas baseadas em padrões comuns
        if analise.get('fase') == 'operacional':
            oportunidades.append({
                'tipo': 'otimizacao',
                'descricao': 'Otimizar processos operacionais para liberar recursos para crescimento',
                'impacto': 'alto',
                'esforco': 'medio',
                'prioridade': 'alta'
            })
        
        return oportunidades
    
    def _gerar_insights_estrategicos(self, analise: Dict, oportunidades: List[Dict]) -> List[str]:
        """Gera insights estratégicos baseados em análise e oportunidades."""
        insights = []
        
        if oportunidades:
            insights.append(
                "💡 Foco em crescimento: Escalar não começa com contratar pessoas; "
                "começa com multiplicar valor por cliente e reduzir dependência operacional."
            )
        
        insights.append(
            "🎯 Estratégia adora simplicidade e odeia distração. "
            "Escolha dois caminhos: aumentar ticket, aumentar volume, ou aumentar velocidade."
        )
        
        return insights
    
    def _salvar_analise(self, analise: Dict, oportunidades: List[Dict], insights: List[str]) -> None:
        """Salva análise estratégica."""
        arquivo_analise = self.diretorio_dados / "analises" / f"analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        arquivo_analise.parent.mkdir(exist_ok=True)
        
        analise_completa = {
            'timestamp': datetime.now().isoformat(),
            'analise': analise,
            'oportunidades': oportunidades,
            'insights': insights
        }
        
        with open(arquivo_analise, 'w') as f:
            json.dump(analise_completa, f, indent=2, ensure_ascii=False)
        
        self.historico_consultas.append(analise_completa)
        
        # Manter apenas últimas 100 análises
        if len(self.historico_consultas) > 100:
            self.historico_consultas.pop(0)
    
    def consultar_estrategia(self, pergunta: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Consulta estratégica direta. Responde perguntas de forma clara e objetiva.
        
        Args:
            pergunta: Pergunta ou situação a ser analisada
            contexto: Contexto adicional (opcional)
        
        Returns:
            Resposta estratégica estruturada
        """
        self.logger.info(f"💭 Consulta estratégica: {pergunta[:50]}...")
        
        # Analisar pergunta e gerar resposta
        resposta = self._gerar_resposta_estrategica(pergunta, contexto or {})
        
        # Salvar consulta
        consulta = {
            'timestamp': datetime.now().isoformat(),
            'pergunta': pergunta,
            'contexto': contexto,
            'resposta': resposta
        }
        self.historico_consultas.append(consulta)
        
        return resposta
    
    def _gerar_resposta_estrategica(self, pergunta: str, contexto: Dict) -> Dict[str, Any]:
        """
        Gera resposta estratégica baseada na pergunta.
        Estilo: direto, objetivo, estratégico. Usa humor quando apropriado.
        """
        pergunta_lower = pergunta.lower()
        
        # Padrões de resposta baseados em palavras-chave
        resposta = {
            'resposta_direta': '',
            'framework_sugerido': None,
            'acoes_recomendadas': [],
            'insights': []
        }
        
        # Escalar negócio
        if any(palavra in pergunta_lower for palavra in ['escalar', 'crescer', 'multiplicar', 'faturamento']):
            resposta['resposta_direta'] = (
                "Escalar serviço não começa com contratar pessoas; começa com multiplicar "
                "valor por cliente e reduzir dependência da sua hora. Primeiro, productize "
                "o serviço. Depois, desenhe ofertas escaláveis (mentoria em grupo, cursos, "
                "produtos digitais, playbooks). Só então contrate para substituir operações. "
                "Crescimento primeiro vem da mente, depois da equipe."
            )
            resposta['framework_sugerido'] = 'canvas'
            resposta['acoes_recomendadas'] = [
                'Productizar o serviço atual',
                'Criar ofertas escaláveis (não dependentes de sua hora)',
                'Depois contratar para substituir operações'
            ]
        
        # Dobrar operação
        elif any(palavra in pergunta_lower for palavra in ['dobrar', 'aumentar', 'trimestre', 'crescimento']):
            resposta['resposta_direta'] = (
                "Três caminhos: (1) aumentar ticket, (2) aumentar volume, (3) aumentar "
                "velocidade. Escolha dois. E prometa a si mesmo que não vai inventar um "
                "quarto. Estratégia adora simplicidade e odeia distração."
            )
            resposta['framework_sugerido'] = 'priorizacao'
            resposta['acoes_recomendadas'] = [
                'Definir qual dos três caminhos priorizar',
                'Escolher no máximo dois caminhos',
                'Focar execução sem distrações'
            ]
        
        # Tomada de decisão
        elif any(palavra in pergunta_lower for palavra in ['decidir', 'escolher', 'priorizar', 'decisão']):
            resposta['resposta_direta'] = (
                "Decisão sem clareza é aposta. Primeiro, defina o que você quer alcançar. "
                "Depois, liste opções. Por fim, avalie impacto vs esforço. "
                "A melhor decisão é a que você consegue executar."
            )
            resposta['framework_sugerido'] = 'priorizacao'
            resposta['acoes_recomendadas'] = [
                'Definir objetivo claro',
                'Listar todas as opções',
                'Avaliar impacto vs esforço',
                'Escolher e executar'
            ]
        
        # Análise estratégica geral
        else:
            resposta['resposta_direta'] = (
                "Estratégia é sobre fazer escolhas. Escolha o que fazer e, mais importante, "
                "o que não fazer. Clareza primeiro, depois execução. "
                "Se não está claro, pare e esclareça antes de seguir."
            )
            resposta['framework_sugerido'] = 'swot'
            resposta['acoes_recomendadas'] = [
                'Definir objetivo claro',
                'Analisar situação atual',
                'Identificar caminhos possíveis',
                'Escolher e executar'
            ]
        
        resposta['insights'] = [
            "Priorização: clareza → estratégia → ação",
            "Estratégia adora simplicidade",
            "Melhor decisão é a executável"
        ]
        
        return resposta
    
    def criar_plano_acao(self, objetivo: str, contexto: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Cria plano de ação estruturado para um objetivo.
        
        Args:
            objetivo: Objetivo a ser alcançado
            contexto: Contexto adicional
        
        Returns:
            Plano de ação estruturado
        """
        self.logger.info(f"📋 Criando plano de ação para: {objetivo[:50]}...")
        
        plano = {
            'objetivo': objetivo,
            'timestamp': datetime.now().isoformat(),
            'fases': [],
            'metricas': [],
            'prazos': []
        }
        
        # Estruturar plano básico
        plano['fases'] = [
            {
                'fase': 1,
                'nome': 'Clareza',
                'descricao': 'Definir objetivo claro e mensurável',
                'entregas': ['Objetivo definido', 'Métricas estabelecidas']
            },
            {
                'fase': 2,
                'nome': 'Estratégia',
                'descricao': 'Definir caminho e prioridades',
                'entregas': ['Caminho escolhido', 'Prioridades definidas']
            },
            {
                'fase': 3,
                'nome': 'Execução',
                'descricao': 'Executar com foco',
                'entregas': ['Ações executadas', 'Resultados medidos']
            }
        ]
        
        plano['metricas'] = [
            'Progresso em %',
            'Tempo decorrido',
            'Resultados alcançados'
        ]
        
        self.estrategias_propostas.append(plano)
        
        return plano
    
    def aplicar_framework(self, framework: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica um framework estratégico aos dados fornecidos.
        
        Args:
            framework: Nome do framework (swot, okr, priorizacao, etc.)
            dados: Dados para análise
        
        Returns:
            Análise estruturada usando o framework
        """
        if framework not in self.frameworks:
            return {
                'erro': f'Framework {framework} não disponível',
                'frameworks_disponiveis': list(self.frameworks.keys())
            }
        
        info_framework = self.frameworks[framework]
        
        # Estrutura básica do framework
        analise = {
            'framework': info_framework['nome'],
            'descricao': info_framework['descricao'],
            'timestamp': datetime.now().isoformat(),
            'dados_analisados': dados,
            'resultado': {}
        }
        
        # Estruturas específicas por framework
        if framework == 'swot':
            analise['resultado'] = {
                'forcas': dados.get('forcas', []),
                'fraquezas': dados.get('fraquezas', []),
                'oportunidades': dados.get('oportunidades', []),
                'ameacas': dados.get('ameacas', [])
            }
        elif framework == 'okr':
            analise['resultado'] = {
                'objetivo': dados.get('objetivo', ''),
                'key_results': dados.get('key_results', [])
            }
        elif framework == 'priorizacao':
            analise['resultado'] = {
                'alto_impacto_baixo_esforco': dados.get('quick_wins', []),
                'alto_impacto_alto_esforco': dados.get('projetos_estrategicos', []),
                'baixo_impacto_baixo_esforco': dados.get('preencher_tempo', []),
                'baixo_impacto_alto_esforco': dados.get('evitar', [])
            }
        
        self.frameworks_aplicados.append(analise)
        
        return analise
    
    def processar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem enviada pelo orquestrador.
        Deve retornar uma resposta textual.
        A resposta deve refletir a especialidade do agente.
        
        Args:
            mensagem: Mensagem ou pergunta a ser processada
        
        Returns:
            Resposta estratégica do agente
        """
        try:
            if not mensagem or not isinstance(mensagem, str):
                return "[🎯 Mestre Visionário] Mensagem inválida recebida."
            
            # Usar método consultar_estrategia existente (pode ser lento, mas é necessário)
            try:
                resposta_dict = self.consultar_estrategia(mensagem)
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao consultar estratégia: {e}")
                # Fallback para resposta genérica
                return (
                    f"[🎯 Mestre Visionário] Recebi sua pergunta sobre '{mensagem[:100]}'. "
                    f"Como mentor estratégico, foco em clareza, estratégia e ação. "
                    f"Estratégia adora simplicidade e odeia distração. "
                    f"Priorização: clareza → estratégia → ação."
                )
            
            # Converter resposta dict em string formatada
            resposta = resposta_dict.get('resposta_direta', '')
            
            if resposta_dict.get('acoes_recomendadas'):
                resposta += "\n\nAções recomendadas:"
                for i, acao in enumerate(resposta_dict['acoes_recomendadas'], 1):
                    resposta += f"\n{i}. {acao}"
            
            if resposta_dict.get('insights'):
                resposta += "\n\nInsights:"
                for insight in resposta_dict['insights']:
                    resposta += f"\n• {insight}"
            
            return f"[🎯 Mestre Visionário] {resposta}"
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar mensagem: {e}")
            return f"[🎯 Mestre Visionário] Não consegui responder devido a um erro. Tente reformular a pergunta."
    
    def obter_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do agente."""
        return {
            'nome': self.nome,
            'status': self.estado['status'],
            'consultas_realizadas': len(self.historico_consultas),
            'estrategias_propostas': len(self.estrategias_propostas),
            'frameworks_aplicados': len(self.frameworks_aplicados),
            'frameworks_disponiveis': list(self.frameworks.keys()),
            'ultima_atualizacao': self.estado['ultima_atualizacao']
        }
    
    def salvar_estado(self) -> None:
        """Salva estado incluindo histórico."""
        self.estado['historico_consultas'] = self.historico_consultas
        self.estado['estrategias_propostas'] = self.estrategias_propostas
        self.estado['frameworks_aplicados'] = self.frameworks_aplicados
        super().salvar_estado()

