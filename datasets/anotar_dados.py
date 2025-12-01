"""
Utilitário de Anotação para YOLO - IASenior
Interface para anotar imagens manualmente no formato YOLO.
"""

import cv2
import json
import yaml
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import sys
import argparse


class AnotadorYOLO:
    """
    Classe para anotar imagens no formato YOLO.
    Formato YOLO: class_id center_x center_y width height (todos normalizados 0-1)
    """
    
    def __init__(self, imagem_path: Path, classes: Dict[int, str], arquivo_label_path: Optional[Path] = None):
        """
        Inicializa o anotador.
        
        Args:
            imagem_path: Caminho da imagem a anotar
            classes: Dicionário {id: nome_classe}
            arquivo_label_path: Caminho do arquivo de labels (opcional)
        """
        self.imagem_path = imagem_path
        self.classes = classes
        self.arquivo_label_path = arquivo_label_path or (imagem_path.parent.parent / "labels" / f"{imagem_path.stem}.txt")
        self.arquivo_label_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Carregar imagem
        self.imagem = cv2.imread(str(imagem_path))
        if self.imagem is None:
            raise ValueError(f"Não foi possível carregar imagem: {imagem_path}")
        
        self.height, self.width = self.imagem.shape[:2]
        
        # Anotações atuais
        self.anotacoes: List[Dict] = []
        self.carregar_anotacoes_existentes()
        
        # Estado da anotação
        self.desenho_ativo = False
        self.ponto_inicio = None
        self.classe_atual = 0
        self.anotacao_temporaria = None
        
        # Interface
        self.nome_janela = f"Anotador YOLO - {imagem_path.name}"
        cv2.namedWindow(self.nome_janela)
        cv2.setMouseCallback(self.nome_janela, self._callback_mouse)
    
    def carregar_anotacoes_existentes(self):
        """Carrega anotações existentes do arquivo de labels."""
        if not self.arquivo_label_path.exists():
            return
        
        try:
            with open(self.arquivo_label_path, 'r') as f:
                linhas = f.readlines()
            
            for linha in linhas:
                partes = linha.strip().split()
                if len(partes) == 5:
                    class_id = int(partes[0])
                    center_x = float(partes[1])
                    center_y = float(partes[2])
                    width = float(partes[3])
                    height = float(partes[4])
                    
                    # Converter para coordenadas absolutas
                    x_center_abs = center_x * self.width
                    y_center_abs = center_y * self.height
                    w_abs = width * self.width
                    h_abs = height * self.height
                    
                    x1 = int(x_center_abs - w_abs / 2)
                    y1 = int(y_center_abs - h_abs / 2)
                    x2 = int(x_center_abs + w_abs / 2)
                    y2 = int(y_center_abs + h_abs / 2)
                    
                    self.anotacoes.append({
                        'class_id': class_id,
                        'bbox': [x1, y1, x2, y2]
                    })
        except Exception as e:
            print(f"⚠️ Erro ao carregar anotações existentes: {e}")
    
    def _callback_mouse(self, event, x, y, flags, param):
        """Callback do mouse para desenhar bounding boxes."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.desenho_ativo = True
            self.ponto_inicio = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.desenho_ativo:
                self.anotacao_temporaria = (self.ponto_inicio, (x, y))
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.desenho_ativo:
                x1, y1 = self.ponto_inicio
                x2, y2 = x, y
                
                # Normalizar coordenadas
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                
                # Garantir dentro dos limites
                x1 = max(0, min(x1, self.width))
                x2 = max(0, min(x2, self.width))
                y1 = max(0, min(y1, self.height))
                y2 = max(0, min(y2, self.height))
                
                if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # Tamanho mínimo
                    self.anotacoes.append({
                        'class_id': self.classe_atual,
                        'bbox': [x1, y1, x2, y2]
                    })
                
                self.desenho_ativo = False
                self.anotacao_temporaria = None
    
    def _desenhar_anotacoes(self, imagem):
        """Desenha todas as anotações na imagem."""
        cores = {
            0: (0, 255, 0),      # pessoa - verde
            1: (255, 0, 0),      # pessoa_em_pe - azul
            2: (0, 0, 255),      # pessoa_caida - vermelho
            3: (255, 255, 0),    # pessoa_sentada - ciano
            4: (255, 0, 255),    # pessoa_no_banheiro - magenta
        }
        
        for anotacao in self.anotacoes:
            x1, y1, x2, y2 = anotacao['bbox']
            class_id = anotacao['class_id']
            cor = cores.get(class_id, (255, 255, 255))
            
            # Desenhar retângulo
            cv2.rectangle(imagem, (x1, y1), (x2, y2), cor, 2)
            
            # Desenhar label
            nome_classe = self.classes.get(class_id, f"Classe {class_id}")
            cv2.putText(imagem, nome_classe, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor, 2)
        
        # Desenhar anotação temporária
        if self.anotacao_temporaria:
            (x1, y1), (x2, y2) = self.anotacao_temporaria
            cor = cores.get(self.classe_atual, (255, 255, 255))
            cv2.rectangle(imagem, (x1, y1), (x2, y2), cor, 2, cv2.LINE_AA)
    
    def _desenhar_info(self, imagem):
        """Desenha informações na imagem."""
        info_texto = [
            f"Classe Atual: {self.classes.get(self.classe_atual, 'N/A')} (ID: {self.classe_atual})",
            f"Total Anotacoes: {len(self.anotacoes)}",
            "",
            "Teclas:",
            "0-4: Selecionar classe",
            "s: Salvar",
            "d: Deletar última",
            "q: Sair"
        ]
        
        y_offset = 20
        for linha in info_texto:
            cv2.putText(imagem, linha, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 20
    
    def salvar_anotacoes(self):
        """Salva anotações no formato YOLO."""
        with open(self.arquivo_label_path, 'w') as f:
            for anotacao in self.anotacoes:
                x1, y1, x2, y2 = anotacao['bbox']
                class_id = anotacao['class_id']
                
                # Calcular centro e dimensões normalizadas
                center_x = ((x1 + x2) / 2) / self.width
                center_y = ((y1 + y2) / 2) / self.height
                width = (x2 - x1) / self.width
                height = (y2 - y1) / self.height
                
                # Garantir valores entre 0 e 1
                center_x = max(0.0, min(1.0, center_x))
                center_y = max(0.0, min(1.0, center_y))
                width = max(0.0, min(1.0, width))
                height = max(0.0, min(1.0, height))
                
                f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
        
        print(f"✅ Anotações salvas em: {self.arquivo_label_path}")
    
    def anotar(self):
        """Loop principal de anotação."""
        print("\n" + "="*60)
        print("📝 ANOTADOR YOLO - IASenior")
        print("="*60)
        print(f"Imagem: {self.imagem_path.name}")
        print(f"Resolução: {self.width}x{self.height}")
        print("\nClasses disponíveis:")
        for id_classe, nome in self.classes.items():
            print(f"  {id_classe}: {nome}")
        print("\nInstruções:")
        print("  - Clique e arraste para criar bounding box")
        print("  - Teclas 0-4: Selecionar classe")
        print("  - s: Salvar anotações")
        print("  - d: Deletar última anotação")
        print("  - q: Sair e salvar")
        print("="*60 + "\n")
        
        while True:
            # Criar cópia da imagem
            imagem_display = self.imagem.copy()
            
            # Desenhar anotações e info
            self._desenhar_anotacoes(imagem_display)
            self._desenhar_info(imagem_display)
            
            # Mostrar
            cv2.imshow(self.nome_janela, imagem_display)
            
            # Aguardar tecla
            tecla = cv2.waitKey(1) & 0xFF
            
            if tecla == ord('q'):
                self.salvar_anotacoes()
                break
            elif tecla == ord('s'):
                self.salvar_anotacoes()
            elif tecla == ord('d'):
                if self.anotacoes:
                    self.anotacoes.pop()
                    print(f"🗑️ Última anotação deletada. Total: {len(self.anotacoes)}")
            elif tecla >= ord('0') and tecla <= ord('4'):
                self.classe_atual = tecla - ord('0')
                nome_classe = self.classes.get(self.classe_atual, 'N/A')
                print(f"📌 Classe selecionada: {self.classe_atual} - {nome_classe}")
        
        cv2.destroyAllWindows()


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Anotador YOLO - IASenior')
    parser.add_argument('imagem', type=str, help='Caminho da imagem a anotar')
    parser.add_argument('--classes', type=str, default='datasets/classes.yaml',
                       help='Arquivo de configuração de classes')
    
    args = parser.parse_args()
    
    # Carregar classes
    import yaml
    classes_file = Path(args.classes)
    if not classes_file.exists():
        print(f"❌ Arquivo de classes não encontrado: {classes_file}")
        return
    
    with open(classes_file, 'r') as f:
        config = yaml.safe_load(f)
    
    classes = {i: nome for i, nome in enumerate(config['names'])}
    
    # Criar anotador
    imagem_path = Path(args.imagem)
    if not imagem_path.exists():
        print(f"❌ Imagem não encontrada: {imagem_path}")
        return
    
    try:
        anotador = AnotadorYOLO(imagem_path, classes)
        anotador.anotar()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

