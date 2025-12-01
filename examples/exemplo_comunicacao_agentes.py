"""
Exemplo de uso da comunicação entre agentes e sistema de debate.
Demonstra como usar processar_pergunta, debate e resposta_final.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orquestrador import OrquestradorAgentes


def exemplo_processar_pergunta():
    """Exemplo de processamento simples de pergunta."""
    print("\n" + "="*60)
    print("💭 EXEMPLO 1: Processar Pergunta")
    print("="*60)
    
    # Criar e inicializar orquestrador
    orquestrador = OrquestradorAgentes()
    orquestrador.inicializar_agentes()
    
    # Fazer pergunta
    pergunta = "Como melhorar a performance do sistema de detecção?"
    resultado = orquestrador.processar_pergunta(pergunta)
    
    print(f"\n❓ Pergunta: {pergunta}")
    print(f"\n📊 Respostas de {resultado['agentes_responderam']}/{resultado['total_agentes']} agentes:\n")
    
    for nome_agente, dados in resultado['respostas'].items():
        if dados['status'] == 'sucesso':
            print(f"🤖 {nome_agente}:")
            print(f"   {dados['resposta'][:200]}...")
            print()
    
    # Consolidar resposta final
    resposta_consolidada = orquestrador.resposta_final(resultado)
    print("\n" + "="*60)
    print("📝 RESPOSTA CONSOLIDADA:")
    print("="*60)
    print(resposta_consolidada)


def exemplo_debate():
    """Exemplo de debate entre agentes."""
    print("\n" + "="*60)
    print("💬 EXEMPLO 2: Debate entre Agentes")
    print("="*60)
    
    # Criar e inicializar orquestrador
    orquestrador = OrquestradorAgentes()
    orquestrador.inicializar_agentes()
    
    # Fazer pergunta para debate
    pergunta = "Qual a melhor estratégia para escalar o sistema IASenior?"
    debate_resultado = orquestrador.debate(pergunta)
    
    print(f"\n❓ Pergunta do Debate: {pergunta}")
    print(f"\n📊 Rodada 1: {debate_resultado['rodada1']['total']} respostas")
    print(f"💬 Rodada 2: {debate_resultado['rodada2']['total']} comentários")
    
    # Consolidar resposta final do debate
    resposta_consolidada = orquestrador.resposta_final(debate_resultado)
    print("\n" + "="*60)
    print("📝 RESULTADO DO DEBATE:")
    print("="*60)
    print(resposta_consolidada)


def exemplo_pergunta_especifica():
    """Exemplo com pergunta específica sobre uma área."""
    print("\n" + "="*60)
    print("🎯 EXEMPLO 3: Pergunta Específica")
    print("="*60)
    
    orquestrador = OrquestradorAgentes()
    orquestrador.inicializar_agentes()
    
    pergunta = "Como otimizar o modelo YOLO para melhor precisão?"
    resultado = orquestrador.processar_pergunta(pergunta)
    
    print(f"\n❓ Pergunta: {pergunta}\n")
    
    # Mostrar apenas respostas relevantes
    for nome_agente, dados in resultado['respostas'].items():
        if dados['status'] == 'sucesso' and any(palavra in nome_agente.lower() for palavra in ['visao', 'pesquisa', 'performance']):
            print(f"🤖 {nome_agente}:")
            print(f"   {dados['resposta']}\n")


def main():
    """Executa todos os exemplos."""
    print("\n" + "="*60)
    print("🤖 SISTEMA DE COMUNICAÇÃO ENTRE AGENTES")
    print("="*60)
    print("\nDemonstração dos novos métodos de comunicação e debate.")
    
    try:
        exemplo_processar_pergunta()
        exemplo_debate()
        exemplo_pergunta_especifica()
        
        print("\n" + "="*60)
        print("✅ Exemplos concluídos com sucesso!")
        print("="*60)
        print("\n💡 Métodos disponíveis no OrquestradorAgentes:")
        print("   • processar_pergunta(pergunta: str) -> Dict")
        print("   • debate(pergunta: str) -> Dict")
        print("   • resposta_final(respostas: Dict) -> str")
        print("\n📚 Cada agente implementa:")
        print("   • processar_mensagem(mensagem: str) -> str")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

