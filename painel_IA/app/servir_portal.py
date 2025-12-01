#!/usr/bin/env python3
"""
Servidor HTTP simples para visualizar o Portal do Cliente.
Força atualizações sempre, evitando cache do navegador.
"""

import http.server
import socketserver
import webbrowser
import os
import socket
import time
from pathlib import Path
from datetime import datetime

FILE_NAME = "portal_cliente.html"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Headers agressivos para evitar cache e garantir atualizações
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Content-Type-Options', 'nosniff')
        # Adicionar timestamp para forçar revalidação
        self.send_header('Last-Modified', datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'))
        super().end_headers()
    
    def do_GET(self):
        # Adicionar timestamp como query string para evitar cache
        if '?' not in self.path and self.path.endswith('.html'):
            # Redirecionar para URL com timestamp
            timestamp = int(time.time())
            self.send_response(302)
            self.send_header('Location', f"{self.path}?v={timestamp}")
            self.end_headers()
            return
        
        # Servir arquivo normalmente
        super().do_GET()
    
    def log_message(self, format, *args):
        # Log customizado com timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def find_free_port(start_port=8080, max_attempts=10):
    """Encontra uma porta livre."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Não foi possível encontrar uma porta livre entre {start_port} e {start_port + max_attempts}")

def get_file_info(file_path):
    """Obtém informações do arquivo para exibir no console."""
    if file_path.exists():
        stat = file_path.stat()
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime)
        return {
            'size': size,
            'modified': modified,
            'exists': True
        }
    return {'exists': False}

def main():
    # Mudar para o diretório do arquivo
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    file_path = script_dir / FILE_NAME
    
    # Verificar se o arquivo existe
    if not file_path.exists():
        print(f"❌ Erro: Arquivo {FILE_NAME} não encontrado em {script_dir}")
        return
    
    # Obter informações do arquivo
    file_info = get_file_info(file_path)
    
    # Encontrar porta livre
    PORT = find_free_port(8080)
    
    # Criar servidor
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            # Adicionar timestamp para evitar cache
            timestamp = int(time.time())
            url = f"http://localhost:{PORT}/{FILE_NAME}?v={timestamp}"
            
            print("=" * 70)
            print("🚀 Servidor do Portal do Cliente iniciado!")
            print("=" * 70)
            print(f"📂 Diretório: {script_dir}")
            print(f"🌐 URL: {url}")
            print(f"📄 Arquivo: {FILE_NAME}")
            print(f"📊 Tamanho: {file_info['size']:,} bytes")
            print(f"🕒 Última modificação: {file_info['modified'].strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"🔌 Porta: {PORT}")
            print(f"🔄 Cache: DESABILITADO (sempre carrega versão mais recente)")
            print("=" * 70)
            print("\n💡 Pressione Ctrl+C para parar o servidor")
            print("💡 Para forçar atualização: Ctrl+Shift+R (Chrome) ou Ctrl+F5 (Firefox)\n")
            
            # Abrir no navegador automaticamente
            try:
                webbrowser.open(url)
                print(f"✅ Abrindo no navegador...")
            except Exception as e:
                print(f"⚠️  Não foi possível abrir automaticamente: {e}")
                print(f"   Abra manualmente: {url}")
            
            # Iniciar servidor
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\n🛑 Servidor parado pelo usuário.")
                print("👋 Até logo!")
    except OSError as e:
        print(f"❌ Erro ao iniciar servidor na porta {PORT}: {e}")
        print(f"💡 Tente matar o processo: kill -9 $(lsof -ti:{PORT})")

if __name__ == "__main__":
    main()
