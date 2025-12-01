"""
Script de Coleta de Dados para Treinamento YOLO - IASenior
Coleta frames do sistema em execução para criar dataset de treinamento.
"""

import cv2
import shutil
import json
from datetime import datetime
from pathlib import Path
import sys
import logging
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FRAME_PATH, RESULTS_DIR, FRAME_WIDTH, FRAME_HEIGHT

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diretórios
DATASETS_DIR = Path(__file__).parent
COLETADOS_DIR = DATASETS_DIR / "coletados"
COLETADOS_IMAGES_DIR = COLETADOS_DIR / "images"
COLETADOS_LABELS_DIR = COLETADOS_DIR / "labels"
COLETADOS_METADATA_DIR = COLETADOS_DIR / "metadata"

# Criar diretórios
COLETADOS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
COLETADOS_LABELS_DIR.mkdir(parents=True, exist_ok=True)
COLETADOS_METADATA_DIR.mkdir(parents=True, exist_ok=True)


class ColetorDados:
    """
    Classe para coletar dados do sistema em execução.
    Captura frames e informações para criação de dataset.
    """
    
    def __init__(self):
        self.contador_frame = 0
        self.metadados_coleta = []
        
    def coletar_frame_com_status(self, status: str = None, intervalo_segundos: int = 5) -> Optional[str]:
        """
        Coleta um frame do sistema atual.
        
        Args:
            status: Status atual do sistema (ex: 'queda', 'ok', 'banheiro')
            intervalo_segundos: Intervalo mínimo entre coletas
        
        Returns:
            Caminho do frame coletado ou None
        """
        if not Path(FRAME_PATH).exists():
            logger.warning("⚠️ Frame não disponível no momento")
            return None
        
        try:
            # Ler frame
            frame = cv2.imread(FRAME_PATH)
            if frame is None:
                logger.warning("⚠️ Erro ao ler frame")
                return None
            
            # Gerar nome único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            nome_arquivo = f"frame_{timestamp}.jpg"
            caminho_destino = COLETADOS_IMAGES_DIR / nome_arquivo
            
            # Salvar frame
            cv2.imwrite(str(caminho_destino), frame)
            
            # Salvar metadados
            metadata = {
                'nome_arquivo': nome_arquivo,
                'timestamp': datetime.now().isoformat(),
                'status_sistema': status or 'unknown',
                'resolucao': f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
                'coletado_automaticamente': True
            }
            
            metadata_path = COLETADOS_METADATA_DIR / f"{nome_arquivo.replace('.jpg', '.json')}"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.contador_frame += 1
            self.metadados_coleta.append(metadata)
            
            logger.info(f"✅ Frame coletado: {nome_arquivo} (Status: {status})")
            return str(caminho_destino)
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar frame: {e}")
            return None
    
    def coletar_lote(self, quantidade: int, intervalo: float = 5.0) -> int:
        """
        Coleta múltiplos frames.
        
        Args:
            quantidade: Número de frames a coletar
            intervalo: Intervalo entre coletas (segundos)
        
        Returns:
            Número de frames coletados
        """
        logger.info(f"📸 Iniciando coleta de {quantidade} frames...")
        
        coletados = 0
        import time
        
        for i in range(quantidade):
            # Ler status atual
            status_path = RESULTS_DIR / "status.txt"
            status = None
            if status_path.exists():
                with open(status_path, 'r') as f:
                    status = f.read().strip().lower()
            
            # Coletar frame
            frame_coletado = self.coletar_frame_com_status(status)
            if frame_coletado:
                coletados += 1
            
            if i < quantidade - 1:  # Não esperar após último frame
                time.sleep(intervalo)
        
        logger.info(f"✅ Coleta concluída: {coletados}/{quantidade} frames coletados")
        return coletados
    
    def exportar_lista_coleta(self) -> Path:
        """Exporta lista de frames coletados."""
        lista_file = COLETADOS_DIR / f"lista_coleta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(lista_file, 'w') as f:
            json.dump(self.metadados_coleta, f, indent=2, ensure_ascii=False)
        return lista_file


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coletor de Dados para Treinamento YOLO')
    parser.add_argument('--quantidade', type=int, default=10, help='Número de frames a coletar')
    parser.add_argument('--intervalo', type=float, default=5.0, help='Intervalo entre coletas (segundos)')
    parser.add_argument('--modo-continuo', action='store_true', help='Coleta contínua até interrupção')
    
    args = parser.parse_args()
    
    coletor = ColetorDados()
    
    if args.modo_continuo:
        logger.info("🔄 Modo contínuo ativado. Pressione Ctrl+C para parar.")
        import time
        try:
            while True:
                status_path = RESULTS_DIR / "status.txt"
                status = None
                if status_path.exists():
                    with open(status_path, 'r') as f:
                        status = f.read().strip().lower()
                
                coletor.coletar_frame_com_status(status)
                time.sleep(args.intervalo)
        except KeyboardInterrupt:
            logger.info("🛑 Coleta interrompida pelo usuário")
    else:
        coletor.coletar_lote(args.quantidade, args.intervalo)
    
    # Exportar lista
    lista_file = coletor.exportar_lista_coleta()
    logger.info(f"📄 Lista de coletas salva em: {lista_file}")
    logger.info(f"📊 Total de frames coletados: {coletor.contador_frame}")


if __name__ == "__main__":
    main()

