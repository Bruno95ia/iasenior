#!/usr/bin/env python3
"""
Script para coletar dados específicos do sistema baseado em eventos.
Coleta frames quando eventos importantes ocorrem (quedas, banheiro, etc).
"""

import cv2
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FRAME_PATH, RESULTS_DIR, RTSP_URL, FRAME_WIDTH, FRAME_HEIGHT

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

COLETADOS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
COLETADOS_LABELS_DIR.mkdir(parents=True, exist_ok=True)
COLETADOS_METADATA_DIR.mkdir(parents=True, exist_ok=True)


class ColetorDadosEspecificos:
    """
    Coleta dados específicos baseado em eventos do sistema.
    """
    
    def __init__(self):
        self.eventos_coletados = {
            'queda': [],
            'banheiro': [],
            'pessoa_em_pe': [],
            'pessoa_sentada': [],
            'normal': []
        }
        self.ultima_coleta = {}
        self.min_intervalo_eventos = 30  # segundos entre coletas do mesmo evento
        
    def ler_status_sistema(self) -> Dict[str, any]:
        """Lê status atual do sistema."""
        status_info = {
            'status': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        status_path = RESULTS_DIR / "status.txt"
        if status_path.exists():
            try:
                with open(status_path, 'r') as f:
                    status_info['status'] = f.read().strip().lower()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler status: {e}")
        
        return status_info
    
    def capturar_frame_direto(self) -> Optional[cv2.Mat]:
        """Captura frame diretamente do stream RTSP."""
        try:
            cap = cv2.VideoCapture(RTSP_URL)
            if not cap.isOpened():
                logger.warning(f"⚠️ Não foi possível abrir stream: {RTSP_URL}")
                return None
            
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                return frame
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar frame direto: {e}")
            return None
    
    def coletar_por_evento(self, evento: str, forcar: bool = False) -> Optional[str]:
        """
        Coleta frame quando evento específico ocorre.
        
        Args:
            evento: Tipo de evento ('queda', 'banheiro', 'pessoa_em_pe', etc)
            forcar: Se True, coleta mesmo se já coletou recentemente
        
        Returns:
            Caminho do frame coletado ou None
        """
        # Verificar intervalo mínimo
        if not forcar and evento in self.ultima_coleta:
            tempo_decorrido = time.time() - self.ultima_coleta[evento]
            if tempo_decorrido < self.min_intervalo_eventos:
                logger.debug(f"⏭️ Evento {evento} ignorado (coletado há {tempo_decorrido:.1f}s)")
                return None
        
        # Tentar ler frame do arquivo primeiro
        frame = None
        if Path(FRAME_PATH).exists():
            frame = cv2.imread(FRAME_PATH)
        
        # Se não conseguir, tentar capturar direto
        if frame is None:
            logger.info("📸 Tentando capturar frame diretamente do stream...")
            frame = self.capturar_frame_direto()
        
        if frame is None:
            logger.warning("⚠️ Não foi possível obter frame")
            return None
        
        # Gerar nome único com evento
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        nome_arquivo = f"{evento}_{timestamp}.jpg"
        caminho_destino = COLETADOS_IMAGES_DIR / nome_arquivo
        
        # Salvar frame
        try:
            cv2.imwrite(str(caminho_destino), frame)
            
            # Salvar metadados
            metadata = {
                'nome_arquivo': nome_arquivo,
                'evento': evento,
                'timestamp': datetime.now().isoformat(),
                'resolucao': f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
                'fonte': 'evento_especifico',
                'coletado_automaticamente': True
            }
            
            metadata_path = COLETADOS_METADATA_DIR / f"{nome_arquivo.replace('.jpg', '.json')}"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Atualizar estatísticas
            self.eventos_coletados[evento].append({
                'arquivo': nome_arquivo,
                'timestamp': metadata['timestamp']
            })
            self.ultima_coleta[evento] = time.time()
            
            logger.info(f"✅ Frame coletado para evento '{evento}': {nome_arquivo}")
            return str(caminho_destino)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar frame: {e}")
            return None
    
    def monitorar_e_coletar(self, duracao_minutos: int = 60, intervalo_verificacao: float = 5.0):
        """
        Monitora sistema e coleta frames quando eventos ocorrem.
        
        Args:
            duracao_minutos: Duração do monitoramento em minutos
            intervalo_verificacao: Intervalo entre verificações (segundos)
        """
        logger.info(f"👁️ Iniciando monitoramento por {duracao_minutos} minutos...")
        logger.info(f"   Verificando a cada {intervalo_verificacao} segundos")
        logger.info(f"   Intervalo mínimo entre coletas do mesmo evento: {self.min_intervalo_eventos}s")
        
        inicio = time.time()
        fim = inicio + (duracao_minutos * 60)
        total_coletados = 0
        
        try:
            while time.time() < fim:
                # Ler status do sistema
                status_info = self.ler_status_sistema()
                status = status_info['status']
                
                # Mapear status para eventos
                evento = None
                if 'queda' in status or 'fall' in status:
                    evento = 'queda'
                elif 'banheiro' in status or 'bathroom' in status:
                    evento = 'banheiro'
                elif 'em_pe' in status or 'standing' in status:
                    evento = 'pessoa_em_pe'
                elif 'sentada' in status or 'sitting' in status:
                    evento = 'pessoa_sentada'
                else:
                    evento = 'normal'
                
                # Coletar se evento relevante
                if evento in ['queda', 'banheiro', 'pessoa_em_pe', 'pessoa_sentada']:
                    frame_coletado = self.coletar_por_evento(evento)
                    if frame_coletado:
                        total_coletados += 1
                
                # Aguardar próximo ciclo
                time.sleep(intervalo_verificacao)
                
                # Log de progresso a cada 5 minutos
                tempo_decorrido = time.time() - inicio
                if int(tempo_decorrido) % 300 == 0:  # A cada 5 minutos
                    logger.info(f"⏱️ Progresso: {tempo_decorrido/60:.1f} min | Coletados: {total_coletados}")
        
        except KeyboardInterrupt:
            logger.info("🛑 Monitoramento interrompido pelo usuário")
        
        # Estatísticas finais
        logger.info("=" * 80)
        logger.info("📊 ESTATÍSTICAS DE COLETA")
        logger.info("=" * 80)
        for evento, coletas in self.eventos_coletados.items():
            if coletas:
                logger.info(f"   {evento}: {len(coletas)} frames")
        logger.info(f"   TOTAL: {total_coletados} frames coletados")
        
        # Salvar estatísticas
        stats_file = COLETADOS_DIR / f"estatisticas_coleta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump({
                'inicio': datetime.fromtimestamp(inicio).isoformat(),
                'fim': datetime.fromtimestamp(time.time()).isoformat(),
                'duracao_minutos': duracao_minutos,
                'total_coletados': total_coletados,
                'eventos_coletados': self.eventos_coletados
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Estatísticas salvas em: {stats_file}")
    
    def coletar_lote_balanceado(self, total_frames: int, proporcoes: Dict[str, float] = None):
        """
        Coleta lote balanceado de frames por tipo de evento.
        
        Args:
            total_frames: Total de frames a coletar
            proporcoes: Proporção por evento (ex: {'queda': 0.3, 'normal': 0.7})
        """
        if proporcoes is None:
            proporcoes = {
                'queda': 0.3,  # 30% quedas (prioridade)
                'banheiro': 0.2,  # 20% banheiro
                'pessoa_em_pe': 0.2,  # 20% em pé
                'pessoa_sentada': 0.15,  # 15% sentada
                'normal': 0.15  # 15% normal
            }
        
        logger.info(f"📊 Coletando {total_frames} frames balanceados...")
        
        frames_por_evento = {}
        for evento, proporcao in proporcoes.items():
            frames_por_evento[evento] = int(total_frames * proporcao)
            logger.info(f"   {evento}: {frames_por_evento[evento]} frames")
        
        # Coletar frames (simulado - na prática precisaria detectar eventos)
        logger.info("ℹ️ Para coleta balanceada real, execute em modo monitoramento")
        logger.info("   ou use coletar_dados.py e filtre manualmente depois")


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coletor de Dados Específicos por Evento')
    parser.add_argument('--evento', type=str, help='Tipo de evento a coletar (queda, banheiro, etc)')
    parser.add_argument('--monitorar', type=int, metavar='MINUTOS', help='Monitorar e coletar por N minutos')
    parser.add_argument('--intervalo-verificacao', type=float, default=5.0, help='Intervalo entre verificações (seg)')
    parser.add_argument('--min-intervalo', type=int, default=30, help='Intervalo mínimo entre coletas do mesmo evento (seg)')
    
    args = parser.parse_args()
    
    coletor = ColetorDadosEspecificos()
    coletor.min_intervalo_eventos = args.min_intervalo
    
    if args.monitorar:
        coletor.monitorar_e_coletar(
            duracao_minutos=args.monitorar,
            intervalo_verificacao=args.intervalo_verificacao
        )
    elif args.evento:
        coletor.coletar_por_evento(args.evento, forcar=True)
    else:
        print("=" * 80)
        print("📸 COLETOR DE DADOS ESPECÍFICOS - IASENIOR")
        print("=" * 80)
        print()
        print("Uso:")
        print("  # Coletar frame de evento específico")
        print("  python datasets/coletar_dados_especificos.py --evento queda")
        print()
        print("  # Monitorar e coletar automaticamente")
        print("  python datasets/coletar_dados_especificos.py --monitorar 60")
        print()
        print("  # Monitorar com intervalo customizado")
        print("  python datasets/coletar_dados_especificos.py --monitorar 120 --intervalo-verificacao 3")


if __name__ == "__main__":
    main()

