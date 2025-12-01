# 🐳 Setup Docker - IASenior

Guia rápido para configurar o ambiente Docker do IASenior.

## 📋 Pré-requisitos

- Docker instalado: https://docs.docker.com/get-docker/
- Docker Compose instalado (geralmente vem com Docker Desktop)

## 🚀 Início Rápido

### 1. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env se necessário (valores padrão já funcionam)
```

### 2. Iniciar PostgreSQL

```bash
# Iniciar apenas PostgreSQL
docker-compose up -d postgres

# Ou iniciar PostgreSQL + pgAdmin
docker-compose up -d
```

### 3. Verificar se está rodando

```bash
# Ver status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f postgres
```

### 4. Pronto! ✅

O PostgreSQL estará disponível em `localhost:5432` e o sistema criará o schema automaticamente.

## 📊 Acessar pgAdmin (Interface Visual)

Se iniciou o pgAdmin:

1. Acesse: http://localhost:5050
2. Login:
   - Email: `admin@iasenior.com`
   - Senha: `admin`
3. Adicionar servidor:
   - Nome: `IASenior DB`
   - Host: `postgres` (nome do serviço no Docker)
   - Port: `5432`
   - Database: `iasenior`
   - Username: `iasenior`
   - Password: `iasenior`

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar
docker-compose up -d

# Parar
docker-compose stop

# Iniciar novamente
docker-compose start

# Parar e remover containers (mantém dados)
docker-compose down

# Parar e remover tudo incluindo dados (⚠️ cuidado!)
docker-compose down -v
```

### Logs

```bash
# Ver logs do PostgreSQL
docker-compose logs -f postgres

# Ver logs do pgAdmin
docker-compose logs -f pgadmin

# Ver todos os logs
docker-compose logs -f
```

### Backup e Restore

```bash
# Backup
docker-compose exec postgres pg_dump -U iasenior iasenior > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T postgres psql -U iasenior iasenior < backup.sql
```

### Acessar PostgreSQL via CLI

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U iasenior -d iasenior

# Comandos úteis dentro do psql:
# \dt          - Listar tabelas
# \d eventos   - Ver estrutura da tabela eventos
# \q           - Sair
```

## 🔍 Verificar Saúde

```bash
# Ver status dos containers
docker-compose ps

# Verificar se PostgreSQL está respondendo
docker-compose exec postgres pg_isready -U iasenior
```

## 🗑️ Limpar Tudo

```bash
# Parar e remover containers e volumes (⚠️ apaga todos os dados!)
docker-compose down -v

# Remover imagens também
docker-compose down -v --rmi all
```

## 📝 Estrutura dos Volumes

Os dados são persistidos em volumes Docker:

- `postgres_data`: Dados do PostgreSQL
- `pgadmin_data`: Configurações do pgAdmin

Para ver onde estão os volumes:

```bash
docker volume ls | grep iasenior
docker volume inspect iasenior_postgres_data
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs postgres

# Verificar se a porta 5432 está livre
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows
```

### Erro de conexão

- Verifique se o container está rodando: `docker-compose ps`
- Verifique as variáveis de ambiente no `.env`
- Verifique os logs: `docker-compose logs postgres`

### Resetar banco de dados

```bash
# Parar containers
docker-compose down

# Remover volume (apaga dados!)
docker volume rm iasenior_postgres_data

# Iniciar novamente
docker-compose up -d postgres
```

## 🔒 Segurança

Para produção:

1. **Altere as senhas padrão** no `.env`:
   ```env
   DB_PASSWORD=senha_forte_aqui
   POSTGRES_PASSWORD=senha_forte_aqui
   ```

2. **Não exponha a porta 5432** publicamente:
   ```yaml
   # No docker-compose.yml, remova ou comente:
   # ports:
   #   - "5432:5432"
   ```

3. **Use secrets management** (Docker Secrets, AWS Secrets Manager, etc.)

4. **Configure SSL/TLS** para conexões

## 📚 Mais Informações

- [Documentação Docker Compose](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [pgAdmin Docker Hub](https://hub.docker.com/r/dpage/pgadmin4)

