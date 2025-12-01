# 🚀 Como Usar o CLI de Debate

## 📋 Pré-requisitos

### 1. Instalar dependências

```bash
# Instalar apenas o colorama
pip install colorama

# OU instalar todas as dependências do projeto
pip install -r requirements.txt
```

## 🎯 Executar o CLI

### Método 1: Execução direta (recomendado)

```bash
python3 cli_debate_3rodadas.py
```

### Método 2: Tornar executável

```bash
# Tornar o arquivo executável
chmod +x cli_debate_3rodadas.py

# Executar diretamente
./cli_debate_3rodadas.py
```

### Método 3: Com Python explícito

```bash
python cli_debate_3rodadas.py
```

## 💡 Como Usar

1. **Inicie o CLI**: Execute o comando acima
2. **Aguarde inicialização**: O sistema carregará todos os agentes
3. **Digite sua pergunta**: Quando aparecer o prompt `❓ Sua Pergunta:`
4. **Aguarde as 3 rodadas**: O sistema executará automaticamente:
   - Rodada 1: Respostas iniciais
   - Rodada 2: Comentários
   - Rodada 3: Refinamento
5. **Veja a consolidação final**: Resposta consolidada de todos os agentes
6. **Faça outra pergunta** ou digite `sair` para encerrar

## 🎨 Exemplo de Uso

```
❓ Sua Pergunta: Como melhorar a performance do sistema?

[O sistema executará as 3 rodadas automaticamente]

📊 RODADA 1: Respostas Iniciais
[Agentes respondem...]

💬 RODADA 2: Comentários e Perspectivas
[Agentes comentam...]

🎯 RODADA 3: Refinamento e Síntese
[Agentes refinam...]

📋 CONSOLIDAÇÃO FINAL
[Resposta consolidada...]
```

## ⌨️ Comandos

- **Digite sua pergunta**: Qualquer texto e pressione ENTER
- **Sair**: Digite `sair`, `exit`, `quit` ou `q`
- **Interromper**: Pressione `Ctrl+C` (não encerra, apenas interrompe)

## ⚠️ Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'colorama'"

```bash
pip install colorama
```

### Erro: "No module named 'agents'"

Certifique-se de estar na raiz do projeto:
```bash
cd /Users/bruno/IASENIOR_FINAL
python3 cli_debate_3rodadas.py
```

### Erro ao inicializar agentes

Verifique se todos os arquivos de agentes estão presentes no diretório `agents/`

## 📝 Notas

- O CLI funciona melhor em terminais que suportam cores ANSI
- Em alguns terminais, as cores podem não aparecer (mas o CLI ainda funciona)
- O sistema não inicia os agentes em threads (apenas inicializa para processar mensagens)

---

**Versão**: 1.0.0  
**Data**: 2025-01

