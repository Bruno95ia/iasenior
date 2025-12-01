# 🎯 Qual Método de Anotação Usar?

Escolha o método mais adequado para seu caso:

## ⚡ Anotação Rápida (`anotar_rapido.py`)

**Use quando:**
- ✅ Quer anotar o mais rápido possível
- ✅ Tem muitos frames para anotar
- ✅ As quedas são similares entre frames
- ✅ Quer usar atalhos de teclado

**Vantagens:**
- ⚡ Muito rápido (2-3 segundos por frame)
- 🤖 Detecção automática de pessoas
- 📋 Reutiliza última bbox automaticamente
- ⌨️ Atalhos: Setas (navegar), Espaço (próximo), Q (marcar queda)

**Como usar:**
1. Abra a interface
2. Para cada frame:
   - Se tem queda: Clique "✅ Tem Queda" (usa bbox automática)
   - Se não tem: Clique "❌ Sem Queda"
   - Ajuste bbox se necessário
3. Use setas do teclado para navegar

**Velocidade:** ~200-300 frames/hora

---

## 🤖 Anotação Inteligente (`anotar_quedas_inteligente.py`)

**Use quando:**
- ✅ Quer precisão máxima
- ✅ Quedas variam muito entre frames
- ✅ Quer sugestões automáticas de bbox
- ✅ Quer propagar anotações para frames próximos

**Vantagens:**
- 🤖 IA detecta pessoas e sugere bboxes
- ✅ Botão para usar sugestão com 1 clique
- 📋 Propagação automática (anota frames próximos)
- 🔍 Filtro para mostrar só frames com pessoas

**Como usar:**
1. Ative "Detecção automática"
2. Para cada frame:
   - Veja sugestões automáticas (amarelo)
   - Clique "Usar Sugestão" ou ajuste manualmente
   - Use "Salvar + Propagar" para anotar frames próximos
3. Desative filtro se quiser ver todos os frames

**Velocidade:** ~100-150 frames/hora (mas com mais precisão)

---

## 🎬 Anotação por Vídeo (`anotar_por_video.py`)

**Use quando:**
- ✅ Tem vídeos longos com quedas claras
- ✅ Quedas duram vários segundos
- ✅ Quer anotar muitos frames de uma vez
- ✅ Quer ver timeline visual

**Vantagens:**
- ⚡ Muito rápido para vídeos longos
- ⏱️ Marca início/fim da queda (não frame a frame)
- 📊 Timeline visual mostra todas as quedas
- 🎯 Gera anotações automaticamente para todos os frames

**Como usar:**
1. Selecione o vídeo
2. Para cada queda no vídeo:
   - Adicione intervalo: "Início" e "Fim" em segundos
   - Exemplo: Queda de 5s a 8s → adicione intervalo 5.0 - 8.0
3. Visualize na timeline
4. Clique "Salvar Todas as Anotações"

**Velocidade:** ~10-20 quedas/hora (mas cada queda = muitos frames!)

**Exemplo:**
- Vídeo de 60 segundos com 3 quedas
- Queda 1: 5s - 8s (3 segundos = ~90 frames)
- Queda 2: 25s - 27s (2 segundos = ~60 frames)
- Queda 3: 45s - 50s (5 segundos = ~150 frames)
- **Total: 3 intervalos = 300 frames anotados em minutos!**

---

## 📝 Anotação Manual (`anotar_quedas.py`)

**Use quando:**
- ✅ Quer controle total
- ✅ Prefere interface tradicional
- ✅ Não precisa de automação

**Vantagens:**
- 🎛️ Controle completo
- 📐 Ajuste fino de coordenadas
- 👁️ Preview detalhado

**Velocidade:** ~50-80 frames/hora

---

## 🎯 Recomendação

### Para começar rápido:
1. **Use Anotação por Vídeo** para marcar todas as quedas rapidamente
2. Depois use **Anotação Rápida** para ajustar frames específicos

### Para máxima precisão:
1. Use **Anotação Inteligente** com detecção automática
2. Revise frames críticos manualmente

### Para muitos vídeos:
1. **Anotação por Vídeo** é a mais eficiente
2. Anote todos os vídeos primeiro
3. Depois refine com outros métodos se necessário

---

## 💡 Dica Pro

**Workflow Recomendado:**

1. **Primeira passada** (rápida):
   ```bash
   streamlit run anotar_por_video.py
   ```
   - Marque todos os intervalos de queda
   - Salve

2. **Segunda passada** (refinamento):
   ```bash
   streamlit run anotar_rapido.py
   ```
   - Revise frames críticos
   - Ajuste bboxes se necessário
   - Use filtro para ver só frames com pessoas

3. **Treinar modelo** com dados anotados!

---

## ⚡ Atalhos de Teclado (Anotação Rápida)

- **→ ou Espaço**: Próximo frame
- **←**: Frame anterior
- **Q**: Marcar como queda
- **N**: Sem queda
- **S**: Salvar

---

**Escolha o método e comece a anotar!** 🚀

