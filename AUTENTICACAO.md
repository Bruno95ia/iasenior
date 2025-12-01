# 🔐 Sistema de Autenticação - IASenior

Sistema completo de autenticação e autorização com níveis de acesso para o projeto IASenior.

## 📋 Visão Geral

O sistema de autenticação implementa:
- **Login/Logout** com tokens de sessão
- **Níveis de acesso** hierárquicos
- **Permissões** granulares por funcionalidade
- **Sessões** gerenciadas no banco de dados
- **Logs de autenticação** para auditoria
- **Proteção contra brute force** (bloqueio temporário após tentativas falhadas)

## 🎯 Níveis de Acesso

O sistema possui 4 níveis de acesso hierárquicos:

### 1. Admin (Nível 1)
- **Acesso total** ao sistema
- Pode gerenciar usuários
- Pode configurar o sistema
- Pode visualizar e editar todos os dados
- Permissões: `acesso_total`, `gerenciar_usuarios`, `configurar_sistema`, `visualizar_dados`, `editar_dados`

### 2. Operador (Nível 2)
- Acesso a operações e visualização
- Pode gerenciar alertas
- Pode visualizar e editar dados
- Permissões: `visualizar_dados`, `editar_dados`, `gerenciar_alertas`

### 3. Visualizador (Nível 3)
- Apenas visualização de dados e relatórios
- Não pode editar dados
- Permissões: `visualizar_dados`

### 4. Cliente (Nível 4)
- Acesso limitado ao portal
- Pode visualizar relatórios
- Permissões: `visualizar_portal`, `visualizar_relatorios`

## 🚀 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

As dependências necessárias incluem:
- `bcrypt>=4.0.0` - Para hash de senhas
- `flask-cors>=4.0.0` - Para CORS no servidor
- `psycopg2-binary>=2.9.0` - Para PostgreSQL

### 2. Configurar Banco de Dados

O sistema criará automaticamente as tabelas necessárias na primeira conexão:

- `niveis_acesso` - Níveis de acesso disponíveis
- `usuarios` - Usuários do sistema
- `sessoes` - Sessões ativas
- `logs_autenticacao` - Logs de autenticação

### 3. Criar Usuário Administrador

```bash
python criar_usuario_admin.py
```

Siga as instruções para criar o primeiro usuário administrador.

## 📖 Uso

### Servidor com Autenticação

Para usar o servidor com autenticação integrada:

```bash
cd painel_IA/app
python servidor_auth.py
```

O servidor estará disponível em `http://localhost:8080`

### Login

1. Acesse `http://localhost:8080/login.html`
2. Digite usuário e senha
3. Após login bem-sucedido, será redirecionado para o portal

### API de Autenticação

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "senha123"
}
```

Resposta:
```json
{
  "sucesso": true,
  "token": "abc123...",
  "usuario": {
    "id": 1,
    "username": "admin",
    "email": "admin@iasenior.com",
    "nome_completo": "Administrador",
    "nivel_nome": "admin",
    "nivel_numero": 1,
    "permissoes": {...}
  }
}
```

#### Verificar Token
```bash
GET /api/auth/verify
Authorization: Bearer <token>
```

#### Logout
```bash
POST /api/auth/logout
Authorization: Bearer <token>
```

#### Obter Usuário Atual
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

## 🔧 Integração no Código

### Verificar Autenticação

```python
from auth import get_auth_manager

auth_manager = get_auth_manager()

# Verificar token
resultado = auth_manager.verificar_token(token)
if resultado:
    usuario = resultado['usuario']
    print(f"Usuário autenticado: {usuario['username']}")
```

### Verificar Permissões

```python
# Verificar permissão específica
if auth_manager.verificar_permissao(usuario, 'editar_dados'):
    # Usuário pode editar dados
    pass

# Verificar nível mínimo
if auth_manager.verificar_nivel_minimo(usuario, 2):  # Operador ou superior
    # Usuário tem nível suficiente
    pass
```

### Criar Usuário

```python
from auth import get_auth_manager

auth_manager = get_auth_manager()

resultado = auth_manager.criar_usuario(
    username='novo_usuario',
    senha='senha123',
    email='usuario@example.com',
    nome_completo='Novo Usuário',
    nivel_acesso_id=3  # Visualizador
)
```

### No Servidor Flask

```python
from servidor_auth import requer_autenticacao, requer_permissao, requer_nivel

@app.route('/api/dados')
@requer_autenticacao
def obter_dados():
    usuario = request.usuario
    # Retornar dados
    return jsonify({'dados': '...'})

@app.route('/api/editar')
@requer_permissao('editar_dados')
def editar_dados():
    # Apenas usuários com permissão podem acessar
    return jsonify({'sucesso': True})

@app.route('/api/admin')
@requer_nivel(1)  # Apenas admin
def admin():
    # Apenas administradores podem acessar
    return jsonify({'sucesso': True})
```

## 🔒 Segurança

### Proteções Implementadas

1. **Hash de Senhas**: Usa bcrypt com salt automático
2. **Tokens Seguros**: Tokens aleatórios de 64 caracteres
3. **Sessões com Expiração**: Tokens expiram após 24 horas (configurável)
4. **Proteção contra Brute Force**: Bloqueio temporário após 5 tentativas falhadas
5. **Logs de Auditoria**: Todas as tentativas de login são registradas
6. **Validação de Sessão**: Verificação de token em cada requisição

### Configurações de Segurança

Variáveis de ambiente:

```bash
# Tempo de expiração do token (horas)
TOKEN_EXPIRATION_HOURS=24

# Máximo de tentativas de login
MAX_LOGIN_ATTEMPTS=5

# Chave secreta do Flask
FLASK_SECRET_KEY=<chave_aleatoria>
```

### Recomendações para Produção

1. **Use HTTPS**: Configure SSL/TLS para proteger tokens em trânsito
2. **Chave Secreta Forte**: Use uma chave secreta aleatória e segura
3. **Rate Limiting**: Implemente rate limiting nas rotas de autenticação
4. **Senhas Fortes**: Exija senhas com complexidade mínima
5. **2FA**: Considere implementar autenticação de dois fatores
6. **Backup**: Faça backup regular do banco de dados

## 📊 Estrutura do Banco de Dados

### Tabela `usuarios`
- `id`: ID único do usuário
- `username`: Nome de usuário (único)
- `email`: Email (único, opcional)
- `senha_hash`: Hash bcrypt da senha
- `nome_completo`: Nome completo
- `nivel_acesso_id`: ID do nível de acesso
- `ativo`: Se o usuário está ativo
- `ultimo_login`: Data/hora do último login
- `tentativas_login_falhadas`: Contador de tentativas falhadas
- `bloqueado_ate`: Data/hora até quando está bloqueado

### Tabela `sessoes`
- `id`: ID único da sessão
- `usuario_id`: ID do usuário
- `token`: Token da sessão (único)
- `ip_address`: IP do cliente
- `user_agent`: User agent do navegador
- `expira_em`: Data/hora de expiração
- `ativo`: Se a sessão está ativa

### Tabela `logs_autenticacao`
- `id`: ID único do log
- `usuario_id`: ID do usuário (pode ser NULL)
- `username`: Nome de usuário tentado
- `tipo_evento`: Tipo (login, logout, etc)
- `ip_address`: IP do cliente
- `sucesso`: Se a operação foi bem-sucedida
- `mensagem`: Mensagem descritiva
- `timestamp`: Data/hora do evento

## 🛠️ Manutenção

### Limpar Sessões Expiradas

O sistema limpa automaticamente sessões expiradas, mas você pode fazer manualmente:

```python
from database import get_db_manager

db = get_db_manager()
db.limpar_sessoes_expiradas()
```

### Ver Logs de Autenticação

```python
from database import get_db_manager

db = get_db_manager()
# Os logs estão na tabela logs_autenticacao
# Você pode consultar diretamente no banco ou criar métodos específicos
```

### Desbloquear Usuário

```python
from database import get_db_manager

db = get_db_manager()
conn = db.get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE usuarios 
            SET bloqueado_ate = NULL, tentativas_login_falhadas = 0
            WHERE username = %s
        """, ('username',))
        conn.commit()
finally:
    db.return_connection(conn)
```

## 📝 Notas

- O sistema usa **bcrypt** para hash de senhas (recomendado e seguro)
- Tokens são armazenados em **localStorage** no navegador e em **cookies** HTTP-only
- Sessões são gerenciadas no **banco de dados** para permitir invalidação remota
- Todos os eventos de autenticação são **logados** para auditoria

## 🐛 Troubleshooting

### Erro: "bcrypt não está instalado"
```bash
pip install bcrypt
```

### Erro: "psycopg2 não está instalado"
```bash
pip install psycopg2-binary
```

### Erro: "Sistema de autenticação não disponível"
- Verifique se o banco de dados está configurado e acessível
- Verifique se as tabelas foram criadas corretamente
- Verifique os logs para mais detalhes

### Usuário não consegue fazer login
1. Verifique se o usuário está ativo
2. Verifique se não está bloqueado (tentativas falhadas)
3. Verifique os logs de autenticação
4. Verifique se a senha está correta

## 📚 Referências

- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

