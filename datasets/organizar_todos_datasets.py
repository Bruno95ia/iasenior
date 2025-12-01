#!/usr/bin/env python3
"""
Script para organizar todos os datasets coletados e prepará-los para treinamento.
Consolida dados de diferentes fontes e organiza em estrutura YOLO padronizada.
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios
DATASETS_DIR = Path(__file__).parent
COLETADOS_DIR = DATASETS_DIR / "coletados"
ANOTADOS_DIR = DATASETS_DIR / "anotados"
PUBLICOS_DIR = DATASETS_DIR / "publicos"
TREINO_DIR = DATASETS_DIR / "treino"
CONSOLIDADO_DIR = DATASETS_DIR / "consolidado"

# Criar diretórios necessários
for dir_path in [ANOTADOS_DIR, TREINO_DIR, CONSOLIDADO_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / "images").mkdir(exist_ok=True)
    (dir_path / "labels").mkdir(exist_ok=True)


class OrganizadorDatasets:
    """
    Organiza e consolida datasets de diferentes fontes.
    """
    
    def __init__(self):
        self.estatisticas = {
            'coletados': {'images': 0, 'labels': 0},
            'anotados': {'images': 0, 'labels': 0},
            'publicos': {'images': 0, 'labels': 0},
            'total': {'images': 0, 'labels': 0}
        }
        self.problemas_encontrados = []
        
    def escanear_fontes(self) -> Dict[str, Dict]:
        """Escaneia todas as fontes de dados disponíveis."""
        logger.info("🔍 Escaneando fontes de dados...")
        
        fontes = {
            'coletados': {
                'images_dir': COLETADOS_DIR / "images",
                'labels_dir': COLETADOS_DIR / "labels",
                'metadata_dir': COLETADOS_DIR / "metadata"
            },
            'anotados': {
                'images_dir': ANOTADOS_DIR / "images",
                'labels_dir': ANOTADOS_DIR / "labels"
            },
            'publicos': {
                'images_dir': PUBLICOS_DIR,
                'labels_dir': PUBLICOS_DIR
            }
        }
        
        resultados = {}
        for fonte, dirs in fontes.items():
            images_dir = dirs['images_dir']
            labels_dir = dirs.get('labels_dir', images_dir)
            
            if images_dir.exists():
                images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
                labels = list(labels_dir.glob("*.txt"))
                
                resultados[fonte] = {
                    'images': len(images),
                    'labels': len(labels),
                    'imagens_encontradas': [f.name for f in images[:10]],  # Primeiras 10
                    'labels_encontrados': [f.name for f in labels[:10]]
                }
                
                logger.info(f"   {fonte}: {len(images)} imagens, {len(labels)} labels")
            else:
                resultados[fonte] = {'images': 0, 'labels': 0}
                logger.warning(f"   {fonte}: Diretório não encontrado")
        
        return resultados
    
    def validar_par_imagem_label(self, imagem_path: Path, labels_dir: Path) -> bool:
        """Valida se existe label correspondente para imagem."""
        label_path = labels_dir / f"{imagem_path.stem}.txt"
        return label_path.exists()
    
    def consolidar_datasets(self, fonte: str = 'todos') -> Dict[str, int]:
        """
        Consolida datasets de diferentes fontes.
        
        Args:
            fonte: Fonte a consolidar ('coletados', 'anotados', 'publicos', 'todos')
        
        Returns:
            Estatísticas da consolidação
        """
        logger.info(f"📦 Consolidando datasets de: {fonte}")
        
        consolidado_images = CONSOLIDADO_DIR / "images"
        consolidado_labels = CONSOLIDADO_DIR / "labels"
        
        consolidado_images.mkdir(parents=True, exist_ok=True)
        consolidado_labels.mkdir(parents=True, exist_ok=True)
        
        estatisticas = {
            'imagens_copiadas': 0,
            'labels_copiados': 0,
            'sem_label': 0,
            'erros': 0
        }
        
        fontes_processar = []
        if fonte == 'todos':
            fontes_processar = ['coletados', 'anotados', 'publicos']
        else:
            fontes_processar = [fonte]
        
        for fonte_nome in fontes_processar:
            if fonte_nome == 'coletados':
                images_dir = COLETADOS_DIR / "images"
                labels_dir = COLETADOS_DIR / "labels"
            elif fonte_nome == 'anotados':
                images_dir = ANOTADOS_DIR / "images"
                labels_dir = ANOTADOS_DIR / "labels"
            elif fonte_nome == 'publicos':
                images_dir = PUBLICOS_DIR
                labels_dir = PUBLICOS_DIR
            else:
                continue
            
            if not images_dir.exists():
                logger.warning(f"⚠️ Diretório não encontrado: {images_dir}")
                continue
            
            logger.info(f"\n📂 Processando: {fonte_nome}")
            
            # Listar imagens
            images = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
            
            for img_path in images:
                try:
                    # Gerar nome único baseado na fonte
                    nome_arquivo = f"{fonte_nome}_{img_path.name}"
                    destino_img = consolidado_images / nome_arquivo
                    
                    # Copiar imagem
                    shutil.copy2(img_path, destino_img)
                    estatisticas['imagens_copiadas'] += 1
                    
                    # Verificar e copiar label
                    label_origem = labels_dir / f"{img_path.stem}.txt"
                    if label_origem.exists():
                        destino_label = consolidado_labels / f"{fonte_nome}_{img_path.stem}.txt"
                        shutil.copy2(label_origem, destino_label)
                        estatisticas['labels_copiados'] += 1
                    else:
                        estatisticas['sem_label'] += 1
                        logger.debug(f"⚠️ Sem label para: {img_path.name}")
                
                except Exception as e:
                    estatisticas['erros'] += 1
                    logger.error(f"❌ Erro ao processar {img_path.name}: {e}")
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 ESTATÍSTICAS DE CONSOLIDAÇÃO")
        logger.info("=" * 80)
        logger.info(f"   Imagens copiadas: {estatisticas['imagens_copiadas']}")
        logger.info(f"   Labels copiados: {estatisticas['labels_copiados']}")
        logger.info(f"   Sem label: {estatisticas['sem_label']}")
        logger.info(f"   Erros: {estatisticas['erros']}")
        
        return estatisticas
    
    def gerar_relatorio_completo(self) -> Path:
        """Gera relatório completo de todos os datasets."""
        logger.info("📄 Gerando relatório completo...")
        
        relatorio_file = DATASETS_DIR / f"RELATORIO_DATASETS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        fontes = self.escanear_fontes()
        
        conteudo = f"""# 📊 Relatório Completo de Datasets - IASenior

**Data**: {datetime.now().isoformat()}

## 📁 Fontes de Dados

"""
        
        for fonte, dados in fontes.items():
            conteudo += f"### {fonte.upper()}\n\n"
            conteudo += f"- **Imagens**: {dados.get('images', 0)}\n"
            conteudo += f"- **Labels**: {dados.get('labels', 0)}\n\n"
        
        conteudo += f"""
## 📋 Próximos Passos

1. **Anotar imagens sem label**
   - Execute: `python datasets/anotar_dados.py <imagem.jpg>`

2. **Consolidar todos os datasets**
   - Execute: `python datasets/organizar_todos_datasets.py --consolidar`

3. **Preparar para treinamento**
   - Execute: `python datasets/preparar_dataset.py`

## ⚠️ Avisos

- Imagens sem labels não serão usadas no treinamento
- Certifique-se de ter anotado todas as imagens importantes
- Balanceamento de classes é importante para bons resultados

---
**Gerado automaticamente em**: {datetime.now().isoformat()}
"""
        
        with open(relatorio_file, 'w') as f:
            f.write(conteudo)
        
        logger.info(f"✅ Relatório salvo em: {relatorio_file}")
        return relatorio_file


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organizador de Datasets')
    parser.add_argument('--escanear', action='store_true', help='Apenas escanear fontes de dados')
    parser.add_argument('--consolidar', type=str, default='todos', 
                       choices=['todos', 'coletados', 'anotados', 'publicos'],
                       help='Consolidar datasets de uma fonte específica')
    parser.add_argument('--relatorio', action='store_true', help='Gerar relatório completo')
    
    args = parser.parse_args()
    
    organizador = OrganizadorDatasets()
    
    if args.escanear or (not args.consolidar and not args.relatorio):
        # Modo padrão: escanear e mostrar relatório
        organizador.escanear_fontes()
        organizador.gerar_relatorio_completo()
    
    if args.consolidar:
        organizador.consolidar_datasets(args.consolidar)
    
    if args.relatorio:
        organizador.gerar_relatorio_completo()


if __name__ == "__main__":
    main()

