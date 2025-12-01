"""
Script para listar monitores disponíveis no sistema.
Útil para configurar o MONITOR_IDX no config.py
"""

import mss
import sys
from pathlib import Path

def listar_monitores():
    """Lista todos os monitores disponíveis."""
    try:
        with mss.mss() as sct:
            print("=" * 60)
            print("📺 Monitores Disponíveis")
            print("=" * 60)
            
            for i, monitor in enumerate(sct.monitors):
                if i == 0:
                    print(f"Monitor {i} (TODOS): {monitor}")
                else:
                    width = monitor['width']
                    height = monitor['height']
                    left = monitor['left']
                    top = monitor['top']
                    print(f"\nMonitor {i}:")
                    print(f"  Resolução: {width}x{height}")
                    print(f"  Posição: ({left}, {top})")
                    print(f"  Dicionário completo: {monitor}")
            
            print("\n" + "=" * 60)
            print("💡 Use o índice do monitor desejado no config.py")
            print("   Exemplo: MONITOR_IDX = 1")
            print("=" * 60)
            
            return len(sct.monitors)
            
    except Exception as e:
        print(f"❌ Erro ao listar monitores: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    listar_monitores()
