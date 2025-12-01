"""
Sistema de Autenticação - IASenior
Gerencia login, logout, sessões e verificação de permissões por níveis de acesso.
"""

import os
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from functools import wraps

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt não instalado. Instale com: pip install bcrypt")

from database import get_db_manager

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Gerenciador de autenticação e autorização.
    Gerencia login, logout, sessões e verificação de permissões.
    """
    
    # Níveis de acesso
    NIVEL_ADMIN = 1
    NIVEL_OPERADOR = 2
    NIVEL_VISUALIZADOR = 3
    NIVEL_CLIENTE = 4
    
    # Nomes dos níveis
    NIVEIS = {
        1: 'admin',
        2: 'operador',
        3: 'visualizador',
        4: 'cliente'
    }
    
    def __init__(self, db_config: Dict[str, Any] = None):
        """Inicializa o gerenciador de autenticação."""
        if not BCRYPT_AVAILABLE:
            raise ImportError("bcrypt não está instalado. Instale com: pip install bcrypt")
        
        self.db = get_db_manager(db_config)
        self.token_expiration_hours = int(os.getenv('TOKEN_EXPIRATION_HOURS', '24'))
        self.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
        
        # Limpar sessões expiradas ao iniciar
        self.db.limpar_sessoes_expiradas()
    
    def hash_senha(self, senha: str) -> str:
        """
        Gera hash bcrypt da senha.
        
        Args:
            senha: Senha em texto plano
        
        Returns:
            Hash bcrypt da senha
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_senha(self, senha: str, senha_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            senha: Senha em texto plano
            senha_hash: Hash bcrypt da senha
        
        Returns:
            True se a senha estiver correta
        """
        try:
            return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"❌ Erro ao verificar senha: {e}")
            return False
    
    def gerar_token(self) -> str:
        """
        Gera um token de sessão único.
        
        Returns:
            Token hexadecimal de 64 caracteres
        """
        return secrets.token_hex(32)
    
    def login(self, username: str, senha: str, ip_address: str = None, 
             user_agent: str = None) -> Dict[str, Any]:
        """
        Realiza login de usuário.
        
        Args:
            username: Nome de usuário
            senha: Senha em texto plano
            ip_address: Endereço IP do cliente
            user_agent: User agent do navegador
        
        Returns:
            Dict com resultado do login:
            - sucesso: bool
            - token: str (se sucesso)
            - usuario: dict (se sucesso)
            - mensagem: str
        """
        try:
            # Obter usuário
            usuario = self.db.obter_usuario_por_username(username)
            
            if not usuario:
                self.db.registrar_log_autenticacao(
                    username=username,
                    tipo_evento='login',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    sucesso=False,
                    mensagem='Usuário não encontrado'
                )
                return {
                    'sucesso': False,
                    'mensagem': 'Usuário ou senha incorretos'
                }
            
            # Verificar se usuário está ativo
            if not usuario.get('ativo'):
                self.db.registrar_log_autenticacao(
                    usuario_id=usuario['id'],
                    username=username,
                    tipo_evento='login',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    sucesso=False,
                    mensagem='Usuário inativo'
                )
                return {
                    'sucesso': False,
                    'mensagem': 'Usuário inativo. Entre em contato com o administrador.'
                }
            
            # Verificar se está bloqueado
            if usuario.get('bloqueado_ate'):
                bloqueado_ate = usuario['bloqueado_ate']
                if isinstance(bloqueado_ate, str):
                    bloqueado_ate = datetime.fromisoformat(bloqueado_ate.replace('Z', '+00:00'))
                
                if bloqueado_ate and bloqueado_ate > datetime.now():
                    self.db.registrar_log_autenticacao(
                        usuario_id=usuario['id'],
                        username=username,
                        tipo_evento='login',
                        ip_address=ip_address,
                        user_agent=user_agent,
                        sucesso=False,
                        mensagem='Usuário bloqueado temporariamente'
                    )
                    return {
                        'sucesso': False,
                        'mensagem': f'Conta bloqueada temporariamente. Tente novamente mais tarde.'
                    }
            
            # Verificar senha
            if not self.verificar_senha(senha, usuario['senha_hash']):
                # Incrementar tentativas falhadas
                self.db.incrementar_tentativas_falhadas(username)
                
                self.db.registrar_log_autenticacao(
                    usuario_id=usuario['id'],
                    username=username,
                    tipo_evento='login',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    sucesso=False,
                    mensagem='Senha incorreta'
                )
                return {
                    'sucesso': False,
                    'mensagem': 'Usuário ou senha incorretos'
                }
            
            # Login bem-sucedido
            # Gerar token
            token = self.gerar_token()
            expira_em = datetime.now() + timedelta(hours=self.token_expiration_hours)
            
            # Criar sessão
            self.db.criar_sessao(
                usuario_id=usuario['id'],
                token=token,
                ip_address=ip_address,
                user_agent=user_agent,
                expira_em=expira_em
            )
            
            # Atualizar último login
            self.db.atualizar_ultimo_login(usuario['id'])
            
            # Registrar log de sucesso
            self.db.registrar_log_autenticacao(
                usuario_id=usuario['id'],
                username=username,
                tipo_evento='login',
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=True,
                mensagem='Login realizado com sucesso'
            )
            
            # Remover dados sensíveis
            usuario_retorno = {
                'id': usuario['id'],
                'username': usuario['username'],
                'email': usuario.get('email'),
                'nome_completo': usuario.get('nome_completo'),
                'nivel_nome': usuario.get('nivel_nome'),
                'nivel_numero': usuario.get('nivel_numero'),
                'permissoes': usuario.get('permissoes', {})
            }
            
            return {
                'sucesso': True,
                'token': token,
                'usuario': usuario_retorno,
                'mensagem': 'Login realizado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {e}", exc_info=True)
            return {
                'sucesso': False,
                'mensagem': 'Erro interno ao realizar login'
            }
    
    def logout(self, token: str):
        """
        Realiza logout (invalida sessão).
        
        Args:
            token: Token da sessão
        """
        try:
            sessao = self.db.obter_sessao(token)
            if sessao:
                self.db.invalidar_sessao(token)
                self.db.registrar_log_autenticacao(
                    usuario_id=sessao['usuario_id'],
                    username=sessao['username'],
                    tipo_evento='logout',
                    sucesso=True,
                    mensagem='Logout realizado'
                )
        except Exception as e:
            logger.error(f"❌ Erro no logout: {e}")
    
    def verificar_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se um token é válido e retorna dados da sessão.
        
        Args:
            token: Token da sessão
        
        Returns:
            Dict com dados da sessão e usuário, ou None se inválido
        """
        try:
            sessao = self.db.obter_sessao(token)
            if not sessao:
                return None
            
            # Verificar se usuário ainda está ativo
            if not sessao.get('usuario_ativo'):
                self.db.invalidar_sessao(token)
                return None
            
            # Obter dados completos do usuário
            usuario = self.db.obter_usuario_por_id(sessao['usuario_id'])
            if not usuario:
                return None
            
            return {
                'sessao': sessao,
                'usuario': {
                    'id': usuario['id'],
                    'username': usuario['username'],
                    'email': usuario.get('email'),
                    'nome_completo': usuario.get('nome_completo'),
                    'nivel_nome': usuario.get('nivel_nome'),
                    'nivel_numero': usuario.get('nivel_numero'),
                    'permissoes': usuario.get('permissoes', {})
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar token: {e}")
            return None
    
    def verificar_permissao(self, usuario: Dict[str, Any], permissao: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            usuario: Dict com dados do usuário (deve ter 'permissoes')
            permissao: Nome da permissão a verificar
        
        Returns:
            True se o usuário tem a permissão
        """
        permissoes = usuario.get('permissoes', {})
        
        # Admin tem acesso total
        if permissoes.get('acesso_total'):
            return True
        
        # Verificar permissão específica
        return permissoes.get(permissao, False)
    
    def verificar_nivel_minimo(self, usuario: Dict[str, Any], nivel_minimo: int) -> bool:
        """
        Verifica se o usuário tem nível mínimo necessário.
        
        Args:
            usuario: Dict com dados do usuário (deve ter 'nivel_numero')
            nivel_minimo: Nível mínimo necessário (1=admin, 2=operador, etc)
        
        Returns:
            True se o usuário tem nível suficiente (número menor = maior privilégio)
        """
        nivel_usuario = usuario.get('nivel_numero', 999)
        return nivel_usuario <= nivel_minimo
    
    def criar_usuario(self, username: str, senha: str, email: str = None,
                     nome_completo: str = None, nivel_acesso_id: int = 4,
                     metadata: Dict = None) -> Dict[str, Any]:
        """
        Cria um novo usuário.
        
        Args:
            username: Nome de usuário único
            senha: Senha em texto plano
            email: Email do usuário
            nome_completo: Nome completo
            nivel_acesso_id: ID do nível de acesso
            metadata: Dados adicionais
        
        Returns:
            Dict com resultado da criação
        """
        try:
            senha_hash = self.hash_senha(senha)
            usuario_id = self.db.criar_usuario(
                username=username,
                senha_hash=senha_hash,
                email=email,
                nome_completo=nome_completo,
                nivel_acesso_id=nivel_acesso_id,
                metadata=metadata
            )
            
            return {
                'sucesso': True,
                'usuario_id': usuario_id,
                'mensagem': 'Usuário criado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar usuário: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao criar usuário: {str(e)}'
            }


# Instância global (singleton)
_auth_manager = None


def get_auth_manager(db_config: Dict[str, Any] = None) -> AuthManager:
    """
    Obtém instância global do gerenciador de autenticação.
    
    Args:
        db_config: Configurações de conexão (opcional)
    
    Returns:
        Instância de AuthManager
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(db_config)
    return _auth_manager


# Decoradores para verificação de autenticação e permissões

def requer_autenticacao(f):
    """
    Decorador para verificar se o usuário está autenticado.
    Usa token do header 'Authorization' ou cookie 'session_token'.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Esta função será implementada quando integrarmos com Flask/HTTP
        # Por enquanto, é apenas uma estrutura
        return f(*args, **kwargs)
    return wrapper


def requer_permissao(permissao: str):
    """
    Decorador para verificar se o usuário tem uma permissão específica.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Esta função será implementada quando integrarmos com Flask/HTTP
            return f(*args, **kwargs)
        return wrapper
    return decorator


def requer_nivel(nivel_minimo: int):
    """
    Decorador para verificar se o usuário tem nível mínimo necessário.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Esta função será implementada quando integrarmos com Flask/HTTP
            return f(*args, **kwargs)
        return wrapper
    return decorator

