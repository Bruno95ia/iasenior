"""
Sistema de Notificações - IASenior
Envia notificações por email, SMS e outros canais para cuidadores.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    import smtplib
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

logger = logging.getLogger(__name__)


class NotificacaoManager:
    """
    Gerenciador de notificações para o sistema IASenior.
    Suporta email, SMS (via API) e webhooks.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o gerenciador de notificações.
        
        Args:
            config: Configurações de notificações
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true')
        
        # Configurações de email
        self.smtp_host = self.config.get('smtp_host', os.getenv('SMTP_HOST', 'smtp.gmail.com'))
        self.smtp_port = self.config.get('smtp_port', int(os.getenv('SMTP_PORT', '587')))
        self.smtp_user = self.config.get('smtp_user', os.getenv('SMTP_USER', ''))
        self.smtp_password = self.config.get('smtp_password', os.getenv('SMTP_PASSWORD', ''))
        self.smtp_use_tls = self.config.get('smtp_use_tls', os.getenv('SMTP_USE_TLS', 'true').lower() == 'true')
        
        # Destinatários
        self.email_destinatarios = self.config.get('email_destinatarios', [])
        if not self.email_destinatarios:
            # Ler de variável de ambiente (separado por vírgula)
            env_emails = os.getenv('NOTIFICATION_EMAILS', '')
            if env_emails:
                self.email_destinatarios = [e.strip() for e in env_emails.split(',')]
        
        # Configurações de alertas
        self.alertar_quedas = self.config.get('alertar_quedas', True)
        self.alertar_banheiro = self.config.get('alertar_banheiro', True)
        self.alertar_sistema = self.config.get('alertar_sistema', False)
        
        # Histórico de notificações enviadas
        self.historico_notificacoes = []
        
        if not self.enabled:
            logger.info("ℹ️ Notificações desabilitadas")
        elif not SMTP_AVAILABLE:
            logger.warning("⚠️ smtplib não disponível. Notificações por email desabilitadas.")
    
    def enviar_email(self, assunto: str, corpo: str, html: str = None, 
                    destinatarios: List[str] = None, anexos: List[Dict] = None) -> bool:
        """
        Envia email de notificação.
        
        Args:
            assunto: Assunto do email
            corpo: Corpo do email (texto)
            html: Corpo do email (HTML, opcional)
            destinatarios: Lista de destinatários (usa padrão se None)
            anexos: Lista de anexos [{'arquivo': path, 'nome': nome}]
        
        Returns:
            True se enviado com sucesso
        """
        if not self.enabled or not SMTP_AVAILABLE:
            return False
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("⚠️ Credenciais SMTP não configuradas")
            return False
        
        destinatarios = destinatarios or self.email_destinatarios
        if not destinatarios:
            logger.warning("⚠️ Nenhum destinatário configurado")
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = assunto
            
            # Adicionar corpo
            part_text = MIMEText(corpo, 'plain', 'utf-8')
            msg.attach(part_text)
            
            if html:
                part_html = MIMEText(html, 'html', 'utf-8')
                msg.attach(part_html)
            
            # Adicionar anexos
            if anexos:
                for anexo in anexos:
                    arquivo_path = anexo.get('arquivo')
                    nome_arquivo = anexo.get('nome', Path(arquivo_path).name)
                    
                    if Path(arquivo_path).exists():
                        with open(arquivo_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {nome_arquivo}'
                            )
                            msg.attach(part)
            
            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            # Registrar no histórico
            self.historico_notificacoes.append({
                'tipo': 'email',
                'assunto': assunto,
                'destinatarios': destinatarios,
                'timestamp': datetime.now().isoformat(),
                'sucesso': True
            })
            
            logger.info(f"✅ Email enviado: {assunto} para {len(destinatarios)} destinatário(s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            
            # Registrar falha
            self.historico_notificacoes.append({
                'tipo': 'email',
                'assunto': assunto,
                'destinatarios': destinatarios,
                'timestamp': datetime.now().isoformat(),
                'sucesso': False,
                'erro': str(e)
            })
            
            return False
    
    def notificar_queda(self, metadata: Dict = None) -> bool:
        """
        Envia notificação de queda detectada.
        
        Args:
            metadata: Dados adicionais sobre a queda
        
        Returns:
            True se notificação enviada
        """
        if not self.alertar_quedas:
            return False
        
        assunto = "🚨 ALERTA: Queda Detectada - Sistema IASenior"
        
        corpo = f"""
ALERTA CRÍTICO - QUEDA DETECTADA

O sistema de monitoramento IASenior detectou uma possível queda.

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Por favor, verifique imediatamente a pessoa monitorada.

---
Sistema IASenior - Monitoramento Inteligente
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert {{ background-color: #fee; border-left: 5px solid #c00; padding: 15px; margin: 20px 0; }}
        .header {{ background-color: #c00; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 ALERTA: QUEDA DETECTADA</h1>
    </div>
    <div class="content">
        <div class="alert">
            <h2>O sistema detectou uma possível queda</h2>
            <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Ação necessária:</strong> Verifique imediatamente a pessoa monitorada.</p>
        </div>
    </div>
    <div class="footer">
        Sistema IASenior - Monitoramento Inteligente<br>
        Este é um email automático, por favor não responda.
    </div>
</body>
</html>
"""
        
        return self.enviar_email(assunto, corpo, html)
    
    def notificar_banheiro_tempo(self, track_id: str, tempo_minutos: int, tempo_segundos: int) -> bool:
        """
        Envia notificação de tempo excedido no banheiro.
        
        Args:
            track_id: ID da pessoa
            tempo_minutos: Minutos no banheiro
            tempo_segundos: Segundos no banheiro
        
        Returns:
            True se notificação enviada
        """
        if not self.alertar_banheiro:
            return False
        
        assunto = f"⚠️ Alerta: Tempo no Banheiro Excedido ({tempo_minutos}min)"
        
        corpo = f"""
ALERTA - TEMPO NO BANHEIRO EXCEDIDO

Uma pessoa está no banheiro há mais tempo que o limite configurado.

Pessoa: {track_id}
Tempo no banheiro: {tempo_minutos} minutos e {tempo_segundos} segundos
Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Por favor, verifique se está tudo bem.

---
Sistema IASenior - Monitoramento Inteligente
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert {{ background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 20px 0; }}
        .header {{ background-color: #ffc107; color: #000; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ Alerta: Tempo no Banheiro Excedido</h1>
    </div>
    <div class="content">
        <div class="alert">
            <h2>Uma pessoa está no banheiro há mais tempo que o limite</h2>
        </div>
        <div class="info">
            <p><strong>Pessoa:</strong> {track_id}</p>
            <p><strong>Tempo no banheiro:</strong> {tempo_minutos} minutos e {tempo_segundos} segundos</p>
            <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        <p>Por favor, verifique se está tudo bem.</p>
    </div>
    <div class="footer">
        Sistema IASenior - Monitoramento Inteligente<br>
        Este é um email automático, por favor não responda.
    </div>
</body>
</html>
"""
        
        return self.enviar_email(assunto, corpo, html)
    
    def notificar_sistema(self, tipo: str, mensagem: str, severidade: str = 'info') -> bool:
        """
        Envia notificação de sistema (erros, avisos, etc).
        
        Args:
            tipo: Tipo de notificação
            mensagem: Mensagem
            severidade: Severidade ('info', 'warning', 'error')
        
        Returns:
            True se notificação enviada
        """
        if not self.alertar_sistema and severidade != 'error':
            return False
        
        if severidade == 'error':
            assunto = f"❌ Erro no Sistema IASenior: {tipo}"
            cor = "#c00"
        elif severidade == 'warning':
            assunto = f"⚠️ Aviso no Sistema IASenior: {tipo}"
            cor = "#ffc107"
        else:
            assunto = f"ℹ️ Informação do Sistema IASenior: {tipo}"
            cor = "#17a2b8"
        
        corpo = f"""
NOTIFICAÇÃO DO SISTEMA

Tipo: {tipo}
Severidade: {severidade.upper()}
Mensagem: {mensagem}

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
Sistema IASenior - Monitoramento Inteligente
"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .alert {{ background-color: #f8f9fa; border-left: 5px solid {cor}; padding: 15px; margin: 20px 0; }}
        .header {{ background-color: {cor}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{assunto}</h1>
    </div>
    <div class="content">
        <div class="alert">
            <p><strong>Tipo:</strong> {tipo}</p>
            <p><strong>Severidade:</strong> {severidade.upper()}</p>
            <p><strong>Mensagem:</strong> {mensagem}</p>
            <p><strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </div>
    <div class="footer">
        Sistema IASenior - Monitoramento Inteligente<br>
        Este é um email automático, por favor não responda.
    </div>
</body>
</html>
"""
        
        return self.enviar_email(assunto, corpo, html)
    
    def obter_historico(self, limite: int = 50) -> List[Dict]:
        """
        Obtém histórico de notificações enviadas.
        
        Args:
            limite: Limite de registros
        
        Returns:
            Lista de notificações
        """
        return self.historico_notificacoes[-limite:]


# Instância global
_notificacao_manager = None


def get_notificacao_manager(config: Dict[str, Any] = None) -> NotificacaoManager:
    """
    Obtém instância global do gerenciador de notificações.
    
    Args:
        config: Configurações (opcional)
    
    Returns:
        Instância de NotificacaoManager
    """
    global _notificacao_manager
    if _notificacao_manager is None:
        _notificacao_manager = NotificacaoManager(config)
    return _notificacao_manager

