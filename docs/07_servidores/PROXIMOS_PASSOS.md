# 🎯 Próximos Passos - Configuração dos Servidores

## ✅ Status Atual

### Server BD (PostgreSQL)
- ✅ PostgreSQL 16 configurado e funcionando
- ✅ Banco `iasenior` criado
- ✅ Usuário `iasenior` configurado
- ✅ Conexões remotas habilitadas
- ✅ Limpeza concluída (removido instalações por engano)

### Server STR (Storage)
- ✅ Estrutura de diretórios criada
- ✅ Scripts de limpeza instalados

### Server PROCESS (Inferência)
- ⏳ Aguardando configuração

### Server API (Dashboard)
- ⏳ Aguardando configuração

---

## 🚀 Próximos Passos

### 1. Configurar Server PROCESS

**IMPORTANTE**: Execute no **Server PROCESS**, não no BD!

```bash
# No Server PROCESS
curl -o /root/setup_process.sh https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/setup_server_process.sh

chmod +x /root/setup_process.sh

bash /root/setup_process.sh
```

**Durante a execução, você precisará informar**:
- IP do Server BD (PostgreSQL)
- IP do Server STR (Storage)

**Após a execução**:
```bash
# Testar manualmente
cd /opt/iasenior
source venv/bin/activate
python scripts/stream_inferencia_rtsp.py

# Se funcionar, iniciar serviço
systemctl start iasenior-inferencia
systemctl status iasenior-inferencia
```

---

### 2. Configurar Server API

Depois que o PROCESS estiver funcionando:

```bash
# No Server API
curl -o /root/setup_api.sh https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/setup_server_api.sh

chmod +x /root/setup_api.sh

bash /root/setup_api.sh
```

**Ou configurar manualmente**:

```bash
# No Server API
cd /opt/iasenior
git clone https://github.com/Bruno95ia/iasenior.git .

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install streamlit flask pandas plotly psycopg2-binary python-dotenv bcrypt

# Configurar .env
nano .env
# Adicionar:
# DB_HOST=IP_DO_SERVER_BD
# STREAM_HOST=IP_DO_SERVER_PROCESS
```

---

## 📋 Checklist de Progresso

### Server BD
- [x] PostgreSQL instalado
- [x] Banco criado
- [x] Conexões remotas configuradas
- [x] Limpeza concluída

### Server STR
- [x] Estrutura criada
- [x] Scripts instalados

### Server PROCESS
- [ ] Docker instalado
- [ ] Código baixado
- [ ] Ambiente Python configurado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Conexão BD testada
- [ ] Serviço iniciado

### Server API
- [ ] Código baixado
- [ ] Ambiente Python configurado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Conexão BD testada
- [ ] Dashboard acessível

---

## 🔗 Obter IPs dos Servidores

Execute em cada servidor:

```bash
hostname -I | awk '{print $1}'
```

**Anotar**:
- Server BD: `___________`
- Server STR: `___________`
- Server PROCESS: `___________`
- Server API: `___________`

---

## 🧪 Testes de Conexão

### Testar BD (do PROCESS ou API)

```bash
# Instalar cliente
apt-get install -y postgresql-client

# Testar
psql -h IP_DO_SERVER_BD -U iasenior -d iasenior -c "SELECT version();"
# Senha: iasenior2366
```

### Testar PROCESS (do API)

```bash
# Verificar se MJPEG está rodando
curl http://IP_DO_SERVER_PROCESS:8888/stream
```

---

## 📝 Ordem Recomendada

1. ✅ **Server BD** - Já configurado
2. ✅ **Server STR** - Já configurado
3. ⏳ **Server PROCESS** - Próximo passo
4. ⏳ **Server API** - Depois do PROCESS

---

## 🔧 Comandos Úteis

### Verificar Status dos Serviços

```bash
# No PROCESS
systemctl status iasenior-inferencia

# No API
systemctl status iasenior-dashboard
systemctl status iasenior-mjpeg
```

### Ver Logs

```bash
# No PROCESS
journalctl -u iasenior-inferencia -f

# No API
journalctl -u iasenior-dashboard -f
journalctl -u iasenior-mjpeg -f
```

### Verificar Portas

```bash
netstat -tulpn | grep -E "5432|8554|8501|8888"
```

---

## 📞 Suporte

Se algo não funcionar:

1. Verificar logs: `journalctl -u NOME_SERVICO -n 50`
2. Testar manualmente antes de iniciar serviço
3. Verificar arquivos `.env` com IPs corretos
4. Verificar conectividade entre servidores

---

**Próximo passo**: Configurar o Server PROCESS! 🚀

