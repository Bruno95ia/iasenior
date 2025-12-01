# 📧 Configuração de Notificações - IASenior

Este guia explica como configurar o sistema de notificações por email.

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto ou defina variáveis de ambiente:

```env
# Habilitar notificações
NOTIFICATIONS_ENABLED=true

# Configurações SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app  # Use senha de app, não a senha normal
SMTP_USE_TLS=true

# Destinatários (separados por vírgula)
NOTIFICATION_EMAILS=cuidador1@email.com,cuidador2@email.com
```

### 2. Gmail (Recomendado)

Para usar Gmail:

1. **Ativar autenticação de 2 fatores** na sua conta Google
2. **Gerar senha de app**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "Email" e "Outro (nome personalizado)"
   - Digite "IASenior" como nome
   - Copie a senha gerada (16 caracteres)
3. **Usar a senha de app** no `SMTP_PASSWORD`

**Configuração para Gmail:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Senha de app (sem espaços)
SMTP_USE_TLS=true
```

### 3. Outlook/Hotmail

```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=seu_email@outlook.com
SMTP_PASSWORD=sua_senha
SMTP_USE_TLS=true
```

### 4. Outros Provedores

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**SendGrid:**
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua_api_key
```

## 🔔 Tipos de Notificações

### 1. Queda Detectada
- **Quando**: Sistema detecta uma possível queda
- **Frequência**: Máximo 1 a cada 5 minutos
- **Severidade**: Crítica
- **Assunto**: "🚨 ALERTA: Queda Detectada - Sistema IASenior"

### 2. Tempo no Banheiro Excedido
- **Quando**: Pessoa fica no banheiro mais que o limite configurado
- **Frequência**: Máximo 1 a cada 10 minutos por pessoa
- **Severidade**: Aviso
- **Assunto**: "⚠️ Alerta: Tempo no Banheiro Excedido"

### 3. Notificações de Sistema (Opcional)
- **Quando**: Erros ou avisos do sistema
- **Configurável**: `alertar_sistema` no código
- **Severidade**: Info/Warning/Error

## 🧪 Testar Notificações

### Teste Manual

```python
from notificacoes import get_notificacao_manager

# Obter gerenciador
notif = get_notificacao_manager()

# Testar notificação de queda
notif.notificar_queda()

# Testar notificação de banheiro
notif.notificar_banheiro_tempo(
    track_id="123",
    tempo_minutos=12,
    tempo_segundos=30
)
```

### Teste via Script

```bash
python -c "from notificacoes import get_notificacao_manager; get_notificacao_manager().notificar_queda()"
```

## 🛠️ Troubleshooting

### Erro: "authentication failed"
- Verifique usuário e senha
- Para Gmail, use senha de app (não senha normal)
- Verifique se autenticação de 2 fatores está ativada

### Erro: "connection refused"
- Verifique se a porta está correta (587 para TLS, 465 para SSL)
- Verifique firewall
- Tente desabilitar TLS: `SMTP_USE_TLS=false`

### Emails não estão sendo enviados
- Verifique `NOTIFICATIONS_ENABLED=true`
- Verifique logs para erros
- Teste conexão SMTP manualmente

### Muitos emails (spam)
- O sistema tem proteção anti-spam:
  - Quedas: máximo 1 a cada 5 minutos
  - Banheiro: máximo 1 a cada 10 minutos por pessoa
- Ajuste os tempos no código se necessário

## 📝 Notas

- Emails são enviados em HTML e texto
- Histórico de notificações é mantido em memória
- Notificações são enviadas automaticamente quando eventos ocorrem
- Sistema funciona mesmo se banco de dados não estiver disponível

## 🔒 Segurança

- **Nunca** commite senhas no código
- Use variáveis de ambiente ou arquivo `.env` (não versionado)
- Para produção, use serviços de email dedicados (SendGrid, AWS SES, etc)
- Considere usar secrets management (AWS Secrets Manager, etc)

---

**Última atualização**: Janeiro 2024

