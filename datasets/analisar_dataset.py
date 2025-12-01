"""
Script de Análise de Dataset - IASenior
Analisa e gera estatísticas do dataset preparado.
"""

import yaml
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List
import cv2
import numpy as np


class AnalisadorDataset:
    """Classe para analisar dataset YOLO."""
    
    def __init__(self, dataset_yaml: Path):
        """Inicializa o analisador."""
        self.dataset_yaml = Path(dataset_yaml)
        
        with open(self.dataset_yaml, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.path_base = Path(self.config['path'])
        self.classes = self.config['names']
        
    def analisar(self) -> Dict:
        """Analisa dataset completo."""
        print("🔍 Analisando dataset...")
        
        analise = {
            'configuracao': self.config,
            'estatisticas': {}
        }
        
        # Analisar cada split
        for split in ['train', 'val', 'test']:
            if split in self.config:
                print(f"\n📊 Analisando {split}...")
                stats = self._analisar_split(split)
                analise['estatisticas'][split] = stats
        
        return analise
    
    def _analisar_split(self, split: str) -> Dict:
        """Analisa um split específico."""
        images_dir = self.path_base / self.config[split] / "images"
        labels_dir = images_dir.parent.parent / "labels"
        
        if not images_dir.exists():
            return {'erro': f'Diretório não encontrado: {images_dir}'}
        
        imagens = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        
        stats = {
            'total_imagens': len(imagens),
            'classes_distribuicao': Counter(),
            'resolucoes': [],
            'anotacoes_por_imagem': [],
            'tamanho_arquivos': []
        }
        
        for img_path in imagens:
            # Ler imagem
            try:
                img = cv2.imread(str(img_path))
                if img is not None:
                    h, w = img.shape[:2]
                    stats['resolucoes'].append((w, h))
                    stats['tamanho_arquivos'].append(img_path.stat().st_size / (1024 * 1024))  # MB
            except:
                pass
            
            # Ler labels
            label_path = labels_dir / f"{img_path.stem}.txt"
            if label_path.exists():
                with open(label_path, 'r') as f:
                    linhas = f.readlines()
                
                stats['anotacoes_por_imagem'].append(len(linhas))
                
                for linha in linhas:
                    partes = linha.strip().split()
                    if len(partes) == 5:
                        class_id = int(partes[0])
                        stats['classes_distribuicao'][class_id] += 1
        
        # Calcular estatísticas
        stats['resolucoes'] = list(set(stats['resolucoes']))
        stats['resolucao_media'] = (
            int(np.mean([r[0] for r in stats['resolucoes']])),
            int(np.mean([r[1] for r in stats['resolucoes']]))
        ) if stats['resolucoes'] else None
        stats['tamanho_medio_mb'] = np.mean(stats['tamanho_arquivos']) if stats['tamanho_arquivos'] else 0
        stats['anotacoes_media'] = np.mean(stats['anotacoes_por_imagem']) if stats['anotacoes_por_imagem'] else 0
        stats['total_anotacoes'] = sum(stats['anotacoes_por_imagem'])
        
        return stats
    
    def gerar_relatorio(self, analise: Dict) -> str:
        """Gera relatório textual da análise."""
        relatorio = ["=" * 60]
        relatorio.append("📊 RELATÓRIO DE ANÁLISE DE DATASET - IASenior")
        relatorio.append("=" * 60)
        relatorio.append("")
        
        relatorio.append("📚 Configuração:")
        relatorio.append(f"   Classes: {len(self.classes)}")
        for i, nome in enumerate(self.classes):
            relatorio.append(f"     {i}: {nome}")
        relatorio.append("")
        
        for split, stats in analise['estatisticas'].items():
            if 'erro' in stats:
                continue
                
            relatorio.append(f"📁 Split: {split.upper()}")
            relatorio.append(f"   Total de imagens: {stats['total_imagens']}")
            relatorio.append(f"   Total de anotações: {stats['total_anotacoes']}")
            relatorio.append(f"   Anotações por imagem (média): {stats['anotacoes_media']:.2f}")
            relatorio.append(f"   Tamanho médio (MB): {stats['tamanho_medio_mb']:.2f}")
            if stats.get('resolucao_media'):
                relatorio.append(f"   Resolução média: {stats['resolucao_media'][0]}x{stats['resolucao_media'][1]}")
            
            relatorio.append("   Distribuição de classes:")
            for class_id, count in stats['classes_distribuicao'].most_common():
                nome_classe = self.classes[class_id] if class_id < len(self.classes) else f"Classe {class_id}"
                percentual = (count / stats['total_anotacoes'] * 100) if stats['total_anotacoes'] > 0 else 0
                relatorio.append(f"     {nome_classe}: {count} ({percentual:.1f}%)")
            
            relatorio.append("")
        
        relatorio.append("=" * 60)
        return "\n".join(relatorio)


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analisador de Dataset YOLO - IASenior')
    parser.add_argument('--dataset', type=str, default='datasets/treino/dataset.yaml',
                       help='Arquivo YAML do dataset')
    parser.add_argument('--salvar', action='store_true',
                       help='Salvar relatório em arquivo')
    
    args = parser.parse_args()
    
    analisador = AnalisadorDataset(Path(args.dataset))
    analise = analisador.analisar()
    
    relatorio = analisador.gerar_relatorio(analise)
    print(relatorio)
    
    if args.salvar:
        relatorio_file = Path(args.dataset).parent / "relatorio_analise.txt"
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"\n📄 Relatório salvo em: {relatorio_file}")
        
        # Salvar JSON também
        json_file = Path(args.dataset).parent / "analise_completa.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analise, f, indent=2, ensure_ascii=False)
        print(f"📄 Análise completa salva em: {json_file}")


if __name__ == "__main__":
    main()

