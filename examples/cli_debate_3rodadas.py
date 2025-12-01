#!/usr/bin/env python3
"""
CLI de Debate com 3 Rodadas - Sistema IASenior
Interface de linha de comando para debates colaborativos entre agentes.
"""

from colorama import Fore, Style, init
import time
import sys
import re
import os
from typing import Dict, Any, List
from agents.orquestrador import OrquestradorAgentes


def limpar_ansi(texto: str) -> str:
    """
    Remove TODOS os códigos ANSI de um texto de forma agressiva.
    
    Args:
        texto: Texto que pode conter códigos ANSI
    
    Returns:
        Texto limpo sem códigos ANSI
    """
    if not texto or not isinstance(texto, str):
        return str(texto) if texto else ""
    
    # Remove todos os padrões possíveis de códigos ANSI
    padroes = [
        r'\x1b\[[0-9;]*m',           # \x1b[32m, \x1b[0m
        r'\033\[[0-9;]*m',           # \033[0m
        r'\[[0-9;]*m',               # [32m, [0m, [36m
        r'\x1b\[[0-9;]*[A-Za-z]',    # Outros códigos ANSI
        r'\033\[[0-9;]*[A-Za-z]',    # Outros códigos ESC
        r'\[[0-9;]*[A-Za-z]',        # [32m, [0m, etc.
    ]
    
    texto_limpo = str(texto)
    for padrao in padroes:
        texto_limpo = re.sub(padrao, '', texto_limpo)
    
    return texto_limpo


def print_simples(texto: str, cor: str = Fore.WHITE) -> None:
    """
    Imprime texto colorido de forma simples e direta (sem animação).
    Remove códigos ANSI antes de aplicar nova cor.
    
    Args:
        texto: Texto a ser impresso
        cor: Cor do texto
    """
    try:
        texto_limpo = limpar_ansi(str(texto))
        print(f"{cor}{texto_limpo}{Style.RESET_ALL}")
    except:
        texto_limpo = limpar_ansi(str(texto))
        print(texto_limpo)


def color_print(texto: str, cor: str = Fore.WHITE, delay: float = 0.005) -> None:
    """
    Imprime texto colorido. Usa print simples se delay for muito pequeno.
    
    Args:
        texto: Texto a ser impresso
        cor: Cor do texto
        delay: Delay para animação (se > 0.01)
    """
    try:
        texto_limpo = limpar_ansi(str(texto))
        
        # Se delay for muito pequeno, imprimir direto (mais rápido e confiável)
        if delay < 0.01:
            print(f"{cor}{texto_limpo}{Style.RESET_ALL}")
        else:
            texto_colorido = f"{cor}{texto_limpo}{Style.RESET_ALL}"
            for char in texto_colorido:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            print()
    except:
        texto_limpo = limpar_ansi(str(texto))
        print(texto_limpo)


def print_box(texto: str, cor_borda: str = Fore.CYAN, cor_texto: str = Fore.WHITE) -> None:
    """
    Imprime texto em uma caixa bonita.
    """
    texto_limpo = limpar_ansi(str(texto))
    linhas = texto_limpo.split('\n')
    if not linhas:
        return
    
    largura = max(len(linha) for linha in linhas if linha.strip()) + 4
    
    # Topo
    print(f"{cor_borda}╔{'═' * (largura - 2)}╗{Style.RESET_ALL}")
    
    # Conteúdo
    for linha in linhas:
        linha_limpa = limpar_ansi(linha)
        espacos = max(0, largura - len(linha_limpa) - 4)
        print(f"{cor_borda}║{Style.RESET_ALL} {cor_texto}{linha_limpa}{' ' * espacos}{Style.RESET_ALL} {cor_borda}║{Style.RESET_ALL}")
    
    # Base
    print(f"{cor_borda}╚{'═' * (largura - 2)}╝{Style.RESET_ALL}")


def mostrar_cabecalho(titulo: str, cor: str = Fore.CYAN, emoji: str = "📋") -> None:
    """
    Mostra cabeçalho formatado.
    """
    titulo_limpo = limpar_ansi(str(titulo))
    largura = 72
    linha_superior = f"{cor}╔{'═' * (largura - 2)}╗{Style.RESET_ALL}"
    linha_inferior = f"{cor}╚{'═' * (largura - 2)}╝{Style.RESET_ALL}"
    titulo_formatado = f"{cor}║{Style.RESET_ALL} {emoji} {cor}{titulo_limpo.center(largura - 6)}{Style.RESET_ALL} {cor}║{Style.RESET_ALL}"
    
    print()
    print(linha_superior)
    print(titulo_formatado)
    print(linha_inferior)
    print()


def mostrar_separador(cor: str = Fore.CYAN, estilo: str = "═") -> None:
    """
    Mostra separador visual.
    """
    print(f"{cor}{estilo * 72}{Style.RESET_ALL}")


def mostrar_respostas_por_rodada(respostas: Dict[str, Any], titulo: str, cor: str) -> None:
    """
    Mostra respostas de uma rodada formatadas.
    """
    mostrar_cabecalho(titulo, cor, "💬")
    
    contador = 0
    total = len([r for r in respostas.values() if r.get('status') == 'sucesso'])
    
    for nome_agente, dados in respostas.items():
        if dados.get('status') == 'sucesso':
            contador += 1
            resposta = dados.get('resposta', 'Sem resposta')
            
            # Limpar TODOS os códigos ANSI da resposta
            resposta = limpar_ansi(resposta)
            nome_agente_limpo = limpar_ansi(nome_agente)
            
            # Emoji e nome do agente
            emoji = "🤖"
            nome_display = nome_agente_limpo.replace('_', ' ').title()
            
            if "pesquisa" in nome_agente_limpo.lower():
                emoji = "🔍"
                nome_display = "Agente de Pesquisa"
            elif "operação" in nome_agente_limpo.lower() or "operacoes" in nome_agente_limpo.lower():
                emoji = "⚙️"
                nome_display = "Agente de Operações"
            elif "visão" in nome_agente_limpo.lower() or "visao" in nome_agente_limpo.lower():
                emoji = "👁️"
                nome_display = "Agente de Visão Computacional"
            elif "segurança" in nome_agente_limpo.lower() or "seguranca" in nome_agente_limpo.lower():
                emoji = "🔒"
                nome_display = "Agente de Segurança"
            elif "performance" in nome_agente_limpo.lower():
                emoji = "⚡"
                nome_display = "Agente de Performance"
            elif "predição" in nome_agente_limpo.lower() or "predicao" in nome_agente_limpo.lower():
                emoji = "🧠"
                nome_display = "Agente de Predição de Queda"
            elif "visionário" in nome_agente_limpo.lower() or "visionario" in nome_agente_limpo.lower():
                emoji = "🎯"
                nome_display = "Mestre Visionário"
            
            # Card do agente
            mostrar_separador(Fore.MAGENTA, "─")
            print(f"\n{emoji} {Fore.MAGENTA}{Style.BRIGHT}{nome_display}{Style.RESET_ALL} [{contador}/{total}]")
            mostrar_separador(Fore.MAGENTA, "─")
            
            # Resposta formatada
            paragrafos = resposta.split('\n\n')
            for i, paragrafo in enumerate(paragrafos):
                if paragrafo.strip():
                    linhas = paragrafo.split('\n')
                    for linha in linhas:
                        if linha.strip():
                            linha_limpa = limpar_ansi(linha.strip())
                            print_simples(f"   {linha_limpa}", cor)
                    if i < len(paragrafos) - 1:
                        print()
            
            print()
            time.sleep(0.1)
            
        elif dados.get('status') == 'erro':
            nome_limpo = limpar_ansi(nome_agente)
            print_simples(f"   ⚠️  {nome_limpo}: Erro ao processar", Fore.RED)
        elif dados.get('status') == 'nao_suportado':
            nome_limpo = limpar_ansi(nome_agente)
            print_simples(f"   ⏭️  {nome_limpo}: Não suporta processamento de mensagens", Fore.YELLOW)
    
    mostrar_separador(cor, "═")


def executar_rodada(orquestrador: OrquestradorAgentes, pergunta: str, numero_rodada: int) -> Dict[str, Any]:
    """
    Executa uma rodada de debate.
    """
    # Suprimir logs completamente
    import logging
    import io
    
    root_logger = logging.getLogger()
    nivel_anterior = root_logger.level
    
    log_buffer = io.StringIO()
    handler_buffer = logging.StreamHandler(log_buffer)
    handlers_originais = root_logger.handlers[:]
    root_logger.handlers = []
    root_logger.addHandler(handler_buffer)
    root_logger.setLevel(logging.CRITICAL)
    
    # Animação simples
    for i in range(3):
        sys.stdout.write(f"\r🔄 Processando Rodada {numero_rodada}{'.' * (i + 1)}")
        sys.stdout.flush()
        time.sleep(0.15)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()
    
    try:
        resultado = orquestrador.processar_pergunta(pergunta)
        root_logger.handlers = handlers_originais
        root_logger.setLevel(nivel_anterior)
        
        # Limpar códigos ANSI das respostas
        respostas_limpas = {}
        for nome, dados in resultado.get('respostas', {}).items():
            if isinstance(dados, dict) and 'resposta' in dados:
                dados_limpo = dados.copy()
                dados_limpo['resposta'] = limpar_ansi(dados.get('resposta', ''))
                respostas_limpas[nome] = dados_limpo
            else:
                respostas_limpas[nome] = dados
        
        return respostas_limpas
    except Exception as e:
        root_logger.handlers = handlers_originais
        root_logger.setLevel(nivel_anterior)
        print_simples(f"❌ Erro na rodada {numero_rodada}: {e}", Fore.RED)
        return {}


def main():
    """Função principal do CLI de debate."""
    # Inicializar colorama
    init(autoreset=True, strip=False, convert=False)
    
    # Configurar terminal
    if 'TERM' not in os.environ:
        os.environ['TERM'] = 'xterm-256color'
    
    # Banner
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║          🤖 SISTEMA DE DEBATE - 3 RODADAS 🤖                    ║
    ║                                                                  ║
    ║          Sistema IASenior - Agentes Colaborativos               ║
    ║          Inteligência Artificial para Monitoramento             ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print_simples(banner, Fore.CYAN)
    time.sleep(0.3)
    
    try:
        # Suprimir logs
        import logging
        import io
        
        log_buffer = io.StringIO()
        handler_buffer = logging.StreamHandler(log_buffer)
        root_logger = logging.getLogger()
        handlers_originais = root_logger.handlers[:]
        root_logger.handlers = []
        root_logger.addHandler(handler_buffer)
        root_logger.setLevel(logging.CRITICAL)
        
        print_simples("\n🚀 Inicializando sistema de agentes...", Fore.BLUE)
        orquestrador = OrquestradorAgentes()
        
        # Loading
        for i in range(3):
            sys.stdout.write(f"\r⏳ Carregando agentes{'.' * (i + 1)}")
            sys.stdout.flush()
            time.sleep(0.2)
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        
        if not orquestrador.inicializar_agentes():
            root_logger.handlers = handlers_originais
            print_simples("❌ Erro ao inicializar agentes!", Fore.RED)
            sys.exit(1)
        
        root_logger.handlers = handlers_originais
        root_logger.setLevel(logging.INFO)
        
        total_agentes = len(orquestrador.agentes)
        print_simples(f"✅ {total_agentes} agentes inicializados com sucesso!\n", Fore.GREEN)
        time.sleep(0.3)
        
        # Instruções
        instrucoes = """💡 INSTRUÇÕES DE USO

   • Digite sua pergunta e pressione ENTER
   • O sistema executará 3 rodadas de debate colaborativo
   • Cada agente participará com sua perspectiva especializada
   • Digite 'sair', 'exit' ou 'quit' para encerrar"""
        
        print_box(instrucoes, Fore.CYAN, Fore.YELLOW)
        print()
        
        # Loop principal
        while True:
            try:
                mostrar_separador(Fore.CYAN, "═")
                print()
                sys.stdout.write(f"{Fore.CYAN}{Style.BRIGHT}❓ Sua Pergunta:{Style.RESET_ALL} ")
                sys.stdout.flush()
                pergunta = input().strip()
                
                if not pergunta:
                    continue
                
                if pergunta.lower() in ["sair", "exit", "quit", "q"]:
                    print_simples("\n👋 Encerrando sistema...", Fore.YELLOW)
                    break
                
                mostrar_cabecalho(f"PERGUNTA: {pergunta}", Fore.CYAN, "❓")
                time.sleep(0.2)
                
                # RODADA 1
                print_simples("\n📊 RODADA 1: Respostas Iniciais", Fore.GREEN)
                print_simples("   Cada agente responde a pergunta inicial...\n", Fore.WHITE)
                
                respostas_r1 = executar_rodada(orquestrador, pergunta, 1)
                mostrar_respostas_por_rodada(respostas_r1, "RODADA 1 - RESPOSTAS INICIAIS", Fore.GREEN)
                time.sleep(0.5)
                
                # RODADA 2
                contexto_r2 = f"Comente sobre as respostas dos outros agentes para a pergunta: '{pergunta}'. "
                contexto_r2 += "Aqui estão as respostas da rodada 1:\n\n"
                
                for nome, dados in respostas_r1.items():
                    if dados.get('status') == 'sucesso':
                        resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                        contexto_r2 += f"[{nome}]: {resposta_limpa}\n\n"
                
                print_simples("\n💬 RODADA 2: Comentários e Perspectivas", Fore.YELLOW)
                print_simples("   Cada agente comenta sobre as respostas dos outros...\n", Fore.WHITE)
                
                respostas_r2 = executar_rodada(orquestrador, contexto_r2, 2)
                mostrar_respostas_por_rodada(respostas_r2, "RODADA 2 - COMENTÁRIOS", Fore.YELLOW)
                time.sleep(0.5)
                
                # RODADA 3
                contexto_r3 = f"Considere todas as respostas e comentários até agora sobre: '{pergunta}'. "
                contexto_r3 += "Refine seu ponto de vista ou adicione uma síntese parcial.\n\n"
                contexto_r3 += "=== Respostas da Rodada 1 ===\n"
                
                for nome, dados in respostas_r1.items():
                    if dados.get('status') == 'sucesso':
                        resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                        contexto_r3 += f"[{nome}]: {resposta_limpa}\n\n"
                
                contexto_r3 += "\n=== Comentários da Rodada 2 ===\n"
                for nome, dados in respostas_r2.items():
                    if dados.get('status') == 'sucesso':
                        resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                        contexto_r3 += f"[{nome}]: {resposta_limpa}\n\n"
                
                print_simples("\n🎯 RODADA 3: Refinamento e Síntese", Fore.BLUE)
                print_simples("   Cada agente refina seu ponto considerando todo o debate...\n", Fore.WHITE)
                
                respostas_r3 = executar_rodada(orquestrador, contexto_r3, 3)
                mostrar_respostas_por_rodada(respostas_r3, "RODADA 3 - REFINAMENTO", Fore.BLUE)
                time.sleep(0.5)
                
                # CONSOLIDAÇÃO FINAL
                mostrar_cabecalho("CONSOLIDAÇÃO FINAL", Fore.MAGENTA, "📋")
                
                try:
                    # Suprimir logs
                    root_logger.handlers = []
                    root_logger.addHandler(logging.StreamHandler(io.StringIO()))
                    root_logger.setLevel(logging.CRITICAL)
                    
                    resposta_final_texto = f"=== DEBATE: {pergunta} ===\n\n"
                    
                    resposta_final_texto += "📊 RODADA 1 - Respostas Iniciais:\n\n"
                    for nome, dados in respostas_r1.items():
                        if dados.get('status') == 'sucesso':
                            resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                            resposta_final_texto += f"🤖 {nome}:\n{resposta_limpa}\n\n"
                    
                    resposta_final_texto += "\n💬 RODADA 2 - Comentários:\n\n"
                    for nome, dados in respostas_r2.items():
                        if dados.get('status') == 'sucesso':
                            resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                            resposta_final_texto += f"🤖 {nome}:\n{resposta_limpa}\n\n"
                    
                    resposta_final_texto += "\n🎯 RODADA 3 - Refinamentos:\n\n"
                    for nome, dados in respostas_r3.items():
                        if dados.get('status') == 'sucesso':
                            resposta_limpa = limpar_ansi(dados.get('resposta', ''))
                            resposta_final_texto += f"🤖 {nome}:\n{resposta_limpa}\n\n"
                    
                    resposta_final_texto += "\n" + "="*60 + "\n"
                    resposta_final_texto += f"✅ Debate completo: {len(respostas_r1)} respostas, {len(respostas_r2)} comentários, {len(respostas_r3)} refinamentos."
                    
                    root_logger.handlers = handlers_originais
                    root_logger.setLevel(logging.INFO)
                    
                    print_simples("\n📋 RESPOSTA CONSOLIDADA:\n", Fore.MAGENTA)
                    print_box(resposta_final_texto, Fore.MAGENTA, Fore.WHITE)
                    
                except Exception as e:
                    root_logger.handlers = handlers_originais
                    root_logger.setLevel(logging.INFO)
                    print_simples(f"⚠️  Erro ao gerar consolidação: {e}", Fore.YELLOW)
                    resumo = f"""📊 RESUMO DO DEBATE

   • Rodada 1: {len(respostas_r1)} respostas
   • Rodada 2: {len(respostas_r2)} comentários
   • Rodada 3: {len(respostas_r3)} refinamentos"""
                    print_box(resumo, Fore.MAGENTA, Fore.WHITE)
                
                print()
                mostrar_separador(Fore.CYAN, "═")
                print_simples("✨ Debate concluído! Digite outra pergunta ou 'sair' para encerrar.\n", Fore.CYAN)
                
            except KeyboardInterrupt:
                print_simples("\n\n⚠️  Interrompido pelo usuário (Ctrl+C)", Fore.YELLOW)
                print_simples("💡 Digite 'sair' para encerrar ou continue com outra pergunta.\n", Fore.CYAN)
                continue
            except Exception as e:
                print_simples(f"\n❌ Erro inesperado: {e}", Fore.RED)
                print_simples("💡 Tente novamente ou digite 'sair' para encerrar.\n", Fore.YELLOW)
                continue
        
        # Despedida
        despedida = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║          ✅ Sistema encerrado com sucesso! ✅                     ║
    ║                                                                  ║
    ║          👋 Obrigado por usar o Sistema de Debate IASenior!     ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
        """
        print_simples(despedida, Fore.GREEN)
        
    except KeyboardInterrupt:
        print_simples("\n\n👋 Sistema encerrado pelo usuário.", Fore.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_simples(f"\n❌ Erro crítico: {e}", Fore.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
