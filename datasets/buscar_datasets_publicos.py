#!/usr/bin/env python3
"""
Script para buscar e baixar datasets públicos relevantes para o sistema IASenior.
Foca em datasets relacionados a pessoas, quedas e detecção de posturas.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil

# Bibliotecas opcionais
try:
    import requests
    REQUESTS_DISPONIVEL = True
except ImportError:
    REQUESTS_DISPONIVEL = False

try:
    import zipfile
    ZIPFILE_DISPONIVEL = True
except ImportError:
    ZIPFILE_DISPONIVEL = False

try:
    import tarfile
    TARFILE_DISPONIVEL = True
except ImportError:
    TARFILE_DISPONIVEL = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DATASETS_DIR = Path(__file__).parent
PUBLICOS_DIR = DATASETS_DIR / "publicos"
PUBLICOS_DIR.mkdir(parents=True, exist_ok=True)


class BuscadorDatasetsPublicos:
    """
    Busca e baixa datasets públicos relevantes para treinamento.
    """
    
    def __init__(self):
        self.datasets_disponiveis = {
            'urfd': {
                'nome': 'UR Fall Detection Dataset',
                'descricao': 'Dataset específico para detecção de quedas',
                'url': 'https://sites.google.com/site/fallalarmpublic/',
                'tipo': 'queda',
                'formato': 'imagens',
                'tamanho_estimado': '500MB',
                'nota': 'Requer download manual do site'
            },
            'mupf': {
                'nome': 'Multiple People Fall Dataset',
                'descricao': 'Dataset com múltiplas pessoas e quedas',
                'url': 'https://github.com/dearhxx/Fall-Detection',
                'tipo': 'queda',
                'formato': 'video',
                'tamanho_estimado': '2GB',
                'nota': 'Dataset de vídeo, requer conversão'
            },
            'fall_detection_videos': {
                'nome': 'Fall Detection Videos',
                'descricao': 'Vídeos de quedas para extração de frames',
                'url': 'https://www.kaggle.com/datasets',
                'tipo': 'queda',
                'formato': 'video',
                'tamanho_estimado': '1GB',
                'nota': 'Kaggle requer autenticação'
            },
            'coco_person': {
                'nome': 'COCO Person Subset',
                'descricao': 'Subset do COCO contendo apenas pessoas',
                'url': 'coco',
                'tipo': 'pessoa',
                'formato': 'coco',
                'tamanho_estimado': '10GB',
                'nota': 'Dataset grande, pode filtrar apenas pessoas'
            }
        }
        
        self.downloads_realizados = []
        
    def listar_datasets_disponiveis(self) -> Dict:
        """Lista todos os datasets disponíveis."""
        logger.info("📚 Datasets Públicos Disponíveis:")
        logger.info("=" * 80)
        
        for key, info in self.datasets_disponiveis.items():
            logger.info(f"\n🔹 {info['nome']}")
            logger.info(f"   Tipo: {info['tipo']}")
            logger.info(f"   Formato: {info['formato']}")
            logger.info(f"   Tamanho: {info['tamanho_estimado']}")
            logger.info(f"   URL: {info['url']}")
            if 'nota' in info:
                logger.info(f"   ⚠️ Nota: {info['nota']}")
        
        return self.datasets_disponiveis
    
    def buscar_datasets_queda_kaggle(self) -> Optional[str]:
        """
        Busca datasets de queda no Kaggle.
        Requer autenticação do Kaggle.
        """
        try:
            import kaggle
            logger.info("🔍 Buscando datasets de queda no Kaggle...")
            
            # Lista de datasets relevantes
            datasets_kaggle = [
                'datasets/gti-upm/falldetectiondataset',
                'datasets/brianlam07/fall-detection-dataset'
            ]
            
            resultados = []
            for dataset_id in datasets_kaggle:
                try:
                    metadata = kaggle.api.dataset_list(search=dataset_id)
                    resultados.append({
                        'id': dataset_id,
                        'encontrado': len(metadata) > 0
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao buscar {dataset_id}: {e}")
            
            return resultados
            
        except ImportError:
            logger.warning("⚠️ Biblioteca kaggle não instalada. Instale com: pip install kaggle")
            logger.info("💡 Configure autenticação: https://www.kaggle.com/docs/api")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao buscar no Kaggle: {e}")
            return None
    
    def baixar_imagens_queda_exemplo(self, quantidade: int = 100) -> int:
        """
        Baixa imagens de exemplo de quedas de fontes públicas.
        Usa APIs públicas quando disponíveis.
        """
        logger.info(f"📥 Baixando {quantidade} imagens de exemplo...")
        
        # Diretório para imagens baixadas
        destino_dir = PUBLICOS_DIR / "imagens_queda_exemplo"
        destino_dir.mkdir(parents=True, exist_ok=True)
        
        # Nota: Implementação real dependeria de APIs específicas
        # Por enquanto, criamos estrutura e documentação
        
        logger.info("ℹ️ Para baixar imagens reais, você pode:")
        logger.info("   1. Usar Google Images com filtros de uso comercial")
        logger.info("   2. Usar APIs como Unsplash, Pexels (buscar 'person lying', 'fall')")
        logger.info("   3. Usar datasets acadêmicos mencionados acima")
        
        # Criar arquivo de instruções
        instrucoes_file = PUBLICOS_DIR / "INSTRUCOES_DOWNLOAD.md"
        with open(instrucoes_file, 'w') as f:
            f.write("# 📥 Instruções para Download de Datasets\n\n")
            f.write("## URLs Recomendadas\n\n")
            for key, info in self.datasets_disponiveis.items():
                f.write(f"### {info['nome']}\n")
                f.write(f"- URL: {info['url']}\n")
                f.write(f"- Tipo: {info['tipo']}\n")
                f.write(f"- Nota: {info.get('nota', 'N/A')}\n\n")
        
        logger.info(f"📄 Instruções salvas em: {instrucoes_file}")
        return 0
    
    def criar_estrutura_dataset_publico(self, nome_dataset: str) -> Path:
        """Cria estrutura de diretórios para dataset público."""
        dataset_dir = PUBLICOS_DIR / nome_dataset
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Estrutura padrão
        (dataset_dir / "images").mkdir(exist_ok=True)
        (dataset_dir / "labels").mkdir(exist_ok=True)
        (dataset_dir / "raw").mkdir(exist_ok=True)
        (dataset_dir / "metadata").mkdir(exist_ok=True)
        
        logger.info(f"✅ Estrutura criada em: {dataset_dir}")
        return dataset_dir
    
    def gerar_lista_fontes(self) -> Path:
        """Gera lista completa de fontes de datasets."""
        lista_file = PUBLICOS_DIR / "FONTES_DATASETS.md"
        
        conteudo = """# 🌐 Fontes de Datasets para IASenior

## 📚 Datasets Recomendados

### Detecção de Quedas

1. **UR Fall Detection Dataset**
   - Site: https://sites.google.com/site/fallalarmpublic/
   - Tipo: Imagens e vídeos de quedas
   - Formato: Vídeo AVI
   - Tamanho: ~500MB
   - Licença: Acadêmica

2. **Fall Detection Dataset (Kaggle)**
   - Link: https://www.kaggle.com/datasets
   - Buscar: "fall detection"
   - Requer: Conta Kaggle gratuita

3. **Multiple People Fall Dataset**
   - GitHub: https://github.com/dearhxx/Fall-Detection
   - Tipo: Vídeos de múltiplas pessoas

### Datasets de Pessoas (COCO, Pascal VOC)

1. **COCO Dataset**
   - Site: https://cocodataset.org/
   - Classe relevante: "person"
   - Tamanho: Grande (~20GB completo)
   - Licença: CC BY 4.0

2. **Pascal VOC**
   - Site: http://host.robots.ox.ac.uk/pascal/VOC/
   - Classe relevante: "person"
   - Ano recomendado: 2012

### APIs para Download

1. **Unsplash API**
   - Termos: "person lying", "person on floor", "fall"
   - API: https://unsplash.com/developers
   - Licença: Unsplash License

2. **Pexels API**
   - Termos: "person lying", "person sleeping"
   - API: https://www.pexels.com/api/
   - Licença: Pexels License

## 📝 Como Usar

1. Baixe os datasets das fontes acima
2. Extraia para `datasets/publicos/{nome_dataset}/raw/`
3. Execute `converter_dataset_publico.py` para converter para formato YOLO
4. Execute `preparar_dataset.py` para organizar

## ⚠️ Importante

- Verifique licenças dos datasets
- Respeite termos de uso
- Dê crédito aos autores originais
- Use apenas para fins de pesquisa/desenvolvimento

"""
        
        with open(lista_file, 'w') as f:
            f.write(conteudo)
        
        logger.info(f"📄 Lista de fontes salva em: {lista_file}")
        return lista_file


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Buscar Datasets Públicos')
    parser.add_argument('--listar', action='store_true', help='Listar datasets disponíveis')
    parser.add_argument('--buscar-kaggle', action='store_true', help='Buscar no Kaggle')
    parser.add_argument('--criar-estrutura', type=str, help='Nome do dataset para criar estrutura')
    
    args = parser.parse_args()
    
    buscador = BuscadorDatasetsPublicos()
    
    if args.listar:
        buscador.listar_datasets_disponiveis()
        buscador.gerar_lista_fontes()
    
    if args.buscar_kaggle:
        buscador.buscar_datasets_queda_kaggle()
    
    if args.criar_estrutura:
        buscador.criar_estrutura_dataset_publico(args.criar_estrutura)
    
    if not any([args.listar, args.buscar_kaggle, args.criar_estrutura]):
        # Modo interativo
        print("=" * 80)
        print("🔍 BUSCADOR DE DATASETS PÚBLICOS - IASENIOR")
        print("=" * 80)
        print()
        buscador.listar_datasets_disponiveis()
        print()
        print("💡 Para mais informações, execute:")
        print("   python datasets/buscar_datasets_publicos.py --listar")
        print()
        print("📄 Consulte: datasets/publicos/FONTES_DATASETS.md")


if __name__ == "__main__":
    main()

