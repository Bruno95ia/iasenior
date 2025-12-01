"""
Exemplo de uso do Agente Mestre Visionário
Demonstra como usar o agente para consultas estratégicas, planos de ação e frameworks.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agents.agente_mestre_visionario import AgenteMestreVisionario


def exemplo_consulta_estrategia():
    """Exemplo de consulta estratégica direta."""
    print("\n" + "="*60)
    print("📊 EXEMPLO 1: Consulta Estratégica")
    print("="*60)
    
    # Criar agente
    config = {
        'intervalo': 60.0,
        'diretorio_dados': 'agents_data'
    }
    agente = AgenteMestreVisionario(config)
    agente.inicializar()
    
    # Fazer consulta
    pergunta = "Como escalar um negócio de serviços para multiplicar faturamento?"
    resposta = agente.consultar_estrategia(pergunta)
    
    print(f"\n❓ Pergunta: {pergunta}")
    print(f"\n💡 Resposta Direta:")
    print(f"   {resposta['resposta_direta']}")
    print(f"\n📋 Framework Sugerido: {resposta['framework_sugerido']}")
    print(f"\n✅ Ações Recomendadas:")
    for i, acao in enumerate(resposta['acoes_recomendadas'], 1):
        print(f"   {i}. {acao}")
    print(f"\n💭 Insights:")
    for insight in resposta['insights']:
        print(f"   • {insight}")


def exemplo_plano_acao():
    """Exemplo de criação de plano de ação."""
    print("\n" + "="*60)
    print("📋 EXEMPLO 2: Plano de Ação")
    print("="*60)
    
    agente = AgenteMestreVisionario({'diretorio_dados': 'agents_data'})
    agente.inicializar()
    
    objetivo = "Dobrar faturamento no próximo trimestre"
    plano = agente.criar_plano_acao(objetivo)
    
    print(f"\n🎯 Objetivo: {plano['objetivo']}")
    print(f"\n📊 Fases do Plano:")
    for fase in plano['fases']:
        print(f"\n   Fase {fase['fase']}: {fase['nome']}")
        print(f"   Descrição: {fase['descricao']}")
        print(f"   Entregas:")
        for entrega in fase['entregas']:
            print(f"     • {entrega}")
    
    print(f"\n📈 Métricas:")
    for metrica in plano['metricas']:
        print(f"   • {metrica}")


def exemplo_framework():
    """Exemplo de aplicação de framework estratégico."""
    print("\n" + "="*60)
    print("🔍 EXEMPLO 3: Aplicação de Framework (SWOT)")
    print("="*60)
    
    agente = AgenteMestreVisionario({'diretorio_dados': 'agents_data'})
    agente.inicializar()
    
    # Dados para análise SWOT
    dados_swot = {
        'forcas': [
            'Tecnologia de ponta em visão computacional',
            'Equipe especializada',
            'Sistema já operacional'
        ],
        'fraquezas': [
            'Dependência de recursos operacionais',
            'Escalabilidade limitada'
        ],
        'oportunidades': [
            'Mercado de IA para saúde em crescimento',
            'Demanda por soluções preventivas',
            'Parcerias estratégicas possíveis'
        ],
        'ameacas': [
            'Concorrência aumentando',
            'Mudanças regulatórias',
            'Custos de infraestrutura'
        ]
    }
    
    resultado = agente.aplicar_framework('swot', dados_swot)
    
    print(f"\n📊 Framework: {resultado['framework']}")
    print(f"   {resultado['descricao']}")
    print(f"\n✅ Forças:")
    for item in resultado['resultado']['forcas']:
        print(f"   • {item}")
    print(f"\n⚠️  Fraquezas:")
    for item in resultado['resultado']['fraquezas']:
        print(f"   • {item}")
    print(f"\n🚀 Oportunidades:")
    for item in resultado['resultado']['oportunidades']:
        print(f"   • {item}")
    print(f"\n⚠️  Ameaças:")
    for item in resultado['resultado']['ameacas']:
        print(f"   • {item}")


def exemplo_priorizacao():
    """Exemplo de matriz de priorização."""
    print("\n" + "="*60)
    print("🎯 EXEMPLO 4: Matriz de Priorização")
    print("="*60)
    
    agente = AgenteMestreVisionario({'diretorio_dados': 'agents_data'})
    agente.inicializar()
    
    dados_priorizacao = {
        'quick_wins': [
            'Otimizar configurações do modelo YOLO',
            'Melhorar dashboard de visualização'
        ],
        'projetos_estrategicos': [
            'Implementar predição proativa de quedas',
            'Criar API para integrações externas'
        ],
        'preencher_tempo': [
            'Documentação adicional',
            'Refatoração de código legado'
        ],
        'evitar': [
            'Features complexas sem validação de mercado',
            'Otimizações prematuras'
        ]
    }
    
    resultado = agente.aplicar_framework('priorizacao', dados_priorizacao)
    
    print(f"\n📊 {resultado['framework']}")
    print(f"\n⚡ Alto Impacto + Baixo Esforço (Quick Wins):")
    for item in resultado['resultado']['alto_impacto_baixo_esforco']:
        print(f"   • {item}")
    
    print(f"\n🎯 Alto Impacto + Alto Esforço (Projetos Estratégicos):")
    for item in resultado['resultado']['alto_impacto_alto_esforco']:
        print(f"   • {item}")
    
    print(f"\n⏰ Baixo Impacto + Baixo Esforço (Preencher Tempo):")
    for item in resultado['resultado']['baixo_impacto_baixo_esforco']:
        print(f"   • {item}")
    
    print(f"\n❌ Baixo Impacto + Alto Esforço (Evitar):")
    for item in resultado['resultado']['baixo_impacto_alto_esforco']:
        print(f"   • {item}")


def main():
    """Executa todos os exemplos."""
    print("\n" + "="*60)
    print("🎯 MESTRE VISIONÁRIO - Exemplos de Uso")
    print("="*60)
    
    try:
        exemplo_consulta_estrategia()
        exemplo_plano_acao()
        exemplo_framework()
        exemplo_priorizacao()
        
        print("\n" + "="*60)
        print("✅ Exemplos concluídos com sucesso!")
        print("="*60)
        print("\n💡 Dica: Use o agente em seu código para consultas estratégicas,")
        print("   criação de planos de ação e aplicação de frameworks.")
        print("\n📚 Consulte a documentação em AGENTES_ESPECIALIZADOS.md")
        print("   para mais informações sobre o Mestre Visionário.")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

