# 🔧 Corrigir: Script Executado no Server BD por Engano

## ⚠️ Situação

O script de configuração do Server PROCESS foi executado no Server BD por engano.

## 🔍 O que Pode Ter Sido Instalado

1. **Código do IASenior** em `/opt/iasenior`
2. **Docker** (não necessário no BD)
3. **Ambiente virtual Python** em `/opt/iasenior/venv`
4. **MediaMTX** em `/opt/mediamtx`
5. **Serviço systemd** `iasenior-inferencia`
6. **FFmpeg** (não necessário no BD)

## ✅ O que NÃO Foi Afetado

- **PostgreSQL** - Deve continuar funcionando normalmente
- **Banco de dados iasenior** - Não foi afetado
- **Configurações do PostgreSQL** - Foram feitos backups

## 🧹 Limpeza

### Opção 1: Script Automático (Recomendado)

```bash
# No Server BD
curl -o /root/limpar_bd.sh https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/limpar_bd_erro.sh

chmod +x /root/limpar_bd.sh

bash /root/limpar_bd.sh
```

O script vai:
- Verificar o que foi instalado
- Perguntar o que remover
- Manter PostgreSQL intacto
- Verificar se tudo está funcionando

### Opção 2: Limpeza Manual

```bash
# 1. Verificar o que foi instalado
ls -la /opt/iasenior 2>/dev/null || echo "Código não encontrado"
docker --version 2>/dev/null || echo "Docker não encontrado"
systemctl list-units | grep iasenior || echo "Serviço não encontrado"

# 2. Remover código (se quiser)
rm -rf /opt/iasenior

# 3. Remover Docker (se quiser)
systemctl stop docker
apt-get remove -y docker-ce docker-ce-cli containerd.io
rm -rf /var/lib/docker

# 4. Remover serviço (se quiser)
systemctl stop iasenior-inferencia
systemctl disable iasenior-inferencia
rm -f /etc/systemd/system/iasenior-inferencia.service
systemctl daemon-reload

# 5. Remover MediaMTX (se quiser)
rm -rf /opt/mediamtx
```

## ✅ Verificar se PostgreSQL Está OK

```bash
# 1. Verificar se está rodando
systemctl status postgresql@16-main
# ou
systemctl status postgresql@15-main

# 2. Testar conexão
psql -h localhost -U iasenior -d iasenior -c "SELECT version();"
# Senha: iasenior2366

# 3. Verificar configurações
grep "listen_addresses" /etc/postgresql/16/main/postgresql.conf
# Deve estar: listen_addresses = '*'

# 4. Verificar pg_hba.conf
grep -i iasenior /etc/postgresql/16/main/pg_hba.conf
# Deve ter a regra de conexão remota
```

## 🎯 Próximos Passos

1. **Limpar o Server BD** (usar script acima)
2. **Verificar se PostgreSQL está funcionando**
3. **Executar o script no servidor correto** (Server PROCESS)

## 📝 Executar no Servidor Correto

Depois de limpar o BD, execute no **Server PROCESS**:

```bash
# No Server PROCESS (não no BD!)
curl -o /root/setup_process.sh https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/setup_server_process.sh

chmod +x /root/setup_process.sh

bash /root/setup_process.sh
```

## ⚠️ Importante

- **NÃO remova o PostgreSQL** - Ele deve continuar funcionando
- **NÃO remova o banco iasenior** - Os dados estão seguros
- **Apenas remova** o que foi instalado por engano (Docker, código Python, etc.)

## 🔍 Verificar o que Foi Instalado

```bash
# Verificar diretórios
ls -la /opt/ | grep iasenior
ls -la /opt/ | grep mediamtx

# Verificar serviços
systemctl list-units | grep iasenior

# Verificar Docker
docker --version
systemctl status docker

# Verificar Python venv
ls -la /opt/iasenior/venv 2>/dev/null || echo "Não encontrado"
```

---

**Resumo**: Execute o script de limpeza no BD, verifique se PostgreSQL está OK, depois execute o script de configuração no Server PROCESS (não no BD!).

