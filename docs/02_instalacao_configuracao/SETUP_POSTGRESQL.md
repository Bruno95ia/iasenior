# 🗄️ Setup do PostgreSQL - IASenior

Este guia explica como configurar o PostgreSQL para o sistema IASenior.

## 📋 Pré-requisitos

- Docker e Docker Compose instalados (recomendado)
- OU PostgreSQL instalado localmente (versão 12 ou superior)
- Python 3.10+
- psycopg2-binary instalado

---

## 🐳 Opção Docker (Recomendado - Mais Fácil!)

### 1. Iniciar PostgreSQL com Docker

```bash
# Na raiz do projeto
docker-compose up -d postgres

# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs -f postgres
```

### 2. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e ajuste se necessário:

```bash
cp .env.example .env
```

As configurações padrão já funcionam com o Docker Compose:
- Database: `iasenior`
- User: `iasenior`
- Password: `iasenior`
- Host: `localhost`
- Port: `5432`

### 3. Pronto! ✅

O PostgreSQL estará disponível e o sistema criará o schema automaticamente na primeira conexão.

### 4. Acessar pgAdmin (Opcional - Interface Visual)

Se quiser gerenciar o banco visualmente:

```bash
# Iniciar pgAdmin também
docker-compose up -d pgadmin

# Acesse: http://localhost:5050
# Email: admin@iasenior.com
# Senha: admin
```

Para conectar ao PostgreSQL no pgAdmin:
- Host: `postgres` (nome do serviço no Docker)
- Port: `5432`
- Database: `iasenior`
- Username: `iasenior`
- Password: `iasenior`

### 5. Comandos úteis

```bash
# Parar PostgreSQL
docker-compose stop postgres

# Iniciar PostgreSQL
docker-compose start postgres

# Parar e remover containers (mantém dados)
docker-compose down

# Parar e remover tudo incluindo dados (⚠️ apaga dados!)
docker-compose down -v

# Backup do banco
docker-compose exec postgres pg_dump -U iasenior iasenior > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U iasenior iasenior < backup.sql

# Ver logs
docker-compose logs -f postgres

# Verificar saúde do container
docker-compose ps
```

### 6. Vantagens do Docker

✅ **Setup rápido**: Um comando e está pronto  
✅ **Isolamento**: Não precisa instalar PostgreSQL localmente  
✅ **Portabilidade**: Funciona igual em qualquer OS  
✅ **Fácil de limpar**: `docker-compose down -v`  
✅ **Versão controlada**: Sempre usa PostgreSQL 15  
✅ **Backup simples**: Apenas copiar o volume `postgres_data`

---

## 📦 Opção Manual (Instalação Tradicional)

Se preferir instalar PostgreSQL localmente:

## 🚀 Instalação

### 1. Instalar PostgreSQL

#### macOS (Homebrew)
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Windows
Baixe e instale do site oficial: https://www.postgresql.org/download/windows/

### 2. Criar Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco de dados
CREATE DATABASE iasenior;

# Criar usuário (opcional)
CREATE USER iasenior WITH PASSWORD 'iasenior';

# Dar permissões
GRANT ALL PRIVILEGES ON DATABASE iasenior TO iasenior;

# Sair
\q
```

### 3. Instalar Dependência Python

```bash
pip install psycopg2-binary
```

Ou adicione ao requirements.txt (já incluído):
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### Opção 1: Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados PostgreSQL
DB_ENABLED=true
DB_NAME=iasenior
DB_USER=iasenior
DB_PASSWORD=iasenior
DB_HOST=localhost
DB_PORT=5432
```

### Opção 2: Configuração Direta

Edite `config.py` ou defina variáveis de ambiente:

```bash
export DB_ENABLED=true
export DB_NAME=iasenior
export DB_USER=iasenior
export DB_PASSWORD=iasenior
export DB_HOST=localhost
export DB_PORT=5432
```

## 🔧 Verificação

### Testar Conexão

```python
from database import get_db_manager

# Testar conexão
db = get_db_manager()
print("✅ Conexão estabelecida!")

# Testar inserção
evento_id = db.inserir_evento(
    tipo='teste',
    mensagem='Teste de conexão',
    severidade='info'
)
print(f"✅ Evento inserido com ID: {evento_id}")
```

### Verificar Schema

```bash
psql -U iasenior -d iasenior

# Listar tabelas
\dt

# Ver estrutura de uma tabela
\d eventos
\d metricas
\d alertas
```

## 📊 Tabelas Criadas

O sistema cria automaticamente as seguintes tabelas:

1. **eventos** - Eventos do sistema
2. **metricas** - Métricas de performance
3. **alertas** - Alertas ativos e resolvidos
4. **historico_ocupacao** - Histórico de ocupação (quarto/banheiro)
5. **deteccoes_queda** - Detecções de queda
6. **monitoramento_banheiro** - Monitoramento de tempo no banheiro

## 🔄 Migração de Dados Existentes

Para migrar dados dos arquivos existentes para o banco:

```python
from persistencia import get_persistencia_manager

persistencia = get_persistencia_manager()
persistencia.sincronizar_arquivos_existentes()
```

## 🛠️ Troubleshooting

### Erro: "psycopg2 não está instalado"
```bash
pip install psycopg2-binary
```

### Erro: "connection refused"
- Verifique se PostgreSQL está rodando: `pg_isready`
- Verifique host e porta nas configurações
- Verifique firewall

### Erro: "authentication failed"
- Verifique usuário e senha
- Verifique `pg_hba.conf` para configurações de autenticação

### Erro: "database does not exist"
- Crie o banco: `CREATE DATABASE iasenior;`

## 📝 Notas

- O sistema cria o schema automaticamente na primeira conexão
- Índices são criados automaticamente para melhor performance
- O pool de conexões gerencia múltiplas conexões simultâneas
- Dados são salvos automaticamente quando `DB_ENABLED=true`

## 🔒 Segurança

Para produção, considere:
- Usar senhas fortes
- Limitar acesso por IP
- Usar SSL/TLS
- Configurar backup automático
- Usar variáveis de ambiente ou secrets management

