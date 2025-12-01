#!/usr/bin/env python3
"""
Servidor HTTP com autenticação - IASenior
Servidor Flask com sistema de autenticação integrado.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory, redirect, session
from flask_cors import CORS

try:
    from auth import get_auth_manager
    from database import get_db_manager
    AUTH_AVAILABLE = True
except ImportError as e:
    AUTH_AVAILABLE = False
    logging.warning(f"Autenticação não disponível: {e}")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())
CORS(app, supports_credentials=True)

# Configurações
FILE_NAME = "portal_cliente.html"
LOGIN_FILE = "login.html"
PORT = int(os.getenv('PORT', '8080'))


def obter_token():
    """Obtém token do header Authorization ou cookie."""
    # Tentar header Authorization
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Tentar cookie
    token = request.cookies.get('session_token')
    if token:
        return token
    
    # Tentar localStorage (via JavaScript)
    token = request.headers.get('X-Session-Token')
    if token:
        return token
    
    return None


def verificar_autenticacao():
    """Verifica se o usuário está autenticado."""
    if not AUTH_AVAILABLE:
        return None
    
    token = obter_token()
    if not token:
        return None
    
    auth_manager = get_auth_manager()
    resultado = auth_manager.verificar_token(token)
    
    if resultado:
        return resultado['usuario']
    return None


def requer_autenticacao(f):
    """Decorador para rotas que requerem autenticação."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = verificar_autenticacao()
        if not usuario:
            if request.path.startswith('/api/'):
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Não autenticado',
                    'requer_login': True
                }), 401
            else:
                return redirect(f'/login.html?redirect={request.path}')
        request.usuario = usuario
        return f(*args, **kwargs)
    return decorated_function


def requer_permissao(permissao: str):
    """Decorador para rotas que requerem permissão específica."""
    def decorator(f):
        @wraps(f)
        @requer_autenticacao
        def decorated_function(*args, **kwargs):
            usuario = request.usuario
            auth_manager = get_auth_manager()
            
            if not auth_manager.verificar_permissao(usuario, permissao):
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Permissão negada'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requer_nivel(nivel_minimo: int):
    """Decorador para rotas que requerem nível mínimo."""
    def decorator(f):
        @wraps(f)
        @requer_autenticacao
        def decorated_function(*args, **kwargs):
            usuario = request.usuario
            auth_manager = get_auth_manager()
            
            if not auth_manager.verificar_nivel_minimo(usuario, nivel_minimo):
                return jsonify({
                    'sucesso': False,
                    'mensagem': 'Nível de acesso insuficiente'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Rotas de autenticação
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Endpoint de login."""
    if not AUTH_AVAILABLE:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Sistema de autenticação não disponível'
        }), 503
    
    try:
        data = request.get_json()
        username = data.get('username')
        senha = data.get('password')
        
        if not username or not senha:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Usuário e senha são obrigatórios'
            }), 400
        
        auth_manager = get_auth_manager()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        resultado = auth_manager.login(username, senha, ip_address, user_agent)
        
        if resultado['sucesso']:
            response = jsonify(resultado)
            response.set_cookie(
                'session_token',
                resultado['token'],
                max_age=86400,  # 24 horas
                httponly=True,
                secure=False,  # True em produção com HTTPS
                samesite='Lax'
            )
            return response
        else:
            return jsonify(resultado), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro interno do servidor'
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@requer_autenticacao
def api_logout():
    """Endpoint de logout."""
    if not AUTH_AVAILABLE:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Sistema de autenticação não disponível'
        }), 503
    
    try:
        token = obter_token()
        if token:
            auth_manager = get_auth_manager()
            auth_manager.logout(token)
        
        response = jsonify({'sucesso': True, 'mensagem': 'Logout realizado'})
        response.set_cookie('session_token', '', expires=0)
        return response
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro interno do servidor'
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
def api_verify():
    """Endpoint para verificar se token é válido."""
    if not AUTH_AVAILABLE:
        return jsonify({
            'valido': False,
            'mensagem': 'Sistema de autenticação não disponível'
        }), 503
    
    try:
        token = obter_token()
        if not token:
            return jsonify({'valido': False}), 401
        
        auth_manager = get_auth_manager()
        resultado = auth_manager.verificar_token(token)
        
        if resultado:
            return jsonify({
                'valido': True,
                'usuario': resultado['usuario']
            })
        else:
            return jsonify({'valido': False}), 401
            
    except Exception as e:
        logger.error(f"Erro ao verificar token: {e}", exc_info=True)
        return jsonify({'valido': False}), 500


@app.route('/api/auth/me', methods=['GET'])
@requer_autenticacao
def api_me():
    """Endpoint para obter dados do usuário atual."""
    return jsonify({
        'sucesso': True,
        'usuario': request.usuario
    })


# Rotas de arquivos estáticos
@app.route('/')
def index():
    """Redireciona para login ou portal."""
    usuario = verificar_autenticacao()
    if usuario:
        return redirect('/portal_cliente.html')
    else:
        return redirect('/login.html')


@app.route('/login.html')
def login():
    """Página de login."""
    return send_from_directory('.', LOGIN_FILE)


@app.route('/portal_cliente.html')
@requer_autenticacao
def portal():
    """Portal do cliente (requer autenticação)."""
    return send_from_directory('.', FILE_NAME)


@app.route('/<path:filename>')
def serve_file(filename):
    """Serve arquivos estáticos."""
    # Arquivos públicos (não requerem autenticação)
    arquivos_publicos = [
        'login.html',
        'manifest.json',
        'service-worker.js',
        'static'
    ]
    
    # Verificar se é arquivo público
    if any(filename.startswith(arq) for arq in arquivos_publicos):
        return send_from_directory('.', filename)
    
    # Outros arquivos requerem autenticação
    usuario = verificar_autenticacao()
    if not usuario:
        if filename.endswith('.html'):
            return redirect(f'/login.html?redirect=/{filename}')
        else:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Não autenticado'
            }), 401
    
    return send_from_directory('.', filename)


# Health check
@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'auth_available': AUTH_AVAILABLE
    })


def main():
    """Inicia o servidor."""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    file_path = script_dir / FILE_NAME
    if not file_path.exists():
        logger.error(f"Arquivo {FILE_NAME} não encontrado em {script_dir}")
        return
    
    logger.info("=" * 70)
    logger.info("🚀 Servidor do Portal do Cliente com Autenticação iniciado!")
    logger.info("=" * 70)
    logger.info(f"📂 Diretório: {script_dir}")
    logger.info(f"🌐 URL: http://localhost:{PORT}")
    logger.info(f"🔐 Autenticação: {'Ativa' if AUTH_AVAILABLE else 'Desativada'}")
    logger.info("=" * 70)
    logger.info("\n💡 Pressione Ctrl+C para parar o servidor\n")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Servidor parado pelo usuário.")
        logger.info("👋 Até logo!")


if __name__ == "__main__":
    main()

