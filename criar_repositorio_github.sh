#!/bin/bash
# ============================================================================
# Script para criar repositório no GitHub e fazer push
# ============================================================================

set -e

echo "🚀 Criando repositório no GitHub..."
echo "===================================="

# Verificar se está autenticado
if ! gh auth status &>/dev/null; then
    echo "❌ Você precisa autenticar primeiro!"
    echo ""
    echo "Execute:"
    echo "  gh auth login"
    echo ""
    echo "Ou se preferir via web:"
    echo "  gh auth login --web"
    echo ""
    exit 1
fi

# Criar repositório
echo "📦 Criando repositório 'iasenior' no GitHub..."
gh repo create iasenior \
    --public \
    --description "Sistema de Monitoramento Inteligente com IA para detecção de quedas em tempo real" \
    --source=. \
    --remote=origin \
    --push

echo ""
echo "✅ Repositório criado e código enviado!"
echo ""
echo "🌐 Acesse: https://github.com/$(gh api user --jq .login)/iasenior"
echo ""

