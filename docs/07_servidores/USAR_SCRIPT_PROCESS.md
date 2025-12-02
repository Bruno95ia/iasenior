# 🚀 Como Usar o Script de Configuração do Server PROCESS

## 📋 Pré-requisitos

Antes de executar, tenha em mãos:
- IP do Server BD (PostgreSQL)
- IP do Server STR (Storage)

## 🔧 Executar Script

### Opção 1: Baixar e Executar Diretamente

```bash
# No Server PROCESS, baixar script
curl -o /root/setup_process.sh https://raw.githubusercontent.com/Bruno95ia/iasenior/main/scripts/setup_server_process.sh

# Dar permissão
chmod +x /root/setup_process.sh

# Executar
bash /root/setup_process.sh
```

### Opção 2: Se já tem o código local

```bash
# No Server PROCESS
cd /opt/iasenior
bash scripts/setup_server_process.sh
```

## 📝 O que o Script Faz

1. ✅ Configura DNS
2. ✅ Atualiza sistema
3. ✅ Instala/verifica Docker
4. ✅ Instala FFmpeg
5. ✅ Baixa/atualiza código do GitHub
6. ✅ Cria ambiente virtual Python
7. ✅ Instala dependências (PyTorch, YOLO, OpenCV, etc.)
8. ✅ Configura MediaMTX
9. ✅ Cria arquivo .env (solicita IPs)
10. ✅ Testa conexão com BD
11. ✅ Verifica modelo YOLO
12. ✅ Cria serviço systemd
13. ✅ Realiza verificações finais

## 🎯 Durante a Execução

O script vai:
- Solicitar IPs dos servidores (se não tiver .env)
- Instalar tudo automaticamente
- Testar conexões
- Mostrar resumo final

## ✅ Após a Execução

### 1. Testar Manualmente (IMPORTANTE)

```bash
cd /opt/iasenior
source venv/bin/activate
python scripts/stream_inferencia_rtsp.py
```

Se funcionar (mesmo que dê erro de stream), está OK.

### 2. Iniciar Serviço

```bash
systemctl start iasenior-inferencia
systemctl status iasenior-inferencia
```

### 3. Ver Logs

```bash
journalctl -u iasenior-inferencia -f
```

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError"

```bash
cd /opt/iasenior
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Connection refused" ao BD

```bash
# Verificar IP no .env
cat /opt/iasenior/.env | grep DB_HOST

# Testar conexão manual
psql -h IP_DO_BD -U iasenior -d iasenior -c "SELECT 1;"
```

### Erro: "Modelo não encontrado"

```bash
# Verificar se modelo existe
ls -lh /opt/iasenior/modelos/queda_custom.pt

# Se não existir, será baixado automaticamente na primeira execução
```

### Serviço não inicia

```bash
# Ver logs detalhados
journalctl -u iasenior-inferencia -n 50

# Verificar caminhos
cat /etc/systemd/system/iasenior-inferencia.service

# Testar manualmente
cd /opt/iasenior
source venv/bin/activate
python scripts/stream_inferencia_rtsp.py
```

## 📊 Verificar Status

```bash
# Status do serviço
systemctl status iasenior-inferencia

# Portas em uso
netstat -tulpn | grep -E "8554|8888"

# Processos Python
ps aux | grep python | grep stream_inferencia

# Espaço em disco
df -h /opt/iasenior
```

## 🔄 Reexecutar Script

Se precisar reexecutar:

```bash
# O script é idempotente (pode executar várias vezes)
bash /root/setup_process.sh
```

Ele vai:
- Verificar o que já está instalado
- Atualizar apenas o necessário
- Não duplicar configurações

## 📞 Suporte

Se algo não funcionar:

1. Verificar logs: `journalctl -u iasenior-inferencia -n 50`
2. Testar manualmente: `python scripts/stream_inferencia_rtsp.py`
3. Verificar .env: `cat /opt/iasenior/.env`
4. Verificar conectividade: `ping IP_DO_BD`

---

**Última atualização**: 2025-12-02

