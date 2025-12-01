#!/usr/bin/env python3
"""
Script Principal para Criar Dataset Completo do Sistema
Orquestra todo o processo de criação de dataset do início ao fim.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar outros scripts
sys.path.insert(0, str(Path(__file__).parent))
from coletar_dados import ColetorDados
from organizar_todos_datasets import OrganizadorDatasets


def menu_principal():
    """Exibe menu interativo."""
    print("=" * 80)
    print("📦 CRIAÇÃO DE DATASET COMPLETO - IASENIOR")
    print("=" * 80)
    print()
    print("Escolha uma opção:")
    print()
    print("1. 📚 Buscar e listar datasets públicos")
    print("2. 📸 Coletar dados do sistema (geral)")
    print("3. 🎯 Coletar dados específicos por evento")
    print("4. 🔍 Escanear fontes de dados existentes")
    print("5. 📦 Consolidar todos os datasets")
    print("6. 📊 Gerar relatório completo")
    print("7. 🚀 Pipeline completo (coletar + organizar + preparar)")
    print("0. ❌ Sair")
    print()


def executar_pipeline_completo():
    """Executa pipeline completo de criação de dataset."""
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO PIPELINE COMPLETO DE CRIAÇÃO DE DATASET")
    logger.info("=" * 80)
    
    # Passo 1: Buscar datasets públicos
    logger.info("\n📚 Passo 1: Buscando datasets públicos...")
    from buscar_datasets_publicos import BuscadorDatasetsPublicos
    buscador = BuscadorDatasetsPublicos()
    buscador.listar_datasets_disponiveis()
    buscador.gerar_lista_fontes()
    
    # Passo 2: Escanear fontes existentes
    logger.info("\n🔍 Passo 2: Escaneando fontes de dados existentes...")
    organizador = OrganizadorDatasets()
    fontes = organizador.escanear_fontes()
    
    total_existente = sum(f.get('images', 0) for f in fontes.values())
    logger.info(f"   Total de imagens encontradas: {total_existente}")
    
    if total_existente == 0:
        logger.warning("⚠️ Nenhuma imagem encontrada. Recomendamos coletar dados primeiro.")
        resposta = input("   Deseja coletar dados agora? (s/n): ")
        if resposta.lower() == 's':
            quantidade = input("   Quantos frames coletar? (padrão: 100): ")
            quantidade = int(quantidade) if quantidade.isdigit() else 100
            
            logger.info(f"\n📸 Coletando {quantidade} frames...")
            coletor = ColetorDados()
            coletor.coletar_lote(quantidade, intervalo=5.0)
            logger.info("✅ Coleta concluída!")
    
    # Passo 3: Escanear novamente após coleta
    logger.info("\n🔍 Passo 3: Re-escaneando após coleta...")
    fontes = organizador.escanear_fontes()
    
    # Passo 4: Consolidar
    logger.info("\n📦 Passo 4: Consolidando datasets...")
    stats = organizador.consolidar_datasets('todos')
    
    # Passo 5: Gerar relatório
    logger.info("\n📊 Passo 5: Gerando relatório completo...")
    relatorio = organizador.gerar_relatorio_completo()
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ PIPELINE COMPLETO FINALIZADO")
    logger.info("=" * 80)
    logger.info(f"\n📄 Relatório completo: {relatorio}")
    logger.info("\n💡 Próximos passos:")
    logger.info("   1. Anotar imagens coletadas (se necessário)")
    logger.info("   2. Executar: python datasets/preparar_dataset.py")
    logger.info("   3. Executar: python datasets/treinar_modelo.py")


def main():
    """Função principal com menu interativo."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Criador de Dataset Completo')
    parser.add_argument('--pipeline', action='store_true', help='Executar pipeline completo')
    parser.add_argument('--menu', action='store_true', help='Menu interativo')
    
    args = parser.parse_args()
    
    if args.pipeline:
        executar_pipeline_completo()
        return
    
    if args.menu or not args.pipeline:
        while True:
            menu_principal()
            escolha = input("Opção: ").strip()
            
            if escolha == '0':
                print("👋 Até logo!")
                break
            elif escolha == '1':
                from buscar_datasets_publicos import BuscadorDatasetsPublicos
                buscador = BuscadorDatasetsPublicos()
                buscador.listar_datasets_disponiveis()
                buscador.gerar_lista_fontes()
            elif escolha == '2':
                quantidade = input("Quantos frames coletar? (padrão: 100): ")
                quantidade = int(quantidade) if quantidade.isdigit() else 100
                intervalo = input("Intervalo entre coletas em segundos? (padrão: 5): ")
                intervalo = float(intervalo) if intervalo.replace('.', '').isdigit() else 5.0
                
                coletor = ColetorDados()
                coletor.coletar_lote(quantidade, intervalo)
            elif escolha == '3':
                duracao = input("Duração do monitoramento em minutos? (padrão: 60): ")
                duracao = int(duracao) if duracao.isdigit() else 60
                
                from coletar_dados_especificos import ColetorDadosEspecificos
                coletor = ColetorDadosEspecificos()
                coletor.monitorar_e_coletar(duracao_minutos=duracao)
            elif escolha == '4':
                organizador = OrganizadorDatasets()
                organizador.escanear_fontes()
            elif escolha == '5':
                organizador = OrganizadorDatasets()
                organizador.consolidar_datasets('todos')
            elif escolha == '6':
                organizador = OrganizadorDatasets()
                organizador.gerar_relatorio_completo()
            elif escolha == '7':
                executar_pipeline_completo()
            else:
                print("❌ Opção inválida!")
            
            input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()

