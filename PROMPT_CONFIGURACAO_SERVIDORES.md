# 🤖 Prompt Completo para Configuração dos Servidores IASenior

## 📋 Copie este prompt completo e cole no ChatGPT/Claude

```
Você é um especialista em DevOps, administração de sistemas Linux e Python. Estou configurando o sistema IASenior em 4 servidores Ubuntu 24.04 da Opus Tech e preciso da sua ajuda passo a passo, detalhada e prática.

## CONTEXTO DO PROJETO

IASenior é um sistema de monitoramento inteligente com IA para detecção de quedas em tempo real, desenvolvido em Python 3.12 usando:
- YOLOv8 (Ultralytics) para detecção de objetos e pessoas
- PyTorch para deep learning
- Streamlit para dashboard web interativo
- PostgreSQL 15 para banco de dados
- Flask para servidor MJPEG
- MediaMTX (Docker) para streaming RTSP
- Sistema de 7 agentes inteligentes especializados

## ARQUITETURA DOS SERVIDORES OPUS TECH

Tenho 4 servidores físicos da Opus Tech:

### 1. Server PROCESS (16 vCPU + 32GB RAM + 200GB FLASH)
**Função**: Inferência YOLO e processamento de detecção
**Precisa instalar**:
- Python 3.10+ (já tem 3.12.3)
- PyTorch + Ultralytics YOLO
- OpenCV, NumPy, Flask
- Docker (para MediaMTX)
- FFmpeg
**Portas**: 8554 (RTSP), 8888 (MJPEG)
**Scripts principais**: `scripts/stream_inferencia_rtsp.py`

### 2. Server API (8 vCPU + 16GB RAM + 100GB FLASH)
**Função**: Dashboard Streamlit e servidor MJPEG
**Precisa instalar**:
- Python 3.10+ (já tem 3.12.3)
- Streamlit, Flask, Pandas, Plotly
- psycopg2-binary (PostgreSQL client)
**Portas**: 8501 (Dashboard), 8080 (Portal)
**Scripts principais**: `painel_IA/app/dashboard.py`, `mjpeg_server_com_deteccoes.py`

### 3. Server BD (4 vCPU + 8GB RAM + 500GB FLASH)
**Função**: Banco de dados PostgreSQL
**Precisa instalar**:
- PostgreSQL 15
**Porta**: 5432
**Banco**: iasenior
**Usuário**: iasenior

### 4. Server STR (2 vCPU + 4GB RAM + 2TB SAS)
**Função**: Armazenamento de logs, capturas e backups
**Precisa configurar**:
- Estrutura de diretórios em `/mnt/iasenior`
- Compartilhamento NFS (ou método da Opus)
- Scripts de limpeza automática

## PROBLEMAS ATUAIS IDENTIFICADOS

1. **DNS não funciona**: Erro "Temporary failure resolving 'br.archive.ubuntu.com'"
   - Servidores podem não ter acesso à internet
   - Pode precisar configurar DNS manualmente
   - Pode precisar de proxy da Opus

2. **Docker não instalado**: Tentativa de instalação falhou por DNS

3. **Código ainda não foi copiado** para os servidores

## ESTRUTURA DO CÓDIGO

O código está no GitHub: https://github.com/Bruno95ia/iasenior

Estrutura principal:
- `/scripts/stream_inferencia_rtsp.py` - Script de inferência YOLO
- `/painel_IA/app/dashboard.py` - Dashboard Streamlit
- `/mjpeg_server_com_deteccoes.py` - Servidor MJPEG
- `/database.py` - Módulo de banco de dados
- `/config.py` - Configurações centralizadas
- `/modelos/queda_custom.pt` - Modelo YOLO treinado
- `/requirements.txt` - Dependências Python

## DEPENDÊNCIAS PRINCIPAIS

Python packages (requirements.txt):
- ultralytics>=8.0.0
- torch>=2.0.0
- torchvision>=0.15.0
- opencv-python>=4.8.0
- streamlit>=1.28.0
- flask>=3.0.0
- pandas>=2.0.0
- plotly>=5.17.0
- psycopg2-binary>=2.9.0
- python-dotenv>=1.0.0
- reportlab>=4.0.0
- openpyxl>=3.1.0
- bcrypt>=4.0.0

## OBJETIVO

Preciso de ajuda para:

1. **Resolver problema de DNS/rede** nos servidores
2. **Instalar todas as dependências** em cada servidor
3. **Configurar PostgreSQL** no Server BD
4. **Configurar ambiente Python** nos Servers PROCESS e API
5. **Fazer download do código** do GitHub
6. **Configurar arquivos .env** com variáveis corretas
7. **Configurar serviços systemd** para iniciar automaticamente
8. **Configurar compartilhamento de storage** (Server STR)
9. **Testar e validar** cada componente
10. **Configurar firewall** (Fortigate 60D)

## FORMATO DE RESPOSTA DESEJADO

Por favor, forneça:
- **Comandos específicos** para executar (um de cada vez)
- **Explicação clara** do que cada comando faz
- **Como verificar** se funcionou (comando de teste)
- **O que fazer se der erro** (troubleshooting)
- **Próximos passos** após cada etapa
- **Aguarde minha confirmação** antes de passar para o próximo passo

## RESTRIÇÕES E LIMITAÇÕES

- Os servidores podem ter **problemas de conectividade** com internet
- Preciso de soluções que funcionem mesmo com **DNS limitado**
- Prefiro **comandos simples e diretos**
- Quero fazer **passo a passo**, testando cada etapa
- **Não tenho acesso físico** aos servidores (apenas SSH)
- Posso ter **acesso limitado** à internet dos servidores

## ORDEM DE INSTALAÇÃO SUGERIDA

1. **Server BD** primeiro (PostgreSQL)
2. **Server STR** segundo (armazenamento)
3. **Server PROCESS** terceiro (inferência)
4. **Server API** quarto (dashboard)
5. **Configuração final** (conexões, testes)

## INFORMAÇÕES ADICIONAIS

- **Sistema Operacional**: Ubuntu 24.04 (Noble)
- **Python**: 3.12.3 (já instalado)
- **Acesso**: Root via SSH
- **Firewall**: Fortigate 60D
- **Rede**: Pode ter restrições de acesso externo

## COMEÇAR POR

Primeiro, me ajude a:
1. Diagnosticar e resolver o problema de DNS
2. Verificar conectividade com internet
3. Instalar PostgreSQL no Server BD
4. Depois vamos para os outros servidores

Me guie passo a passo, perguntando o resultado de cada comando antes de prosseguir para o próximo. Seja paciente e detalhado nas explicações.
```

---

## 🔄 Como me acessar nos servidores

### Opção 1: Terminal SSH com histórico

Conecte via SSH e mantenha o histórico da conversa:

```bash
# No servidor, crie um arquivo com o prompt
nano /tmp/prompt_iasenior.txt
# Cole o prompt acima e salve

# Depois, copie e cole partes do prompt no ChatGPT via navegador
# Ou use curl para enviar para API (se tiver token)
```

### Opção 2: Script de ajuda local

Crie um script que salva comandos e resultados:

```bash
#!/bin/bash
# ajuda_iasenior.sh - Salva comandos e resultados

echo "Digite o comando que o GPT sugeriu:"
read COMANDO

echo "=== Executando: $COMANDO ===" > /tmp/iasenior_log.txt
eval $COMANDO >> /tmp/iasenior_log.txt 2>&1
echo "=== Resultado acima ===" >> /tmp/iasenior_log.txt

cat /tmp/iasenior_log.txt
```

### Opção 3: Usar o prompt em sessões separadas

1. Conecte no servidor via SSH
2. Abra o ChatGPT em outra aba/janela
3. Cole o prompt
4. Execute os comandos que ele sugerir
5. Cole os resultados de volta no ChatGPT

### Opção 4: Terminal split screen

- Lado esquerdo: SSH no servidor
- Lado direito: ChatGPT/Claude no navegador
- Copie e cole entre as janelas

---

## 📝 Dica: Salvar progresso

Crie um arquivo de log no servidor:

```bash
# No servidor
script /tmp/iasenior_setup.log
# Todos os comandos e saídas serão salvos aqui
# Digite 'exit' para parar de gravar
```

Assim você pode revisar depois ou compartilhar comigo.

---

O prompt acima está pronto para usar. Copie e cole no ChatGPT/Claude quando estiver nos servidores.

