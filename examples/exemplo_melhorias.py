"""
Exemplo de uso das melhorias implementadas no sistema IASenior.
Demonstra os novos recursos de orquestração, logging estruturado e métricas.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.orquestrador import OrquestradorAgentes
from agents.logging_estruturado import StructuredLogger


def exemplo_orquestracao():
    """Demonstra os diferentes padrões de orquestração."""
    print("=" * 60)
    print("EXEMPLO 1: Orquestração de Agentes")
    print("=" * 60)
    
    # Configurar orquestrador com novas opções
    config = {
        'padrao_orquestracao': 'paralelo',
        'max_retries': 3,
        'timeout_agente': 30.0
    }
    
    orquestrador = OrquestradorAgentes(config)
    
    if not orquestrador.inicializar_agentes():
        print("❌ Falha ao inicializar agentes")
        return
    
    pergunta = "Como melhorar a performance do sistema de detecção?"
    
    print(f"\n📝 Pergunta: {pergunta}\n")
    
    # Padrão paralelo (padrão)
    print("🔄 Processando em modo PARALELO...")
    resultado_paralelo = orquestrador.processar_pergunta(pergunta, padrao='paralelo')
    print(f"✅ {resultado_paralelo['agentes_responderam']}/{resultado_paralelo['total_agentes']} agentes responderam")
    
    # Padrão sequencial
    print("\n🔄 Processando em modo SEQUENCIAL...")
    resultado_sequencial = orquestrador.processar_pergunta(pergunta, padrao='sequencial')
    print(f"✅ {resultado_sequencial['agentes_responderam']}/{resultado_sequencial['total_agentes']} agentes responderam")
    
    # Padrão magnético
    print("\n🔄 Processando em modo MAGNÉTICO...")
    resultado_magnetico = orquestrador.processar_pergunta(pergunta, padrao='magnetico')
    print(f"✅ {resultado_magnetico['agentes_responderam']}/{resultado_magnetico['total_agentes']} agentes responderam")
    
    # Health check avançado
    print("\n🏥 Verificando saúde dos agentes...")
    health = orquestrador._verificar_saude_agentes_avancado()
    print(f"✅ Agentes saudáveis: {health['agentes_saudaveis']}")
    print(f"⚠️ Agentes degradados: {health['agentes_degradados']}")
    print(f"❌ Agentes falhando: {health['agentes_falhando']}")
    
    orquestrador.parar_todos()


def exemplo_logging_estruturado():
    """Demonstra o sistema de logging estruturado."""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Logging Estruturado")
    print("=" * 60)
    
    # Criar logger estruturado
    logger = StructuredLogger('exemplo_agente', console_output=True)
    
    # Log simples
    logger.info('Sistema iniciado', versao='1.0', ambiente='desenvolvimento')
    
    # Log de métrica
    logger.log_metric('fps', 30.5, unit='fps', modelo='yolov8n')
    logger.log_metric('latencia', 45.2, unit='ms')
    logger.log_metric('uso_memoria', 512.3, unit='MB')
    
    # Log de evento
    logger.log_event('queda_detectada', 'Queda detectada no quarto 1', 
                     localizacao='quarto_1', confianca=0.95, timestamp='2024-01-15T10:30:45')
    
    # Log de erro
    logger.error('Erro ao processar frame', frame_id='frame_123', erro='timeout')
    
    print("\n✅ Logs estruturados criados em logs/exemplo_agente_structured.jsonl")


def exemplo_visao_computacional():
    """Demonstra melhorias no agente de visão computacional."""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Agente de Visão Computacional")
    print("=" * 60)
    
    from agents.agente_visao_computacional import AgenteVisaoComputacional
    
    config = {
        'max_cache_size': 100,
        'intervalo': 60.0
    }
    
    agente = AgenteVisaoComputacional(config)
    agente.inicializar()
    
    # Coletar métricas
    print("\n📊 Coletando métricas em tempo real...")
    metricas = agente._coletar_metricas_tempo_real()
    print(f"CPU: {metricas.get('cpu_percent', 0):.1f}%")
    print(f"Memória: {metricas.get('memoria_mb', 0):.1f} MB ({metricas.get('memoria_percent', 0):.1f}%)")
    if 'fps_medio' in metricas:
        print(f"FPS médio: {metricas['fps_medio']:.2f}")
    
    # Obter sugestões de otimização
    print("\n💡 Sugestões de otimização YOLOv8:")
    sugestoes = agente.sugerir_otimizacao_yolo()
    for sugestao in sugestoes[:3]:  # Mostrar apenas 3 primeiras
        print(f"  {sugestao}")
    
    # Exemplo de cache
    print("\n💾 Testando cache de frames...")
    agente.adicionar_ao_cache('frame_001', {'deteccoes': 5, 'confianca': 0.85})
    resultado = agente.obter_do_cache('frame_001')
    if resultado:
        print(f"✅ Frame encontrado no cache: {resultado}")
    else:
        print("❌ Frame não encontrado no cache")


def exemplo_predicao_queda():
    """Demonstra melhorias no agente de predição de queda."""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Agente de Predição de Queda")
    print("=" * 60)
    
    from agents.agente_predicao_queda import AgentePredicaoQueda
    
    config = {
        'integrar_tracking': True,
        'janela_temporal': 30,
        'threshold_risco': 0.7
    }
    
    agente = AgentePredicaoQueda(config)
    agente.inicializar()
    
    # Simular alguns dados de movimento
    print("\n📊 Simulando coleta de dados...")
    for i in range(5):
        dados = agente._coletar_dados_movimento()
        if dados:
            agente.historico_posicoes.append(dados)
    
    # Analisar padrões
    if len(agente.historico_posicoes) >= 5:
        print("\n🔍 Analisando padrões temporais...")
        padroes = agente._analisar_padroes_temporais()
        print(f"Estabilidade postural: {padroes.get('estabilidade_postural', 0):.3f}")
        print(f"Velocidade de movimento: {padroes.get('velocidade_movimento', 0):.4f}")
        
        # Predizer risco
        risco = agente._predizer_risco(padroes)
        print(f"\n⚠️ Risco predito: {risco*100:.1f}%")
        print(f"Threshold: {agente.threshold_risco*100:.1f}%")
        
        if risco >= agente.threshold_risco:
            print("🚨 ALERTA: Risco acima do threshold!")
        else:
            print("✅ Risco dentro do limite aceitável")


def main():
    """Executa todos os exemplos."""
    print("\n" + "=" * 60)
    print("EXEMPLOS DE USO DAS MELHORIAS IMPLEMENTADAS")
    print("=" * 60)
    
    try:
        exemplo_logging_estruturado()
        exemplo_visao_computacional()
        exemplo_predicao_queda()
        exemplo_orquestracao()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

