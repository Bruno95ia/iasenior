#!/bin/bash
# ============================================================================
# Helper Script para Configuração nos Servidores
# Facilita comunicação com GPT/Claude quando estiver nos servidores
# ============================================================================

LOG_FILE="/tmp/iasenior_setup_$(date +%Y%m%d_%H%M%S).log"

echo "🔧 Helper IASenior - Configuração de Servidores"
echo "================================================"
echo ""
echo "Este script ajuda a coletar informações e executar comandos"
echo "Log será salvo em: $LOG_FILE"
echo ""

# Função para executar comando e salvar resultado
executar() {
    local cmd="$1"
    echo ""
    echo "=== Executando: $cmd ===" | tee -a "$LOG_FILE"
    echo "Comando: $cmd" >> "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
    echo "---" >> "$LOG_FILE"
    echo "Exit code: $?" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# Menu
echo "Escolha uma opção:"
echo "1) Coletar informações do sistema"
echo "2) Executar comando sugerido pelo GPT"
echo "3) Ver log completo"
echo "4) Limpar log"
echo "5) Copiar informações para colar no GPT"
read -p "Opção (1-5): " opcao

case $opcao in
    1)
        echo "📊 Coletando informações do sistema..."
        executar "uname -a"
        executar "cat /etc/os-release"
        executar "python3 --version"
        executar "docker --version 2>/dev/null || echo 'Docker não instalado'"
        executar "postgresql --version 2>/dev/null || echo 'PostgreSQL não instalado'"
        executar "free -h"
        executar "df -h"
        executar "hostname -I"
        executar "ping -c 3 8.8.8.8 2>&1 | head -5"
        executar "nslookup google.com 2>&1 | head -5"
        echo ""
        echo "✅ Informações coletadas e salvas em: $LOG_FILE"
        echo "📋 Copie o conteúdo do log para colar no GPT:"
        echo "   cat $LOG_FILE"
        ;;
    
    2)
        read -p "Digite o comando que o GPT sugeriu: " cmd
        executar "$cmd"
        echo ""
        echo "✅ Resultado salvo em: $LOG_FILE"
        echo "📋 Copie o resultado para colar no GPT:"
        echo "   tail -50 $LOG_FILE"
        ;;
    
    3)
        if [ -f "$LOG_FILE" ]; then
            cat "$LOG_FILE"
        else
            echo "Log não encontrado. Execute opção 1 ou 2 primeiro."
        fi
        ;;
    
    4)
        rm -f /tmp/iasenior_setup_*.log
        echo "✅ Logs limpos"
        ;;
    
    5)
        echo ""
        echo "📋 INFORMAÇÕES PARA COLAR NO GPT:"
        echo "================================="
        echo ""
        echo "Servidor: $(hostname)"
        echo "IP: $(hostname -I | awk '{print $1}')"
        echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
        echo "Python: $(python3 --version 2>&1)"
        echo ""
        if [ -f "$LOG_FILE" ]; then
            echo "Últimos comandos executados:"
            tail -30 "$LOG_FILE"
        fi
        echo ""
        echo "================================="
        ;;
    
    *)
        echo "Opção inválida"
        exit 1
        ;;
esac

