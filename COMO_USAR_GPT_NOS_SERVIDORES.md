# 🤖 Como Usar GPT/Claude nos Servidores Opus

## 🎯 Situação

Você vai ativar VPN e perder conexão comigo. Aqui estão as melhores formas de continuar recebendo ajuda nos servidores.

---

## 📋 Opção 1: Prompt Completo (Recomendado)

### Passo 1: Baixar o prompt

No servidor, execute:

```bash
# Baixar o prompt do GitHub
curl -o /tmp/prompt_iasenior.txt https://raw.githubusercontent.com/Bruno95ia/iasenior/main/PROMPT_CONFIGURACAO_SERVIDORES.md

# Ou se não tiver curl, copie manualmente do GitHub:
# https://github.com/Bruno95ia/iasenior/blob/main/PROMPT_CONFIGURACAO_SERVIDORES.md
```

### Passo 2: Usar no ChatGPT/Claude

1. Abra ChatGPT ou Claude em outra aba/janela
2. Cole o conteúdo do prompt: `cat /tmp/prompt_iasenior.txt`
3. O assistente vai guiar você passo a passo

---

## 🛠️ Opção 2: Script Helper (Mais Fácil)

### Baixar script helper

```bash
# No servidor
curl -o /usr/local/bin/iasenior-helper https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/helper_servidor.sh
chmod +x /usr/local/bin/iasenior-helper
```

### Usar o helper

```bash
iasenior-helper
```

**Opções do helper:**
1. **Coletar informações** - Coleta tudo sobre o sistema
2. **Executar comando** - Executa comando sugerido pelo GPT e salva resultado
3. **Ver log** - Mostra histórico completo
4. **Copiar informações** - Formata para colar no GPT

**Exemplo de uso:**
```bash
# 1. Coletar informações
iasenior-helper
# Escolha opção 1

# 2. Copiar resultado
cat /tmp/iasenior_setup_*.log

# 3. Colar no GPT e pedir ajuda

# 4. Quando GPT sugerir comando, executar:
iasenior-helper
# Escolha opção 2
# Cole o comando sugerido

# 5. Copiar resultado e colar de volta no GPT
```

---

## 💻 Opção 3: Terminal Split Screen

### Configuração ideal:

```
┌─────────────────┬─────────────────┐
│   Terminal SSH  │   ChatGPT Web   │
│   (Servidor)    │   (Navegador)   │
└─────────────────┴─────────────────┘
```

**Como fazer:**
1. Abra terminal SSH no servidor (lado esquerdo)
2. Abra ChatGPT/Claude no navegador (lado direito)
3. Copie e cole comandos e resultados entre as janelas

---

## 📝 Opção 4: Gravar Sessão Completa

### Usar script para gravar tudo:

```bash
# Iniciar gravação
script /tmp/iasenior_sessao_$(date +%Y%m%d_%H%M%S).log

# Agora todos os comandos e saídas serão gravados
# Execute os comandos normalmente

# Para parar gravação
exit
```

**Depois:**
- Revise o log: `cat /tmp/iasenior_sessao_*.log`
- Copie partes relevantes para o GPT
- Compartilhe comigo depois (quando voltar)

---

## 🔄 Opção 5: Workflow Recomendado

### Passo a passo completo:

```bash
# 1. No servidor, baixar helper
curl -o /usr/local/bin/iasenior-helper https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/helper_servidor.sh
chmod +x /usr/local/bin/iasenior-helper

# 2. Coletar informações iniciais
iasenior-helper
# Escolha opção 1

# 3. Abrir ChatGPT/Claude em outra janela
# 4. Colar prompt completo (do arquivo PROMPT_CONFIGURACAO_SERVIDORES.md)
# 5. Colar informações coletadas
# 6. Seguir instruções do GPT

# 7. Para cada comando sugerido:
iasenior-helper
# Escolha opção 2
# Cole o comando

# 8. Copiar resultado e colar no GPT
cat /tmp/iasenior_setup_*.log | tail -50
```

---

## 📊 Template de Mensagem para GPT

Quando estiver no servidor, comece assim:

```
Olá! Estou configurando o sistema IASenior no servidor [NOME_DO_SERVIDOR].

Informações do servidor:
[COLE AQUI AS INFORMAÇÕES DO iasenior-helper opção 1]

Problema atual:
[DESCREVA O PROBLEMA]

O que preciso:
[O QUE PRECISA FAZER AGORA]

Por favor, me dê comandos específicos, um de cada vez, e me diga como verificar se funcionou.
```

---

## 🎯 Checklist Rápido

Antes de ativar VPN:

- [ ] Baixar prompt: `PROMPT_CONFIGURACAO_SERVIDORES.md`
- [ ] Baixar helper: `scripts/helper_servidor.sh`
- [ ] Testar helper: `iasenior-helper`
- [ ] Abrir ChatGPT/Claude em outra janela
- [ ] Ter acesso ao GitHub: https://github.com/Bruno95ia/iasenior

---

## 💡 Dicas

1. **Salve tudo**: Use `script` para gravar sessões completas
2. **Copie resultados**: Sempre copie saídas de comandos para o GPT
3. **Um passo por vez**: Execute um comando, veja resultado, depois próximo
4. **Verifique sempre**: Teste se cada passo funcionou antes de continuar
5. **Documente erros**: Se algo der errado, copie a mensagem completa

---

## 🔗 Links Úteis

- **Repositório**: https://github.com/Bruno95ia/iasenior
- **Prompt completo**: https://github.com/Bruno95ia/iasenior/blob/main/PROMPT_CONFIGURACAO_SERVIDORES.md
- **Script helper**: https://github.com/Bruno95ia/iasenior/blob/main/scripts/helper_servidor.sh

---

**Boa sorte na configuração!** 🚀

Quando voltar, me mostre os logs e eu ajudo a resolver qualquer problema que aparecer.

