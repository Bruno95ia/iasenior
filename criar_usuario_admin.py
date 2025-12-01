#!/usr/bin/env python3
"""
Script para criar usuário administrador inicial - IASenior
"""

import os
import sys
import getpass
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from auth import get_auth_manager
from database import get_db_manager

def main():
    """Cria usuário administrador inicial."""
    print("=" * 70)
    print("🔐 Criar Usuário Administrador - IASenior")
    print("=" * 70)
    print()
    
    # Verificar se já existe usuário admin
    db = get_db_manager()
    usuario_existente = db.obter_usuario_por_username('admin')
    
    if usuario_existente:
        print("⚠️  Usuário 'admin' já existe!")
        resposta = input("Deseja redefinir a senha? (s/N): ").strip().lower()
        if resposta != 's':
            print("❌ Operação cancelada.")
            return
        
        # Aqui você poderia adicionar lógica para redefinir senha
        print("💡 Use o script de redefinição de senha ou edite diretamente no banco.")
        return
    
    # Coletar dados
    print("Preencha os dados do administrador:")
    print()
    
    username = input("Usuário (padrão: admin): ").strip() or 'admin'
    email = input("Email (opcional): ").strip() or None
    nome_completo = input("Nome completo (opcional): ").strip() or None
    
    while True:
        senha = getpass.getpass("Senha: ")
        if len(senha) < 6:
            print("❌ Senha deve ter pelo menos 6 caracteres.")
            continue
        
        senha_confirmacao = getpass.getpass("Confirmar senha: ")
        if senha != senha_confirmacao:
            print("❌ Senhas não coincidem. Tente novamente.")
            continue
        
        break
    
    print()
    print("Criando usuário...")
    
    try:
        auth_manager = get_auth_manager()
        resultado = auth_manager.criar_usuario(
            username=username,
            senha=senha,
            email=email,
            nome_completo=nome_completo,
            nivel_acesso_id=1  # Admin
        )
        
        if resultado['sucesso']:
            print("=" * 70)
            print("✅ Usuário administrador criado com sucesso!")
            print("=" * 70)
            print(f"👤 Usuário: {username}")
            print(f"📧 Email: {email or 'Não informado'}")
            print(f"👨‍💼 Nome: {nome_completo or 'Não informado'}")
            print(f"🔑 Nível: Administrador")
            print(f"🆔 ID: {resultado['usuario_id']}")
            print("=" * 70)
            print()
            print("💡 Você pode usar este usuário para fazer login no sistema.")
        else:
            print("❌ Erro ao criar usuário:")
            print(f"   {resultado['mensagem']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

