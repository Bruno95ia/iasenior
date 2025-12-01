"""
Script de Validação de Anotações YOLO - IASenior
Valida formato e consistência das anotações.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import argparse


class ValidadorAnotacoes:
    """Valida anotações YOLO."""
    
    def __init__(self, classes_file: Path):
        """Inicializa validador."""
        self.classes_file = Path(classes_file)
        
        with open(self.classes_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.num_classes = config['nc']
        self.classes = config['names']
    
    def validar(self, images_dir: Path, labels_dir: Path) -> Dict:
        """Valida todas as anotações."""
        images_dir = Path(images_dir)
        labels_dir = Path(labels_dir)
        
        resultados = {
            'validas': [],
            'invalidas': [],
            'sem_label': [],
            'sem_imagem': [],
            'estatisticas': {
                'total_imagens': 0,
                'total_labels': 0,
                'total_anotacoes': 0,
                'classes_distribuicao': {}
            }
        }
        
        # Verificar imagens
        imagens = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
        resultados['estatisticas']['total_imagens'] = len(imagens)
        
        for img_path in imagens:
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            if not label_path.exists():
                resultados['sem_label'].append(str(img_path.name))
                continue
            
            # Validar formato do label
            try:
                with open(label_path, 'r') as f:
                    linhas = f.readlines()
                
                valido = True
                problemas = []
                
                for i, linha in enumerate(linhas):
                    partes = linha.strip().split()
                    
                    if len(partes) != 5:
                        valido = False
                        problemas.append(f"Linha {i+1}: número incorreto de valores ({len(partes)} esperado 5)")
                        continue
                    
                    try:
                        class_id = int(partes[0])
                        coords = [float(x) for x in partes[1:5]]
                    except ValueError as e:
                        valido = False
                        problemas.append(f"Linha {i+1}: valores inválidos - {e}")
                        continue
                    
                    # Validar classe
                    if class_id < 0 or class_id >= self.num_classes:
                        valido = False
                        problemas.append(f"Linha {i+1}: class_id {class_id} fora do range [0, {self.num_classes-1}]")
                        continue
                    
                    # Validar coordenadas normalizadas
                    center_x, center_y, width, height = coords
                    
                    if not (0 <= center_x <= 1):
                        valido = False
                        problemas.append(f"Linha {i+1}: center_x fora do range [0, 1]: {center_x}")
                    
                    if not (0 <= center_y <= 1):
                        valido = False
                        problemas.append(f"Linha {i+1}: center_y fora do range [0, 1]: {center_y}")
                    
                    if not (0 <= width <= 1):
                        valido = False
                        problemas.append(f"Linha {i+1}: width fora do range [0, 1]: {width}")
                    
                    if not (0 <= height <= 1):
                        valido = False
                        problemas.append(f"Linha {i+1}: height fora do range [0, 1]: {height}")
                    
                    # Validar tamanho mínimo
                    if width < 0.01 or height < 0.01:
                        valido = False
                        problemas.append(f"Linha {i+1}: bounding box muito pequeno")
                    
                    # Contar classe
                    if class_id not in resultados['estatisticas']['classes_distribuicao']:
                        resultados['estatisticas']['classes_distribuicao'][class_id] = 0
                    resultados['estatisticas']['classes_distribuicao'][class_id] += 1
                    resultados['estatisticas']['total_anotacoes'] += 1
                
                if valido:
                    resultados['validas'].append({
                        'imagem': img_path.name,
                        'anotacoes': len(linhas)
                    })
                else:
                    resultados['invalidas'].append({
                        'imagem': img_path.name,
                        'problemas': problemas
                    })
                
                resultados['estatisticas']['total_labels'] += 1
                
            except Exception as e:
                resultados['invalidas'].append({
                    'imagem': img_path.name,
                    'erro': str(e)
                })
        
        # Verificar labels sem imagem
        labels = list(labels_dir.glob("*.txt"))
        for label_path in labels:
            img_extensions = ['.jpg', '.jpeg', '.png']
            img_exists = any((labels_dir.parent / "images" / f"{label_path.stem}{ext}").exists() 
                           for ext in img_extensions)
            
            if not img_exists:
                resultados['sem_imagem'].append(label_path.name)
        
        return resultados
    
    def gerar_relatorio(self, resultados: Dict) -> str:
        """Gera relatório de validação."""
        relatorio = ["=" * 60]
        relatorio.append("📋 RELATÓRIO DE VALIDAÇÃO DE ANOTAÇÕES - IASenior")
        relatorio.append("=" * 60)
        relatorio.append("")
        
        stats = resultados['estatisticas']
        relatorio.append("📊 Estatísticas Gerais:")
        relatorio.append(f"   Total de imagens: {stats['total_imagens']}")
        relatorio.append(f"   Total de labels: {stats['total_labels']}")
        relatorio.append(f"   Total de anotações: {stats['total_anotacoes']}")
        relatorio.append(f"   Imagens válidas: {len(resultados['validas'])}")
        relatorio.append(f"   Imagens inválidas: {len(resultados['invalidas'])}")
        relatorio.append(f"   Imagens sem label: {len(resultados['sem_label'])}")
        relatorio.append(f"   Labels sem imagem: {len(resultados['sem_imagem'])}")
        relatorio.append("")
        
        relatorio.append("📊 Distribuição de Classes:")
        for class_id in sorted(stats['classes_distribuicao'].keys()):
            count = stats['classes_distribuicao'][class_id]
            nome = self.classes[class_id] if class_id < len(self.classes) else f"Classe {class_id}"
            percentual = (count / stats['total_anotacoes'] * 100) if stats['total_anotacoes'] > 0 else 0
            relatorio.append(f"   {nome} (ID {class_id}): {count} ({percentual:.1f}%)")
        relatorio.append("")
        
        if resultados['invalidas']:
            relatorio.append("❌ Problemas Encontrados:")
            for item in resultados['invalidas'][:10]:  # Primeiros 10
                relatorio.append(f"   {item['imagem']}:")
                for problema in item.get('problemas', []):
                    relatorio.append(f"     - {problema}")
                if 'erro' in item:
                    relatorio.append(f"     - Erro: {item['erro']}")
            if len(resultados['invalidas']) > 10:
                relatorio.append(f"   ... e mais {len(resultados['invalidas']) - 10} problemas")
            relatorio.append("")
        
        relatorio.append("=" * 60)
        return "\n".join(relatorio)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Validador de Anotações YOLO - IASenior')
    parser.add_argument('--images', type=str, required=True,
                       help='Diretório com imagens')
    parser.add_argument('--labels', type=str, required=True,
                       help='Diretório com labels')
    parser.add_argument('--classes', type=str, default='datasets/classes.yaml',
                       help='Arquivo de classes')
    parser.add_argument('--salvar', action='store_true',
                       help='Salvar relatório em arquivo')
    
    args = parser.parse_args()
    
    validador = ValidadorAnotacoes(Path(args.classes))
    resultados = validador.validar(Path(args.images), Path(args.labels))
    
    relatorio = validador.gerar_relatorio(resultados)
    print(relatorio)
    
    if args.salvar:
        relatorio_file = Path(args.labels).parent / "relatorio_validacao.txt"
        with open(relatorio_file, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"\n📄 Relatório salvo em: {relatorio_file}")
    
    # Retornar código de saída baseado em resultados
    if resultados['invalidas'] or resultados['sem_label']:
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

