"""
Sistema de Relatórios - IASenior
Gera relatórios médicos em PDF e exportação CSV/Excel.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("reportlab não instalado. Instale com: pip install reportlab")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RelatorioManager:
    """
    Gerenciador de relatórios para o sistema IASenior.
    Gera relatórios em PDF, CSV e Excel.
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Inicializa o gerenciador de relatórios.
        
        Args:
            output_dir: Diretório para salvar relatórios
        """
        self.output_dir = output_dir or Path("relatorios")
        self.output_dir.mkdir(exist_ok=True)
    
    def gerar_relatorio_pdf(self, periodo: str = 'diario', 
                            data_inicio: datetime = None, 
                            data_fim: datetime = None,
                            dados: Dict = None) -> Optional[str]:
        """
        Gera relatório em PDF.
        
        Args:
            periodo: 'diario', 'semanal', 'mensal' ou 'custom'
            data_inicio: Data inicial (para custom)
            data_fim: Data final (para custom)
            dados: Dados do banco de dados (opcional)
        
        Returns:
            Caminho do arquivo PDF gerado ou None
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("❌ reportlab não está instalado. Instale com: pip install reportlab")
            return None
        
        try:
            # Calcular período
            if periodo == 'diario':
                data_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                data_fim = datetime.now()
            elif periodo == 'semanal':
                data_inicio = datetime.now() - timedelta(days=7)
                data_fim = datetime.now()
            elif periodo == 'mensal':
                data_inicio = datetime.now() - timedelta(days=30)
                data_fim = datetime.now()
            elif periodo == 'custom':
                if not data_inicio or not data_fim:
                    logger.error("❌ data_inicio e data_fim são obrigatórios para período custom")
                    return None
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{periodo}_{timestamp}.pdf"
            filepath = self.output_dir / filename
            
            # Criar documento PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo de título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Título
            story.append(Paragraph("Relatório de Monitoramento IASenior", title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Período
            periodo_text = f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
            story.append(Paragraph(periodo_text, styles['Normal']))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 1*cm))
            
            # Se dados foram fornecidos, usar eles
            if dados:
                # Resumo Executivo
                story.append(Paragraph("<b>Resumo Executivo</b>", styles['Heading2']))
                story.append(Spacer(1, 0.3*cm))
                
                resumo_data = [
                    ['Métrica', 'Valor'],
                    ['Total de Eventos', str(dados.get('total_eventos', 0))],
                    ['Quedas Detectadas', str(dados.get('quedas_detectadas', 0))],
                    ['Alertas de Banheiro', str(dados.get('alertas_banheiro', 0))],
                    ['Média Pessoas no Quarto', f"{dados.get('media_quarto', 0):.1f}"],
                    ['Média Pessoas no Banheiro', f"{dados.get('media_banheiro', 0):.1f}"],
                ]
                
                resumo_table = Table(resumo_data, colWidths=[10*cm, 7*cm])
                resumo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(resumo_table)
                story.append(Spacer(1, 1*cm))
                
                # Eventos Importantes
                if dados.get('eventos_importantes'):
                    story.append(Paragraph("<b>Eventos Importantes</b>", styles['Heading2']))
                    story.append(Spacer(1, 0.3*cm))
                    
                    eventos_data = [['Data/Hora', 'Tipo', 'Mensagem']]
                    for evento in dados['eventos_importantes'][:20]:  # Últimos 20
                        eventos_data.append([
                            evento.get('timestamp', '')[:16],
                            evento.get('tipo', ''),
                            evento.get('mensagem', '')[:50]
                        ])
                    
                    eventos_table = Table(eventos_data, colWidths=[4*cm, 4*cm, 9*cm])
                    eventos_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                    ]))
                    story.append(eventos_table)
                    story.append(PageBreak())
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"✅ Relatório PDF gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório PDF: {e}", exc_info=True)
            return None
    
    def exportar_csv(self, periodo: str = 'diario',
                    data_inicio: datetime = None,
                    data_fim: datetime = None,
                    dados: Dict = None) -> Optional[str]:
        """
        Exporta dados para CSV.
        
        Args:
            periodo: Período do relatório
            data_inicio: Data inicial
            data_fim: Data final
            dados: Dados do banco
        
        Returns:
            Caminho do arquivo CSV ou None
        """
        if not PANDAS_AVAILABLE:
            logger.error("❌ pandas não está instalado")
            return None
        
        try:
            # Calcular período (mesmo código do PDF)
            if periodo == 'diario':
                data_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                data_fim = datetime.now()
            elif periodo == 'semanal':
                data_inicio = datetime.now() - timedelta(days=7)
                data_fim = datetime.now()
            elif periodo == 'mensal':
                data_inicio = datetime.now() - timedelta(days=30)
                data_fim = datetime.now()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{periodo}_{timestamp}.csv"
            filepath = self.output_dir / filename
            
            # Preparar dados
            if dados:
                # Criar DataFrame com eventos
                if dados.get('eventos'):
                    df = pd.DataFrame(dados['eventos'])
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                else:
                    # Criar CSV vazio com estrutura
                    df = pd.DataFrame(columns=['timestamp', 'tipo', 'mensagem', 'severidade'])
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                # CSV vazio
                df = pd.DataFrame(columns=['timestamp', 'tipo', 'mensagem', 'severidade'])
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"✅ CSV exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar CSV: {e}")
            return None
    
    def exportar_excel(self, periodo: str = 'diario',
                      data_inicio: datetime = None,
                      data_fim: datetime = None,
                      dados: Dict = None) -> Optional[str]:
        """
        Exporta dados para Excel.
        
        Args:
            periodo: Período do relatório
            data_inicio: Data inicial
            data_fim: Data final
            dados: Dados do banco
        
        Returns:
            Caminho do arquivo Excel ou None
        """
        if not PANDAS_AVAILABLE:
            logger.error("❌ pandas não está instalado")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{periodo}_{timestamp}.xlsx"
            filepath = self.output_dir / filename
            
            # Criar Excel com múltiplas abas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                if dados:
                    # Aba de Eventos
                    if dados.get('eventos'):
                        df_eventos = pd.DataFrame(dados['eventos'])
                        df_eventos.to_excel(writer, sheet_name='Eventos', index=False)
                    
                    # Aba de Métricas
                    if dados.get('metricas'):
                        df_metricas = pd.DataFrame(dados['metricas'])
                        df_metricas.to_excel(writer, sheet_name='Métricas', index=False)
                    
                    # Aba de Alertas
                    if dados.get('alertas'):
                        df_alertas = pd.DataFrame(dados['alertas'])
                        df_alertas.to_excel(writer, sheet_name='Alertas', index=False)
                else:
                    # Planilhas vazias
                    pd.DataFrame(columns=['timestamp', 'tipo', 'mensagem']).to_excel(
                        writer, sheet_name='Eventos', index=False
                    )
            
            logger.info(f"✅ Excel exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar Excel: {e}")
            return None
    
    def gerar_relatorio_completo(self, periodo: str = 'diario',
                                db_manager = None) -> Dict[str, Optional[str]]:
        """
        Gera relatório completo (PDF + CSV + Excel).
        
        Args:
            periodo: Período do relatório
            db_manager: Instância de DatabaseManager (opcional)
        
        Returns:
            Dict com caminhos dos arquivos gerados
        """
        # Obter dados do banco se disponível
        dados = None
        if db_manager:
            try:
                # Calcular datas
                if periodo == 'diario':
                    data_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    data_fim = datetime.now()
                elif periodo == 'semanal':
                    data_inicio = datetime.now() - timedelta(days=7)
                    data_fim = datetime.now()
                elif periodo == 'mensal':
                    data_inicio = datetime.now() - timedelta(days=30)
                    data_fim = datetime.now()
                
                # Buscar dados
                eventos = db_manager.obter_eventos(inicio=data_inicio, fim=data_fim, limite=1000)
                metricas_quarto = db_manager.obter_metricas(
                    tipo_metrica='pessoas_quarto',
                    inicio=data_inicio,
                    fim=data_fim,
                    limite=1000
                )
                metricas_banheiro = db_manager.obter_metricas(
                    tipo_metrica='pessoas_banheiro',
                    inicio=data_inicio,
                    fim=data_fim,
                    limite=1000
                )
                alertas = db_manager.obter_alertas_ativos()
                
                # Calcular estatísticas
                quedas = [e for e in eventos if e.get('tipo') == 'queda_detectada']
                alertas_banheiro_list = [e for e in eventos if e.get('tipo') == 'alerta_banheiro']
                
                stats_quarto = db_manager.obter_estatisticas_ocupacao('quarto', data_inicio, data_fim)
                stats_banheiro = db_manager.obter_estatisticas_ocupacao('banheiro', data_inicio, data_fim)
                
                dados = {
                    'total_eventos': len(eventos),
                    'quedas_detectadas': len(quedas),
                    'alertas_banheiro': len(alertas_banheiro_list),
                    'media_quarto': float(stats_quarto.get('media', 0)),
                    'media_banheiro': float(stats_banheiro.get('media', 0)),
                    'eventos_importantes': eventos[:20],
                    'eventos': eventos,
                    'metricas': metricas_quarto + metricas_banheiro,
                    'alertas': alertas
                }
            except Exception as e:
                logger.error(f"Erro ao obter dados do banco: {e}")
        
        # Gerar relatórios
        resultado = {
            'pdf': self.gerar_relatorio_pdf(periodo=periodo, dados=dados),
            'csv': self.exportar_csv(periodo=periodo, dados=dados),
            'excel': self.exportar_excel(periodo=periodo, dados=dados)
        }
        
        return resultado


# Instância global
_relatorio_manager = None


def get_relatorio_manager(output_dir: Path = None) -> RelatorioManager:
    """
    Obtém instância global do gerenciador de relatórios.
    
    Args:
        output_dir: Diretório de saída (opcional)
    
    Returns:
        Instância de RelatorioManager
    """
    global _relatorio_manager
    if _relatorio_manager is None:
        _relatorio_manager = RelatorioManager(output_dir)
    return _relatorio_manager

