# 🚀 Instruções Rápidas: Publicar no GitHub

## Opção 1: Autenticar e Criar Automaticamente (Mais Fácil)

### Passo 1: Autenticar no GitHub

```bash
cd /Users/bruno/IASENIOR_FINAL
gh auth login
```

Siga as instruções:
1. Escolha "GitHub.com"
2. Escolha "HTTPS" ou "SSH"
3. Escolha "Login with a web browser"
4. Copie o código que aparecer
5. Cole no navegador quando abrir
6. Autorize o acesso

### Passo 2: Criar Repositório

```bash
./criar_repositorio_github.sh
```

Pronto! ✅

---

## Opção 2: Criar Manualmente no GitHub

### Passo 1: Criar Repositório no Site

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `iasenior`
   - **Description**: `Sistema de Monitoramento Inteligente com IA para detecção de quedas em tempo real`
   - **Public** ou **Private**
   - ⚠️ **NÃO marque** nenhuma opção adicional
3. Clique em **"Create repository"**

### Passo 2: Conectar e Fazer Push

```bash
cd /Users/bruno/IASENIOR_FINAL

# Adicionar remote (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/iasenior.git

# Fazer push
git push -u origin main
```

### Passo 3: Autenticação

Se pedir usuário/senha:
- **Usuário**: seu username do GitHub
- **Senha**: Use um **Personal Access Token**

**Para criar token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Nome: `iasenior-push`
4. Marque: `repo` (todos os sub-itens)
5. Generate token
6. **Copie o token** (só aparece uma vez!)
7. Use o token como senha

---

## ✅ Verificação

Depois do push, acesse:
```
https://github.com/SEU_USUARIO/iasenior
```

Você deve ver todos os 224 arquivos do projeto!

---

## 📊 Status Atual

- ✅ Repositório Git local criado
- ✅ 224 arquivos commitados
- ✅ 2 commits criados
- ⏳ Aguardando criação no GitHub

---

**Escolha uma das opções acima e execute!** 🚀

