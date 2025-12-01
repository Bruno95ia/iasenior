# 🎯 CLI de Debate - 3 Rodadas

Interface de linha de comando para debates colaborativos entre agentes do sistema IASenior.

## 📋 Requisitos

```bash
pip install colorama
```

Ou instale todas as dependências:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

```bash
python3 cli_debate_3rodadas.py
```

## 🎨 Funcionalidades

### 3 Rodadas de Debate

1. **Rodada 1 - Respostas Iniciais**: Cada agente responde à pergunta inicial
2. **Rodada 2 - Comentários**: Cada agente comenta sobre as respostas dos outros
3. **Rodada 3 - Refinamento**: Cada agente refina seu ponto considerando todo o debate

### Recursos Visuais

- ✅ **Cores no terminal**: Verde, Amarelo, Azul, Ciano, Magenta
- ✅ **Animação de digitação**: Efeito typing caractere por caractere
- ✅ **Layout formatado**: Cabeçalhos, separadores e emojis
- ✅ **Feedback visual**: Indicadores de progresso e status

### Comandos

- Digite sua pergunta e pressione ENTER
- Digite `sair`, `exit`, `quit` ou `q` para encerrar
- Use `Ctrl+C` para interromper (não encerra o sistema)

## 📊 Exemplo de Uso

```
❓ Pergunta: Como melhorar a performance do sistema?

📊 RODADA 1: Respostas Iniciais
[Agentes respondem...]

💬 RODADA 2: Comentários e Perspectivas
[Agentes comentam...]

🎯 RODADA 3: Refinamento e Síntese
[Agentes refinam...]

📋 CONSOLIDAÇÃO FINAL
[Resposta consolidada...]
```

## 🎯 Cores Utilizadas

- 🟢 **Verde**: Respostas da Rodada 1
- 🟡 **Amarelo**: Comentários da Rodada 2
- 🔵 **Azul**: Refinamentos da Rodada 3
- 🟣 **Magenta**: Consolidação final
- 🔵 **Ciano**: Sistema e progresso
- 🔴 **Vermelho**: Erros

## 🔧 Estrutura

O CLI utiliza:
- `OrquestradorAgentes` para gerenciar agentes
- `processar_pergunta()` para cada rodada
- `resposta_final()` para consolidação
- `processar_mensagem()` de cada agente

## ⚠️ Notas

- O CLI não inicia os agentes em threads (apenas inicializa)
- Respostas são síncronas e rápidas
- Tratamento de erros robusto
- Compatível com todos os agentes do sistema

---

**Versão**: 1.0.0  
**Data**: 2025-01  
**Status**: ✅ Pronto para uso

