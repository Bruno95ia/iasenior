"""
Script de Preparação de Dataset YOLO - IASenior
Prepara dataset para treinamento: validação, split e organização.
"""

import shutil
import random
from pathlib import Path
from typing import List, Tuple
import yaml
import json


class PreparadorDataset:
    """
    Classe para preparar dataset YOLO para treinamento.
    Valida anotações, faz split train/val/test e organiza estrutura.
    """
    
    def __init__(self, diretorio_anotados: Path, diretorio_saida: Path, classes_file: Path):
        """
        Inicializa o preparador.
        
        Args:
            diretorio_anotados: Diretório com imagens e labels anotados
            diretorio_saida: Diretório de saída para treino/val/test
            classes_file: Arquivo de configuração de classes
        """
        self.diretorio_anotados = Path(diretorio_anotados)
        self.diretorio_saida = Path(diretorio_saida)
        self.classes_file = Path(classes_file)
        
        # Carregar classes
        with open(self.classes_file, 'r') as f:
            self.config_classes = yaml.safe_load(f)
        
        self.classes = {i: nome for i, nome in enumerate(self.config_classes['names'])}
        
        # Diretórios de saída
        self.dir_treino = self.diretorio_saida / "treino"
        self.dir_validacao = self.diretorio_saida / "validacao"
        self.dir_teste = self.diretorio_saida / "teste"
        
        # Criar estrutura
        for dir_out in [self.dir_treino, self.dir_validacao, self.dir_teste]:
            (dir_out / "images").mkdir(parents=True, exist_ok=True)
            (dir_out / "labels").mkdir(parents=True, exist_ok=True)
    
    def validar_anotacoes(self) -> Tuple[List[Path], List[Path]]:
        """
        Valida anotações e retorna listas de válidas e inválidas.
        
        Returns:
            (anotacoes_validas, anotacoes_invalidas)
        """
        imagens_dir = self.diretorio_anotados / "images"
        labels_dir = self.diretorio_anotados / "labels"
        
        if not imagens_dir.exists() or not labels_dir.exists():
            print("❌ Diretórios images/ ou labels/ não encontrados")
            return [], []
        
        imagens = list(imagens_dir.glob("*.jpg")) + list(imagens_dir.glob("*.png"))
        validas = []
        invalidas = []
        
        for img_path in imagens:
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            # Verificar se imagem existe e é válida
            try:
                import cv2
                img = cv2.imread(str(img_path))
                if img is None:
                    invalidas.append(img_path)
                    continue
            except Exception as e:
                invalidas.append(img_path)
                continue
            
            # Verificar se label existe
            if not label_path.exists():
                invalidas.append(img_path)
                continue
            
            # Validar formato do label
            try:
                with open(label_path, 'r') as f:
                    linhas = f.readlines()
                
                valido = True
                for linha in linhas:
                    partes = linha.strip().split()
                    if len(partes) != 5:
                        valido = False
                        break
                    
                    class_id = int(partes[0])
                    coords = [float(x) for x in partes[1:5]]
                    
                    # Verificar classe válida
                    if class_id < 0 or class_id >= len(self.classes):
                        valido = False
                        break
                    
                    # Verificar coordenadas normalizadas (0-1)
                    if any(c < 0 or c > 1 for c in coords):
                        valido = False
                        break
                
                if valido:
                    validas.append(img_path)
                else:
                    invalidas.append(img_path)
            except Exception as e:
                invalidas.append(img_path)
        
        return validas, invalidas
    
    def dividir_dataset(self, imagens_validas: List[Path], 
                       proporcao_treino: float = 0.7,
                       proporcao_validacao: float = 0.2,
                       proporcao_teste: float = 0.1,
                       seed: int = 42) -> Tuple[List[Path], List[Path], List[Path]]:
        """
        Divide dataset em treino, validação e teste.
        
        Args:
            imagens_validas: Lista de imagens válidas
            proporcao_treino: Proporção para treino (padrão: 0.7)
            proporcao_validacao: Proporção para validação (padrão: 0.2)
            proporcao_teste: Proporção para teste (padrão: 0.1)
            seed: Seed para randomização
        
        Returns:
            (treino, validacao, teste)
        """
        # Validar proporções
        total = proporcao_treino + proporcao_validacao + proporcao_teste
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Proporções devem somar 1.0, soma atual: {total}")
        
        # Embaralhar
        random.seed(seed)
        imagens_embaralhadas = imagens_validas.copy()
        random.shuffle(imagens_embaralhadas)
        
        # Calcular tamanhos
        total_imagens = len(imagens_embaralhadas)
        n_treino = int(total_imagens * proporcao_treino)
        n_validacao = int(total_imagens * proporcao_validacao)
        
        # Dividir
        treino = imagens_embaralhadas[:n_treino]
        validacao = imagens_embaralhadas[n_treino:n_treino + n_validacao]
        teste = imagens_embaralhadas[n_treino + n_validacao:]
        
        return treino, validacao, teste
    
    def copiar_para_saida(self, imagens: List[Path], diretorio_destino: Path):
        """
        Copia imagens e labels para diretório de saída.
        
        Args:
            imagens: Lista de imagens a copiar
            diretorio_destino: Diretório de destino
        """
        images_dir = diretorio_destino / "images"
        labels_dir = diretorio_destino / "labels"
        labels_origem = self.diretorio_anotados / "labels"
        
        for img_path in imagens:
            # Copiar imagem
            shutil.copy2(img_path, images_dir / img_path.name)
            
            # Copiar label
            label_path = labels_origem / f"{img_path.stem}.txt"
            if label_path.exists():
                shutil.copy2(label_path, labels_dir / label_path.name)
    
    def preparar(self, proporcao_treino: float = 0.7,
                 proporcao_validacao: float = 0.2,
                 proporcao_teste: float = 0.1,
                 seed: int = 42) -> dict:
        """
        Prepara dataset completo.
        
        Returns:
            Dicionário com estatísticas do dataset
        """
        print("🔍 Validando anotações...")
        validas, invalidas = self.validar_anotacoes()
        
        print(f"✅ Anotações válidas: {len(validas)}")
        if invalidas:
            print(f"⚠️ Anotações inválidas: {len(invalidas)}")
            print(f"   Primeiras 5 inválidas: {[str(p.name) for p in invalidas[:5]]}")
        
        if len(validas) == 0:
            print("❌ Nenhuma anotação válida encontrada!")
            return {}
        
        print("\n📊 Dividindo dataset...")
        treino, validacao, teste = self.dividir_dataset(
            validas, proporcao_treino, proporcao_validacao, proporcao_teste, seed
        )
        
        print(f"   Treino: {len(treino)} imagens")
        print(f"   Validação: {len(validacao)} imagens")
        print(f"   Teste: {len(teste)} imagens")
        
        print("\n📁 Copiando arquivos...")
        self.copiar_para_saida(treino, self.dir_treino)
        print(f"   ✅ Treino copiado")
        
        self.copiar_para_saida(validacao, self.dir_validacao)
        print(f"   ✅ Validação copiada")
        
        self.copiar_para_saida(teste, self.dir_teste)
        print(f"   ✅ Teste copiado")
        
        # Copiar arquivo de classes
        shutil.copy2(self.classes_file, self.diretorio_saida / "classes.yaml")
        
        # Criar arquivo de configuração YOLO
        self._criar_config_yolo()
        
        # Gerar estatísticas
        estatisticas = self._gerar_estatisticas(treino, validacao, teste)
        
        print("\n✅ Dataset preparado com sucesso!")
        return estatisticas
    
    def _criar_config_yolo(self):
        """Cria arquivo de configuração para YOLO."""
        config = {
            'path': str(self.diretorio_saida.absolute()),
            'train': 'treino/images',
            'val': 'validacao/images',
            'test': 'teste/images',
            'nc': len(self.classes),
            'names': list(self.classes.values())
        }
        
        config_file = self.diretorio_saida / "dataset.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"📄 Configuração YOLO salva em: {config_file}")
    
    def _gerar_estatisticas(self, treino: List[Path], validacao: List[Path], teste: List[Path]) -> dict:
        """Gera estatísticas do dataset."""
        from collections import Counter
        
        def contar_classes(imagens: List[Path]) -> dict:
            contador = Counter()
            labels_dir = self.diretorio_anotados / "labels"
            
            for img in imagens:
                label_path = labels_dir / f"{img.stem}.txt"
                if label_path.exists():
                    with open(label_path, 'r') as f:
                        for linha in f:
                            class_id = int(linha.strip().split()[0])
                            contador[class_id] += 1
            
            return dict(contador)
        
        stats = {
            'total_imagens': len(treino) + len(validacao) + len(teste),
            'treino': {
                'imagens': len(treino),
                'classes': contar_classes(treino)
            },
            'validacao': {
                'imagens': len(validacao),
                'classes': contar_classes(validacao)
            },
            'teste': {
                'imagens': len(teste),
                'classes': contar_classes(teste)
            }
        }
        
        # Salvar estatísticas
        stats_file = self.diretorio_saida / "estatisticas.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Estatísticas salvas em: {stats_file}")
        return stats


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Preparador de Dataset YOLO - IASenior')
    parser.add_argument('--anotados', type=str, default='datasets/anotados',
                       help='Diretório com imagens anotadas')
    parser.add_argument('--saida', type=str, default='datasets/treino',
                       help='Diretório de saída para dataset preparado')
    parser.add_argument('--classes', type=str, default='datasets/classes.yaml',
                       help='Arquivo de classes')
    parser.add_argument('--treino', type=float, default=0.7,
                       help='Proporção para treino (padrão: 0.7)')
    parser.add_argument('--validacao', type=float, default=0.2,
                       help='Proporção para validação (padrão: 0.2)')
    parser.add_argument('--teste', type=float, default=0.1,
                       help='Proporção para teste (padrão: 0.1)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Seed para randomização (padrão: 42)')
    
    args = parser.parse_args()
    
    # Criar preparador
    preparador = PreparadorDataset(
        Path(args.anotados),
        Path(args.saida),
        Path(args.classes)
    )
    
    # Preparar dataset
    estatisticas = preparador.preparar(
        proporcao_treino=args.treino,
        proporcao_validacao=args.validacao,
        proporcao_teste=args.teste,
        seed=args.seed
    )
    
    if estatisticas:
        print("\n📈 Resumo do Dataset:")
        print(f"   Total: {estatisticas['total_imagens']} imagens")
        print(f"   Treino: {estatisticas['treino']['imagens']}")
        print(f"   Validação: {estatisticas['validacao']['imagens']}")
        print(f"   Teste: {estatisticas['teste']['imagens']}")


if __name__ == "__main__":
    main()

