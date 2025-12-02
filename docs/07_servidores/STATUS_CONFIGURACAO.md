# 📊 Status da Configuração dos Servidores - IASenior

## ✅ Server BD (PostgreSQL) - CONCLUÍDO

- **Versão**: PostgreSQL 16
- **Porta**: 5432
- **Banco**: iasenior
- **Usuário**: iasenior
- **Senha**: iasenior2366
- **Conexões remotas**: ✅ Configurado
- **listen_addresses**: ✅ '*'
- **pg_hba.conf**: ✅ Regra adicionada

### IP do Servidor BD
```bash
# Execute no Server BD para obter o IP:
hostname -I | awk '{print $1}'
```

---

## ⏳ Próximos Passos

### 1. Server PROCESS (Inferência YOLO)

**Status**: Instalação concluída, precisa configurar conexões

**Ações necessárias**:
1. Obter IP do Server BD
2. Configurar arquivo `.env` com IPs corretos
3. Testar conexão com BD
4. Testar conexão com STR (storage)
5. Iniciar serviço de inferência

**Comandos**:
```bash
# No Server PROCESS
cd /opt/iasenior
nano .env

# Configurar:
# DB_HOST=IP_DO_SERVER_BD
# DB_PASSWORD=iasenior2366
# STORAGE_HOST=IP_DO_SERVER_STR

# Testar conexão BD
apt-get install -y postgresql-client
psql -h IP_DO_SERVER_BD -U iasenior -d iasenior -c "SELECT 1;"

# Testar serviço
source venv/bin/activate
python scripts/stream_inferencia_rtsp.py --help
```

---

### 2. Server API (Dashboard)

**Status**: Instalação concluída, precisa configurar conexões

**Ações necessárias**:
1. Obter IP do Server BD
2. Obter IP do Server PROCESS
3. Configurar arquivo `.env`
4. Testar conexão com BD
5. Iniciar serviços (dashboard e MJPEG)

**Comandos**:
```bash
# No Server API
cd /opt/iasenior
nano .env

# Configurar:
# DB_HOST=IP_DO_SERVER_BD
# DB_PASSWORD=iasenior2366
# STREAM_HOST=IP_DO_SERVER_PROCESS

# Testar conexão BD
apt-get install -y postgresql-client
psql -h IP_DO_SERVER_BD -U iasenior -d iasenior -c "SELECT 1;"

# Testar dashboard
source venv/bin/activate
streamlit run painel_IA/app/dashboard.py --server.port=8501
```

---

### 3. Server STR (Storage)

**Status**: Configuração concluída

**Ações necessárias**:
1. Verificar estrutura de diretórios
2. Verificar espaço disponível
3. Testar scripts de limpeza

**Comandos**:
```bash
# No Server STR
ls -la /mnt/iasenior
df -h /mnt/iasenior
iasenior-espaco
```

---

## 🔗 Obter IPs dos Servidores

Execute em cada servidor:

```bash
# Obter IP
hostname -I | awk '{print $1}'

# Ou
ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1
```

**Anotar**:
- Server BD: `___________`
- Server STR: `___________`
- Server PROCESS: `___________`
- Server API: `___________`

---

## 🧪 Testes de Conexão

### Teste BD → PROCESS/API
```bash
# No Server PROCESS ou API
psql -h IP_DO_SERVER_BD -U iasenior -d iasenior -c "SELECT version();"
# Senha: iasenior2366
```

### Teste PROCESS → BD
```bash
# No Server PROCESS
source /opt/iasenior/venv/bin/activate
python -c "
import psycopg2
conn = psycopg2.connect(
    host='IP_DO_SERVER_BD',
    database='iasenior',
    user='iasenior',
    password='iasenior2366'
)
print('✅ Conexão BD OK')
conn.close()
"
```

### Teste API → BD
```bash
# No Server API
source /opt/iasenior/venv/bin/activate
python -c "
import psycopg2
conn = psycopg2.connect(
    host='IP_DO_SERVER_BD',
    database='iasenior',
    user='iasenior',
    password='iasenior2366'
)
print('✅ Conexão BD OK')
conn.close()
"
```

---

## 📝 Checklist Final

### Server BD
- [x] PostgreSQL instalado
- [x] Banco iasenior criado
- [x] Usuário iasenior criado
- [x] Senha configurada
- [x] Conexões remotas habilitadas
- [x] listen_addresses = '*'
- [x] pg_hba.conf configurado

### Server STR
- [x] Estrutura de diretórios criada
- [x] Scripts de limpeza instalados
- [ ] Testar scripts

### Server PROCESS
- [x] Docker instalado
- [x] Python e dependências instaladas
- [x] Código baixado
- [ ] Arquivo .env configurado
- [ ] Conexão BD testada
- [ ] Serviço iniciado

### Server API
- [x] Python e dependências instaladas
- [x] Código baixado
- [ ] Arquivo .env configurado
- [ ] Conexão BD testada
- [ ] Serviços iniciados
- [ ] Dashboard acessível

---

## 🚀 Iniciar Serviços

### Server PROCESS
```bash
# Testar manualmente primeiro
cd /opt/iasenior
source venv/bin/activate
python scripts/stream_inferencia_rtsp.py

# Se funcionar, iniciar serviço
systemctl start iasenior-inferencia
systemctl status iasenior-inferencia
```

### Server API
```bash
# Testar dashboard manualmente
cd /opt/iasenior
source venv/bin/activate
streamlit run painel_IA/app/dashboard.py --server.port=8501 --server.address=0.0.0.0

# Se funcionar, iniciar serviços
systemctl start iasenior-dashboard
systemctl start iasenior-mjpeg
systemctl status iasenior-dashboard
systemctl status iasenior-mjpeg
```

---

## 📞 Suporte

Se algo não funcionar:

1. Verificar logs:
   ```bash
   journalctl -u iasenior-inferencia -n 50
   journalctl -u iasenior-dashboard -n 50
   ```

2. Verificar conectividade:
   ```bash
   ping IP_DO_SERVER_BD
   telnet IP_DO_SERVER_BD 5432
   ```

3. Verificar firewall:
   ```bash
   ufw status
   ```

---

**Última atualização**: 2025-12-02
**Status geral**: Server BD ✅ | Server STR ✅ | Server PROCESS ⏳ | Server API ⏳

