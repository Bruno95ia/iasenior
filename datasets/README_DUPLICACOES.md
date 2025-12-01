# 📋 Nota sobre Duplicações em Datasets

## ⚠️ Arquivos Duplicados Identificados

### `preparar_dataset.py`
- **Raiz**: `datasets/preparar_dataset.py` - Versão genérica com classe `PreparadorDataset`
- **Quedas**: `datasets/quedas/preparar_dataset.py` - Versão específica para pipeline de quedas

**Status**: Ambos são usados:
- O da raiz é mais genérico e pode ser usado para qualquer dataset
- O de `quedas/` é específico para o pipeline de treinamento de quedas

**Recomendação**: Manter ambos, mas considerar refatorar para que o de `quedas/` use o genérico.

### `treinar_modelo.py`
- **Raiz**: `datasets/treinar_modelo.py` - Versão genérica
- **Quedas**: `datasets/quedas/treinar_modelo.py` - Versão específica para quedas

**Status**: Similar ao caso acima.

## ✅ Estrutura Final Recomendada

```
datasets/
├── preparar_dataset.py      # Genérico (manter)
├── treinar_modelo.py         # Genérico (manter)
├── anotar_dados.py           # Genérico (manter)
├── coletar_dados.py          # Genérico (manter)
├── validar_anotacoes.py      # Genérico (manter)
├── analisar_dataset.py       # Genérico (manter)
└── quedas/                    # Pipeline específico
    ├── preparar_dataset.py   # Específico (manter)
    ├── treinar_modelo.py      # Específico (manter)
    └── ...
```

## 💡 Próximos Passos

1. **Refatorar** `quedas/preparar_dataset.py` para usar a classe genérica
2. **Documentar** diferenças entre versões genérica e específica
3. **Consolidar** se possível, mantendo flexibilidade

