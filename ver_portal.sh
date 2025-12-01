#!/bin/bash

# Script para visualizar o Portal do Cliente

echo "🚀 Iniciando Portal do Cliente Opus Tech..."
echo ""

cd "$(dirname "$0")/painel_IA/app"

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale Python3."
    exit 1
fi

# Executar servidor
python3 servir_portal.py

