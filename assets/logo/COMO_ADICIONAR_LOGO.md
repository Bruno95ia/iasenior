# 🎨 Como Adicionar Sua Logo

## 📋 Passo a Passo

### 1. Prepare sua logo

- **Formato**: PNG (recomendado) ou JPG
- **Tamanho**: 
  - Logo principal: 200x200px ou maior (quadrada funciona melhor)
  - Com fundo transparente (PNG) para melhor integração
- **Nome do arquivo**: `logo.png` ou `logo.jpg`

### 2. Coloque o arquivo

Copie sua logo para:
```
assets/logo/logo.png
```

### 3. Pronto! 🎉

A logo aparecerá automaticamente em:
- ✅ Dashboard principal (cabeçalho e sidebar)
- ✅ Todas as interfaces de anotação
- ✅ README.md (se usar markdown com imagem)

## 🎯 Onde a Logo Aparece

### Dashboard Principal
- **Cabeçalho**: Logo centralizada acima do título
- **Sidebar**: Logo no topo da barra lateral

### Interfaces de Anotação
- **Cabeçalho**: Logo ao lado do título em cada interface

### README.md
- **Topo**: Logo centralizada no início do documento

## 🔧 Opções Avançadas

### Múltiplas Versões da Logo

Se você tiver diferentes versões, pode usar:

- `logo.png` - Versão padrão (usada em todos os lugares)
- `logo_white.png` - Versão branca (para fundos escuros)
- `logo_icon.png` - Ícone pequeno (32x32px ou 64x64px)

O sistema tentará usar a versão mais apropriada automaticamente.

### Ajustar Tamanho

Se quiser ajustar o tamanho da logo em algum lugar específico, edite o arquivo correspondente e altere o parâmetro `largura`:

```python
exibir_logo_streamlit(largura=150)  # Altere o número
```

## ❓ Problemas Comuns

### Logo não aparece?

1. Verifique se o arquivo está em `assets/logo/logo.png`
2. Verifique se o nome do arquivo está correto (case-sensitive)
3. Verifique se o formato é suportado (PNG, JPG, JPEG)

### Logo aparece muito grande/pequena?

Edite o arquivo onde a logo é exibida e ajuste o parâmetro `largura`:
- Dashboard: `painel_IA/app/dashboard.py`
- Anotações: `datasets/quedas/anotar_*.py`

### Quer usar SVG?

O sistema suporta SVG, mas para melhor compatibilidade, recomenda-se converter para PNG.

## 📝 Notas

- A logo é carregada automaticamente quando o sistema inicia
- Se a logo não for encontrada, o sistema usa um fallback com texto estilizado
- A logo é cacheada pelo Streamlit para melhor performance

