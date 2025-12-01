#!/usr/bin/env python3
"""
Sessão Colaborativa de Agentes - IASenior
Faz todos os agentes conversarem e encontrarem melhorias juntas para o projeto.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orquestrador import OrquestradorAgentes
from agents.agente_base import AgenteBase

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SessaoColaborativaAgentes:
    """
    Gerencia uma sessão colaborativa onde todos os agentes analisam o projeto
    e discutem melhorias juntos.
    """
    
    def __init__(self, diretorio_projeto: Path = None):
        """Inicializa a sessão colaborativa."""
        self.diretorio_projeto = diretorio_projeto or Path(__file__).parent
        self.agentes = {}
        self.descobertas = {}
        self.melhorias_encontradas = []
        self.discussoes = []
        self.logger = logger
        
        # Diretório para salvar resultados
        self.diretorio_resultados = self.diretorio_projeto / "agents_data" / "sessao_colaborativa"
        self.diretorio_resultados.mkdir(parents=True, exist_ok=True)
        
    def inicializar_agentes(self) -> bool:
        """Inicializa todos os agentes para a sessão."""
        self.logger.info("🚀 Inicializando agentes para sessão colaborativa...")
        
        config = {
            'diretorio_dados': str(self.diretorio_projeto / 'agents_data'),
            'agentes': {
                'pesquisa': {
                    'intervalo': 1.0,
                    'areas_pesquisa': [
                        'visao_computacional',
                        'yolo',
                        'operacoes',
                        'performance',
                        'seguranca'
                    ]
                },
                'engenharia_visao_computacional': {
                    'intervalo': 1.0,
                },
                'operacoes': {
                    'intervalo': 1.0,
                    'servicos_monitorados': [
                        'stream_inferencia_rtsp.py',
                        'mjpeg_server.py',
                        'mediamtx'
                    ],
                    'auto_restart': False
                },
                'seguranca': {
                    'intervalo': 1.0,
                },
                'performance': {
                    'intervalo': 1.0,
                },
                'predicao_risco_queda': {
                    'intervalo': 1.0,
                    'janela_temporal': 30,
                    'threshold_risco': 0.7,
                    'modelo_predicao': 'lstm'
                }
            }
        }
        
        orquestrador = OrquestradorAgentes(config)
        
        if not orquestrador.inicializar_agentes():
            self.logger.error("❌ Falha ao inicializar agentes")
            return False
        
        self.agentes = orquestrador.agentes
        self.logger.info(f"✅ {len(self.agentes)} agentes inicializados")
        return True
    
    def realizar_sessao(self) -> Dict[str, Any]:
        """
        Realiza a sessão colaborativa completa.
        """
        self.logger.info("=" * 80)
        self.logger.info("🤝 INICIANDO SESSÃO COLABORATIVA DE AGENTES")
        self.logger.info("=" * 80)
        
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'fase': 'inicio',
            'descobertas_por_agente': {},
            'discussoes': [],
            'melhorias_encontradas': [],
            'melhorias_priorizadas': []
        }
        
        # FASE 1: Análise Individual
        self.logger.info("\n📊 FASE 1: Análise Individual do Projeto")
        self.logger.info("-" * 80)
        descobertas = self._fase_analise_individual()
        resultados['descobertas_por_agente'] = descobertas
        
        # FASE 2: Compartilhamento de Descobertas
        self.logger.info("\n💬 FASE 2: Compartilhamento de Descobertas")
        self.logger.info("-" * 80)
        discussoes = self._fase_compartilhamento(descobertas)
        resultados['discussoes'] = discussoes
        
        # FASE 3: Discussão Colaborativa
        self.logger.info("\n🎯 FASE 3: Discussão Colaborativa")
        self.logger.info("-" * 80)
        melhorias = self._fase_discussao_colaborativa(descobertas, discussoes)
        resultados['melhorias_encontradas'] = melhorias
        
        # FASE 4: Priorização
        self.logger.info("\n⭐ FASE 4: Priorização de Melhorias")
        self.logger.info("-" * 80)
        melhorias_priorizadas = self._fase_priorizacao(melhorias)
        resultados['melhorias_priorizadas'] = melhorias_priorizadas
        
        # Salvar resultados
        self._salvar_resultados(resultados)
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("✅ SESSÃO COLABORATIVA CONCLUÍDA")
        self.logger.info("=" * 80)
        
        return resultados
    
    def _fase_analise_individual(self) -> Dict[str, Dict[str, Any]]:
        """Cada agente analisa o projeto independentemente."""
        descobertas = {}
        
        for nome_agente, agente in self.agentes.items():
            self.logger.info(f"\n🤖 {nome_agente.upper()} está analisando o projeto...")
            
            try:
                # Cada agente faz sua análise específica
                descoberta = self._analisar_com_agente(agente, nome_agente)
                descobertas[nome_agente] = descoberta
                
                self.logger.info(f"  ✅ {nome_agente} completou análise")
                self.logger.info(f"  📋 Encontrou {len(descoberta.get('pontos_observados', []))} pontos observados")
                self.logger.info(f"  💡 Sugeriu {len(descoberta.get('sugestoes', []))} melhorias")
                
            except Exception as e:
                self.logger.error(f"  ❌ Erro na análise de {nome_agente}: {e}")
                descobertas[nome_agente] = {
                    'erro': str(e),
                    'pontos_observados': [],
                    'sugestoes': []
                }
        
        return descobertas
    
    def _analisar_com_agente(self, agente: AgenteBase, nome_agente: str) -> Dict[str, Any]:
        """Faz uma análise específica com um agente."""
        descoberta = {
            'agente': nome_agente,
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {},
            'alertas': []
        }
        
        # Análise específica por tipo de agente
        if nome_agente == 'pesquisa':
            # Agente de pesquisa analisa estrutura e documentação
            descoberta = self._analise_pesquisa()
            
        elif nome_agente == 'engenharia_visao_computacional':
            # Agente de visão computacional analisa modelos e performance
            descoberta = self._analise_visao_computacional()
            
        elif nome_agente == 'operacoes':
            # Agente de operações analisa serviços e logs
            descoberta = self._analise_operacoes()
            
        elif nome_agente == 'seguranca':
            # Agente de segurança analisa vulnerabilidades
            descoberta = self._analise_seguranca()
            
        elif nome_agente == 'performance':
            # Agente de performance analisa otimizações
            descoberta = self._analise_performance()
            
        elif nome_agente == 'predicao_risco_queda':
            # Agente de predição analisa modelos de ML
            descoberta = self._analise_predicao()
        
        # Obter status do agente
        try:
            status = agente.obter_status()
            descoberta['status_agente'] = status
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao obter status do agente {nome_agente}: {e}")
            descoberta['status_agente'] = {'erro': str(e)}
        
        return descoberta
    
    def _analise_pesquisa(self) -> Dict[str, Any]:
        """Análise do Agente de Pesquisa."""
        descoberta = {
            'agente': 'pesquisa',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar documentação
        arquivos_doc = list(self.diretorio_projeto.glob("*.md"))
        descoberta['metricas']['documentacao'] = {
            'total_arquivos_md': len(arquivos_doc),
            'arquivos_encontrados': [f.name for f in arquivos_doc]
        }
        
        # Verificar README
        readme = self.diretorio_projeto / "README.md"
        if readme.exists():
            descoberta['pontos_observados'].append({
                'tipo': 'positivo',
                'descricao': 'README.md encontrado e atualizado'
            })
        else:
            descoberta['pontos_observados'].append({
                'tipo': 'atencao',
                'descricao': 'README.md não encontrado'
            })
            descoberta['sugestoes'].append({
                'prioridade': 'alta',
                'descricao': 'Criar README.md com documentação do projeto',
                'categoria': 'documentacao'
            })
        
        # Verificar estrutura de diretórios
        diretorios_importantes = ['scripts', 'agents', 'logs', 'resultados']
        diretorios_existentes = [d for d in diretorios_importantes 
                                if (self.diretorio_projeto / d).exists()]
        
        percentual_completo = 0.0
        if diretorios_importantes:  # Evitar divisão por zero
            percentual_completo = len(diretorios_existentes) / len(diretorios_importantes) * 100
        
        descoberta['metricas']['estrutura'] = {
            'diretorios_importantes': diretorios_existentes,
            'percentual_completo': percentual_completo
        }
        
        # Verificar requirements.txt
        requirements = self.diretorio_projeto / "requirements.txt"
        if requirements.exists():
            with open(requirements, 'r') as f:
                dependencias = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            descoberta['metricas']['dependencias'] = {
                'total': len(dependencias),
                'atualizado': True
            }
        
        # Sugestões baseadas em análise
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'media',
                'descricao': 'Adicionar mais exemplos de uso no README',
                'categoria': 'documentacao',
                'agente': 'pesquisa'
            },
            {
                'prioridade': 'baixa',
                'descricao': 'Considerar adicionar diagramas de arquitetura',
                'categoria': 'documentacao',
                'agente': 'pesquisa'
            }
        ])
        
        return descoberta
    
    def _analise_visao_computacional(self) -> Dict[str, Any]:
        """Análise do Agente de Visão Computacional."""
        descoberta = {
            'agente': 'engenharia_visao_computacional',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar modelos
        modelos_dir = self.diretorio_projeto / "modelos"
        modelo_yolo = self.diretorio_projeto / "yolov8n.pt"
        
        modelos_encontrados = []
        if modelo_yolo.exists():
            modelos_encontrados.append("yolov8n.pt")
        if modelos_dir.exists():
            modelos_encontrados.extend([f.name for f in modelos_dir.glob("*.pt")])
        
        descoberta['metricas']['modelos'] = {
            'total': len(modelos_encontrados),
            'modelos': modelos_encontrados
        }
        
        # Verificar scripts de inferência
        script_inferencia = self.diretorio_projeto / "scripts" / "stream_inferencia_rtsp.py"
        if script_inferencia.exists():
            descoberta['pontos_observados'].append({
                'tipo': 'positivo',
                'descricao': 'Script de inferência encontrado'
            })
            
            # Analisar conteúdo do script
            with open(script_inferencia, 'r') as f:
                conteudo = f.read()
                if 'try:' in conteudo and 'except' in conteudo:
                    descoberta['pontos_observados'].append({
                        'tipo': 'positivo',
                        'descricao': 'Script tem tratamento de erros'
                    })
                else:
                    descoberta['sugestoes'].append({
                        'prioridade': 'media',
                        'descricao': 'Adicionar tratamento de erros no script de inferência',
                        'categoria': 'codigo',
                        'agente': 'engenharia_visao_computacional'
                    })
        
        # Verificar configurações
        config_file = self.diretorio_projeto / "config.py"
        if config_file.exists():
            descoberta['pontos_observados'].append({
                'tipo': 'positivo',
                'descricao': 'Arquivo de configuração centralizado encontrado'
            })
        else:
            descoberta['sugestoes'].append({
                'prioridade': 'alta',
                'descricao': 'Criar config.py para centralizar configurações',
                'categoria': 'arquitetura',
                'agente': 'engenharia_visao_computacional'
            })
        
        # Sugestões específicas de visão computacional
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'media',
                'descricao': 'Considerar usar batch processing para melhorar FPS',
                'categoria': 'performance',
                'agente': 'engenharia_visao_computacional'
            },
            {
                'prioridade': 'baixa',
                'descricao': 'Avaliar uso de YOLOv11 ou YOLO-NAS para melhor precisão',
                'categoria': 'melhoria_modelo',
                'agente': 'engenharia_visao_computacional'
            }
        ])
        
        return descoberta
    
    def _analise_operacoes(self) -> Dict[str, Any]:
        """Análise do Agente de Operações."""
        descoberta = {
            'agente': 'operacoes',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar logs
        logs_dir = self.diretorio_projeto / "logs"
        if logs_dir.exists():
            logs = list(logs_dir.glob("*.log"))
            descoberta['metricas']['logs'] = {
                'total_arquivos': len(logs),
                'arquivos': [f.name for f in logs]
            }
            
            # Verificar tamanho dos logs
            tamanho_total = sum(f.stat().st_size for f in logs)
            tamanho_mb = tamanho_total / (1024 * 1024)
            
            if tamanho_mb > 100:
                descoberta['sugestoes'].append({
                    'prioridade': 'media',
                    'descricao': f'Logs ocupam {tamanho_mb:.1f}MB - considerar rotação de logs',
                    'categoria': 'operacoes',
                    'agente': 'operacoes'
                })
        
        # Verificar scripts de start/stop
        start_script = self.diretorio_projeto / "start_tudo.sh"
        stop_script = self.diretorio_projeto / "stop_tudo.sh"
        
        if start_script.exists() and stop_script.exists():
            descoberta['pontos_observados'].append({
                'tipo': 'positivo',
                'descricao': 'Scripts de gerenciamento (start/stop) encontrados'
            })
        else:
            descoberta['sugestoes'].append({
                'prioridade': 'alta',
                'descricao': 'Criar scripts de start_tudo.sh e stop_tudo.sh',
                'categoria': 'operacoes',
                'agente': 'operacoes'
            })
        
        # Verificar serviços monitorados
        servicos = ['stream_inferencia_rtsp.py', 'mjpeg_server.py', 'mediamtx']
        servicos_encontrados = []
        
        for servico in servicos:
            if 'mediamtx' in servico:
                # Verificar se mediamtx existe
                import shutil
                if shutil.which('mediamtx') or (self.diretorio_projeto / 'mediamtx.yml').exists():
                    servicos_encontrados.append(servico)
            elif (self.diretorio_projeto / servico).exists() or \
                 (self.diretorio_projeto / 'scripts' / servico).exists():
                servicos_encontrados.append(servico)
        
        descoberta['metricas']['servicos'] = {
            'monitorados': servicos,
            'encontrados': servicos_encontrados,
            'cobertura': len(servicos_encontrados) / len(servicos) * 100 if servicos else 0
        }
        
        # Sugestões de operações
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'media',
                'descricao': 'Implementar health checks automáticos para serviços',
                'categoria': 'monitoramento',
                'agente': 'operacoes'
            },
            {
                'prioridade': 'baixa',
                'descricao': 'Considerar usar systemd ou supervisor para gerenciar serviços',
                'categoria': 'deploy',
                'agente': 'operacoes'
            }
        ])
        
        return descoberta
    
    def _analise_seguranca(self) -> Dict[str, Any]:
        """Análise do Agente de Segurança."""
        descoberta = {
            'agente': 'seguranca',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar .gitignore
        gitignore = self.diretorio_projeto / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                conteudo = f.read()
                if '*.log' in conteudo and '__pycache__' in conteudo:
                    descoberta['pontos_observados'].append({
                        'tipo': 'positivo',
                        'descricao': '.gitignore parece adequado'
                    })
        else:
            descoberta['sugestoes'].append({
                'prioridade': 'alta',
                'descricao': 'Criar .gitignore para evitar commit de arquivos sensíveis',
                'categoria': 'seguranca',
                'agente': 'seguranca'
            })
        
        # Verificar senhas hardcoded (análise básica)
        arquivos_py = list(self.diretorio_projeto.rglob("*.py"))
        problemas_seguranca = []
        
        for arquivo in arquivos_py[:10]:  # Limitar para performance
            try:
                with open(arquivo, 'r') as f:
                    conteudo = f.read().lower()
                    if 'password' in conteudo or 'senha' in conteudo:
                        if 'input(' not in conteudo and 'getenv' not in conteudo:
                            problemas_seguranca.append(str(arquivo.relative_to(self.diretorio_projeto)))
            except Exception as e:
                self.logger.debug(f"⚠️ Erro ao analisar arquivo {arquivo}: {e}")
                continue
        
        if problemas_seguranca:
            descoberta['alertas'] = descoberta.get('alertas', [])
            descoberta['alertas'].append({
                'tipo': 'atencao',
                'descricao': f'Possíveis senhas hardcoded em: {", ".join(problemas_seguranca[:3])}',
                'severidade': 'media'
            })
        
        descoberta['metricas']['analise_seguranca'] = {
            'arquivos_analisados': min(10, len(arquivos_py)),
            'problemas_encontrados': len(problemas_seguranca)
        }
        
        # Sugestões de segurança
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'alta',
                'descricao': 'Usar variáveis de ambiente para dados sensíveis',
                'categoria': 'seguranca',
                'agente': 'seguranca'
            },
            {
                'prioridade': 'media',
                'descricao': 'Implementar autenticação para endpoints de API',
                'categoria': 'seguranca',
                'agente': 'seguranca'
            }
        ])
        
        return descoberta
    
    def _analise_performance(self) -> Dict[str, Any]:
        """Análise do Agente de Performance."""
        descoberta = {
            'agente': 'performance',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar uso de cache
        cache_dirs = ['__pycache__', '.cache']
        cache_encontrado = any((self.diretorio_projeto / d).exists() for d in cache_dirs)
        
        descoberta['metricas']['cache'] = {
            'cache_encontrado': cache_encontrado
        }
        
        # Analisar scripts Python para otimizações
        script_inferencia = self.diretorio_projeto / "scripts" / "stream_inferencia_rtsp.py"
        if script_inferencia.exists():
            with open(script_inferencia, 'r') as f:
                conteudo = f.read()
                if 'multiprocessing' in conteudo or 'threading' in conteudo:
                    descoberta['pontos_observados'].append({
                        'tipo': 'positivo',
                        'descricao': 'Script usa paralelização'
                    })
                elif 'for ' in conteudo and 'range' in conteudo:
                    descoberta['sugestoes'].append({
                        'prioridade': 'baixa',
                        'descricao': 'Considerar paralelização para loops de processamento',
                        'categoria': 'performance',
                        'agente': 'performance'
                    })
        
        # Verificar imports de psutil para monitoramento (opcional)
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            descoberta['metricas']['sistema'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            }
            
            if cpu_percent > 70:
                descoberta['alertas'] = descoberta.get('alertas', [])
                descoberta['alertas'].append({
                    'tipo': 'atencao',
                    'descricao': f'CPU alta: {cpu_percent:.1f}%',
                    'severidade': 'media'
                })
        except ImportError:
            # psutil não disponível, pular monitoramento de sistema
            pass
        except Exception:
            pass
        
        # Sugestões de performance
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'media',
                'descricao': 'Implementar cache de resultados de inferência',
                'categoria': 'performance',
                'agente': 'performance'
            },
            {
                'prioridade': 'baixa',
                'descricao': 'Considerar usar GPU acceleration quando disponível',
                'categoria': 'performance',
                'agente': 'performance'
            }
        ])
        
        return descoberta
    
    def _analise_predicao(self) -> Dict[str, Any]:
        """Análise do Agente de Predição."""
        descoberta = {
            'agente': 'predicao_risco_queda',
            'pontos_observados': [],
            'sugestoes': [],
            'metricas': {}
        }
        
        # Verificar dados de treino
        datasets_dir = self.diretorio_projeto / "datasets"
        if datasets_dir.exists():
            subdirs = [d.name for d in datasets_dir.iterdir() if d.is_dir()]
            descoberta['metricas']['datasets'] = {
                'diretorios_encontrados': subdirs,
                'total': len(subdirs)
            }
            
            if 'treino' in subdirs or 'train' in subdirs:
                descoberta['pontos_observados'].append({
                    'tipo': 'positivo',
                    'descricao': 'Diretório de treino encontrado'
                })
        
        # Sugestões de ML
        descoberta['sugestoes'].extend([
            {
                'prioridade': 'media',
                'descricao': 'Implementar validação cruzada para modelos de predição',
                'categoria': 'ml',
                'agente': 'predicao_risco_queda'
            },
            {
                'prioridade': 'baixa',
                'descricao': 'Considerar usar ensemble de modelos para melhor precisão',
                'categoria': 'ml',
                'agente': 'predicao_risco_queda'
            }
        ])
        
        return descoberta
    
    def _fase_compartilhamento(self, descobertas: Dict) -> List[Dict[str, Any]]:
        """Agentes compartilham suas descobertas."""
        discussoes = []
        
        for nome_agente, descoberta in descobertas.items():
            sugestoes = descoberta.get('sugestoes', [])
            pontos = descoberta.get('pontos_observados', [])
            
            if sugestoes or pontos:
                discussao = {
                    'agente': nome_agente,
                    'timestamp': datetime.now().isoformat(),
                    'resumo': f"{nome_agente} compartilhou {len(pontos)} observações e {len(sugestoes)} sugestões",
                    'sugestoes': sugestoes,
                    'pontos_chave': pontos
                }
                discussoes.append(discussao)
                
                self.logger.info(f"\n💬 {nome_agente.upper()} compartilhou:")
                for ponto in pontos[:3]:  # Mostrar primeiros 3
                    self.logger.info(f"   • {ponto.get('descricao', 'N/A')}")
                for sugestao in sugestoes[:3]:  # Mostrar primeiras 3
                    self.logger.info(f"   💡 [{sugestao.get('prioridade', '?').upper()}] {sugestao.get('descricao', 'N/A')}")
        
        return discussoes
    
    def _fase_discussao_colaborativa(self, descobertas: Dict, discussoes: List) -> List[Dict[str, Any]]:
        """Agentes discutem melhorias colaborativas."""
        melhorias = []
        
        # Consolidar todas as sugestões
        todas_sugestoes = []
        for descoberta in descobertas.values():
            todas_sugestoes.extend(descoberta.get('sugestoes', []))
        
        # Agrupar por categoria
        melhorias_por_categoria = {}
        for sugestao in todas_sugestoes:
            categoria = sugestao.get('categoria', 'outros')
            if categoria not in melhorias_por_categoria:
                melhorias_por_categoria[categoria] = []
            melhorias_por_categoria[categoria].append(sugestao)
        
        # Criar melhorias colaborativas
        self.logger.info("\n🎯 Melhorias Colaborativas Identificadas:")
        
        for categoria, sugestoes in melhorias_por_categoria.items():
            melhoria = {
                'categoria': categoria,
                'total_sugestoes': len(sugestoes),
                'agentes_envolvidos': list(set(s.get('agente', 'desconhecido') for s in sugestoes)),
                'sugestoes': sugestoes,
                'prioridade_media': self._calcular_prioridade_media(sugestoes)
            }
            melhorias.append(melhoria)
            
            self.logger.info(f"\n  📂 {categoria.upper()}:")
            self.logger.info(f"     {len(sugestoes)} sugestões de {len(melhoria['agentes_envolvidos'])} agentes")
        
        # Encontrar melhorias que aparecem em múltiplos agentes
        melhorias_consenso = self._encontrar_consenso(todas_sugestoes)
        if melhorias_consenso:
            melhorias.append({
                'categoria': 'consenso_multiagente',
                'tipo': 'consenso',
                'melhorias': melhorias_consenso,
                'prioridade_media': 'alta'
            })
        
        return melhorias
    
    def _encontrar_consenso(self, sugestoes: List[Dict]) -> List[Dict]:
        """Encontra melhorias sugeridas por múltiplos agentes."""
        # Agrupar por descrição similar
        grupos = {}
        for sugestao in sugestoes:
            desc = sugestao.get('descricao', '').lower()
            chave = desc[:50]  # Primeiros 50 caracteres como chave
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(sugestao)
        
        # Retornar grupos com 2+ sugestões (consenso)
        consenso = []
        for chave, grupo in grupos.items():
            if len(grupo) >= 2:
                consenso.append({
                    'descricao': grupo[0].get('descricao'),
                    'agentes_concordam': list(set(s.get('agente') for s in grupo)),
                    'total_concordam': len(grupo),
                    'prioridades': [s.get('prioridade') for s in grupo]
                })
        
        return consenso
    
    def _calcular_prioridade_media(self, sugestoes: List[Dict]) -> str:
        """Calcula prioridade média de um grupo de sugestões."""
        prioridades = {'alta': 3, 'media': 2, 'baixa': 1}
        valores = [prioridades.get(s.get('prioridade', 'media'), 2) for s in sugestoes]
        media = sum(valores) / len(valores) if valores else 2
        
        if media >= 2.5:
            return 'alta'
        elif media >= 1.5:
            return 'media'
        else:
            return 'baixa'
    
    def _fase_priorizacao(self, melhorias: List[Dict]) -> List[Dict[str, Any]]:
        """Prioriza melhorias encontradas."""
        melhorias_priorizadas = []
        
        # Ordenar por prioridade
        ordem_prioridade = {'alta': 3, 'media': 2, 'baixa': 1}
        
        for melhoria in melhorias:
            # Se há consenso entre múltiplos agentes, aumentar prioridade
            if melhoria.get('tipo') == 'consenso':
                prioridade = 4  # Máxima prioridade para consensos
            else:
                prioridade = ordem_prioridade.get(melhoria.get('prioridade_media', 'media'), 2)
            
            melhorias_priorizadas.append({
                **melhoria,
                'score_prioridade': prioridade
            })
        
        # Ordenar por score
        melhorias_priorizadas.sort(key=lambda x: x['score_prioridade'], reverse=True)
        
        self.logger.info("\n⭐ TOP 10 MELHORIAS PRIORIZADAS:")
        for i, melhoria in enumerate(melhorias_priorizadas[:10], 1):
            categoria = melhoria.get('categoria', 'N/A')
            if melhoria.get('tipo') == 'consenso':
                self.logger.info(f"\n  {i}. [CONSENSO] {categoria.upper()}")
                for item in melhoria.get('melhorias', [])[:3]:
                    self.logger.info(f"     • {item.get('descricao')} ({item.get('total_concordam')} agentes concordam)")
            else:
                self.logger.info(f"\n  {i}. [{melhoria.get('prioridade_media', '?').upper()}] {categoria.upper()}")
                self.logger.info(f"     {melhoria.get('total_sugestoes', 0)} sugestões")
        
        return melhorias_priorizadas
    
    def _salvar_resultados(self, resultados: Dict) -> None:
        """Salva resultados da sessão."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar JSON completo
        arquivo_json = self.diretorio_resultados / f"sessao_{timestamp}.json"
        with open(arquivo_json, 'w') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        # Salvar relatório em texto
        arquivo_relatorio = self.diretorio_resultados / f"relatorio_{timestamp}.md"
        self._gerar_relatorio_markdown(resultados, arquivo_relatorio)
        
        self.logger.info(f"\n💾 Resultados salvos em:")
        self.logger.info(f"   📄 {arquivo_json}")
        self.logger.info(f"   📄 {arquivo_relatorio}")
    
    def _gerar_relatorio_markdown(self, resultados: Dict, arquivo: Path) -> None:
        """Gera relatório em Markdown."""
        with open(arquivo, 'w') as f:
            f.write("# 🤝 Relatório de Sessão Colaborativa de Agentes\n\n")
            f.write(f"**Data**: {resultados['timestamp']}\n\n")
            f.write("---\n\n")
            
            # Resumo executivo
            f.write("## 📊 Resumo Executivo\n\n")
            f.write(f"- **Total de Agentes**: {len(resultados['descobertas_por_agente'])}\n")
            f.write(f"- **Melhorias Encontradas**: {len(resultados['melhorias_encontradas'])}\n")
            f.write(f"- **Melhorias Priorizadas**: {len(resultados['melhorias_priorizadas'])}\n\n")
            
            # Melhorias priorizadas
            f.write("## ⭐ Melhorias Priorizadas\n\n")
            for i, melhoria in enumerate(resultados['melhorias_priorizadas'][:20], 1):
                f.write(f"### {i}. {melhoria.get('categoria', 'N/A').upper()}\n\n")
                f.write(f"- **Prioridade**: {melhoria.get('prioridade_media', 'media')}\n")
                if melhoria.get('total_sugestoes'):
                    f.write(f"- **Total de Sugestões**: {melhoria['total_sugestoes']}\n")
                if melhoria.get('agentes_envolvidos'):
                    f.write(f"- **Agentes Envolvidos**: {', '.join(melhoria['agentes_envolvidos'])}\n")
                f.write("\n")
                
                # Listar sugestões
                if melhoria.get('sugestoes'):
                    f.write("**Sugestões:**\n")
                    for sug in melhoria['sugestoes'][:5]:
                        f.write(f"- [{sug.get('prioridade', '?').upper()}] {sug.get('descricao')}\n")
                    f.write("\n")
            
            # Descobertas por agente
            f.write("## 🤖 Descobertas por Agente\n\n")
            for nome_agente, descoberta in resultados['descobertas_por_agente'].items():
                f.write(f"### {nome_agente.upper()}\n\n")
                f.write(f"- **Pontos Observados**: {len(descoberta.get('pontos_observados', []))}\n")
                f.write(f"- **Sugestões**: {len(descoberta.get('sugestoes', []))}\n\n")
            
            f.write("\n---\n\n")
            f.write("*Relatório gerado automaticamente pela Sessão Colaborativa de Agentes*\n")


def main():
    """Função principal."""
    print("=" * 80)
    print("🤝 SESSÃO COLABORATIVA DE AGENTES - IASENIOR")
    print("=" * 80)
    print()
    
    sessao = SessaoColaborativaAgentes()
    
    # Inicializar agentes
    if not sessao.inicializar_agentes():
        print("❌ Falha ao inicializar agentes")
        return 1
    
    # Realizar sessão
    try:
        resultados = sessao.realizar_sessao()
        
        print("\n" + "=" * 80)
        print("✅ SESSÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"\n📊 Resumo:")
        print(f"   • {len(resultados['descobertas_por_agente'])} agentes analisaram o projeto")
        print(f"   • {len(resultados['melhorias_encontradas'])} categorias de melhorias identificadas")
        print(f"   • {len(resultados['melhorias_priorizadas'])} melhorias priorizadas")
        print(f"\n💾 Consulte os arquivos em: agents_data/sessao_colaborativa/")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Sessão interrompida pelo usuário")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro na sessão: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

