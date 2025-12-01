"""
Script de Treinamento YOLO - IASenior
Treina modelo YOLO customizado com dataset preparado.
Otimizado para usar GPU (MPS no MacBook Apple Silicon).
"""

import yaml
from pathlib import Path
from ultralytics import YOLO
import sys
import logging

# Tentar importar torch para detectar GPU
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TreinadorYOLO:
    """
    Classe para treinar modelo YOLO customizado.
    """
    
    def __init__(self, dataset_yaml: Path, modelo_base: str = "yolov8n.pt", 
                 epochs: int = 100, img_size: int = 640, batch: int = 16, device: str = None):
        """
        Inicializa o treinador.
        
        Args:
            dataset_yaml: Arquivo YAML de configuração do dataset
            modelo_base: Modelo base YOLO (yolov8n.pt, yolov8s.pt, etc.)
            epochs: Número de épocas de treinamento
            img_size: Tamanho da imagem para treinamento
            batch: Tamanho do batch
            device: Device para treinamento ('cpu', 'cuda', 'mps' ou None para auto-detect)
        """
        self.dataset_yaml = Path(dataset_yaml)
        self.modelo_base = modelo_base
        self.epochs = epochs
        self.img_size = img_size
        self.batch = batch
        
        # Detectar device automaticamente se não especificado
        if device is None:
            self.device = self._detectar_device()
        else:
            self.device = device
        
        # Verificar dataset
        if not self.dataset_yaml.exists():
            raise FileNotFoundError(f"Arquivo de dataset não encontrado: {dataset_yaml}")
        
        # Carregar configuração do dataset
        with open(self.dataset_yaml, 'r') as f:
            self.config_dataset = yaml.safe_load(f)
        
        logger.info(f"📚 Dataset configurado: {self.dataset_yaml}")
        logger.info(f"🏋️ Modelo base: {self.modelo_base}")
        logger.info(f"📊 Classes: {self.config_dataset.get('nc', '?')}")
        logger.info(f"🖥️  Device: {self.device}")
    
    def _detectar_device(self) -> str:
        """
        Detecta automaticamente o melhor device disponível.
        Prioridade: CUDA > MPS (Apple Silicon) > CPU
        
        Returns:
            String do device ('cuda', 'mps' ou 'cpu')
        """
        if not TORCH_AVAILABLE:
            logger.warning("⚠️  PyTorch não disponível, usando CPU")
            return 'cpu'
        
        # Verificar CUDA (NVIDIA GPU)
        if torch.cuda.is_available():
            logger.info("✅ CUDA (NVIDIA GPU) detectada")
            return 'cuda'
        
        # Verificar MPS (Apple Silicon GPU)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("✅ MPS (Apple Silicon GPU) detectada")
            return 'mps'
        
        # Fallback para CPU
        logger.info("ℹ️  GPU não disponível, usando CPU")
        return 'cpu'
    
    def treinar(self, nome_projeto: str = "iasenior_customizado") -> Path:
        """
        Inicia treinamento do modelo.
        
        Args:
            nome_projeto: Nome do projeto de treinamento
        
        Returns:
            Caminho do modelo treinado
        """
        logger.info("🚀 Iniciando treinamento do modelo YOLO...")
        
        try:
            # Carregar modelo base
            logger.info(f"📦 Carregando modelo base: {self.modelo_base}")
            modelo = YOLO(self.modelo_base)
            
            # Treinar
            logger.info("🏋️ Iniciando treinamento...")
            logger.info(f"   Épocas: {self.epochs}")
            logger.info(f"   Tamanho imagem: {self.img_size}")
            logger.info(f"   Batch: {self.batch}")
            logger.info(f"   Device: {self.device}")
            
            # Ajustar batch size para MPS (Apple Silicon tem limitações de memória)
            batch_ajustado = self.batch
            if self.device == 'mps':
                # MPS funciona melhor com batch sizes menores
                if batch_ajustado > 32:
                    batch_ajustado = 32
                    logger.info(f"   ⚠️  Batch ajustado para {batch_ajustado} (otimização MPS)")
            
            resultados = modelo.train(
                data=str(self.dataset_yaml),
                epochs=self.epochs,
                imgsz=self.img_size,
                batch=batch_ajustado,
                device=self.device,
                name=nome_projeto,
                project='runs/train',
                patience=50,  # Early stopping
                save=True,
                verbose=True,
                plots=True,  # Gerar gráficos de métricas
                val=True  # Validar durante treinamento
            )
            
            # Caminho do melhor modelo
            modelo_treinado = Path(f"runs/train/{nome_projeto}/weights/best.pt")
            
            if modelo_treinado.exists():
                logger.info(f"✅ Treinamento concluído!")
                logger.info(f"📦 Modelo salvo em: {modelo_treinado}")
                return modelo_treinado
            else:
                logger.error("❌ Modelo treinado não encontrado")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro durante treinamento: {e}", exc_info=True)
            raise


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Treinador YOLO - IASenior')
    parser.add_argument('--dataset', type=str, default='datasets/treino/dataset.yaml',
                       help='Arquivo YAML do dataset')
    parser.add_argument('--modelo', type=str, default='yolov8n.pt',
                       choices=['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt'],
                       help='Modelo base YOLO')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Número de épocas')
    parser.add_argument('--img-size', type=int, default=640,
                       help='Tamanho da imagem')
    parser.add_argument('--batch', type=int, default=16,
                       help='Tamanho do batch')
    parser.add_argument('--device', type=str, default=None,
                       choices=['cpu', 'cuda', 'mps', None],
                       help='Device para treinamento (None = auto-detect)')
    parser.add_argument('--nome', type=str, default='iasenior_customizado',
                       help='Nome do projeto de treinamento')
    
    args = parser.parse_args()
    
    # Criar treinador
    treinador = TreinadorYOLO(
        Path(args.dataset),
        args.modelo,
        args.epochs,
        args.img_size,
        args.batch,
        args.device
    )
    
    # Treinar
    modelo_treinado = treinador.treinar(args.nome)
    
    if modelo_treinado:
        print(f"\n✅ Treinamento concluído com sucesso!")
        print(f"📦 Modelo disponível em: {modelo_treinado}")
        print(f"\n💡 Para usar o modelo treinado:")
        print(f"   - Atualize MODEL_PATH no config.py para: {modelo_treinado}")
        print(f"   - Ou use: export MODEL_PATH={modelo_treinado}")


if __name__ == "__main__":
    main()

