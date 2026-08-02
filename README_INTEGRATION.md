# 🚀 Telegram → Hermes → Claude Code + Obsidian

Sistema completo de integração para enviar instruções, prompts, imagens e código do Telegram para Claude Code usando Hermes como bridge e Obsidian para gerenciar sessões.

## 📊 Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM BOT                            │
│               @Danrcbh_bot (telegram)                       │
└────────────────────────┬────────────────────────────────────┘
                         ↓ (webhook POST)
┌─────────────────────────────────────────────────────────────┐
│           TELEGRAM WEBHOOK SERVER (FastAPI)                 │
│         telegram_webhook_server.py (porta 8000)             │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│   TELEGRAM+HERMES+OBSIDIAN INTEGRATOR                       │
│  telegram_hermes_obsidian_integrator.py                     │
└────┬────────────────────────┬──────────────────────────┬────┘
     ↓                        ↓                          ↓
  TEXT/CODE            IMAGE/FILE                 SESSION MGT
     ↓                        ↓                          ↓
┌──────────────────────────────────────────────────────────────┐
│         HERMES BRIDGE (hermes_claude_bridge.py)              │
│              Hermes MCP Server                               │
│              (100.86.232.77:8080)                            │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│              CLAUDE CODE (MCP Client)                        │
│            (Análise + Processamento)                         │
└──────────────────────────────────────────────────────────────┘

PARALLEL:
┌──────────────────────────────────────────────────────────────┐
│         OBSIDIAN VAULT (obsidian_vault_manager.py)           │
│    • Sessions Management                                     │
│    • Interaction Logging                                     │
│    • Message History                                         │
│    • Session Export/Archive                                  │
│    Vault: ./obsidian_vault/                                  │
└──────────────────────────────────────────────────────────────┘
```

## 🗂️ Estrutura de Arquivos

### Passo A: Claude Code Bridge
- **`hermes_claude_bridge.py`** - Bridge para enviar dados a Claude Code
  - Classes: `HermesClaudeBridge`, `ContentType`
  - Métodos: `send_text_prompt()`, `send_code()`, `send_image_analysis()`, `send_file()`

### Passo B: Telegram Webhook
- **`telegram_webhook_server.py`** - Servidor FastAPI para webhooks
  - Endpoints: `/webhook/telegram`, `/health`, `/set-webhook`, `/`
  - Handlers: `process_text_message()`, `process_photo_message()`, `process_document_message()`, `process_code_command()`

### Passo C: Obsidian Integration
- **`obsidian_vault_manager.py`** - Gerenciador de Vault
  - Classes: `ObsidianVaultManager`, `SessionType`, `SessionStatus`
  - Métodos: `create_session()`, `add_interaction()`, `add_message()`, `list_sessions()`, `get_vault_stats()`

- **`telegram_hermes_obsidian_integrator.py`** - Integrador completo
  - Classe: `TelegramHermesObsidianIntegrator`
  - Conecta todos os componentes

### Documentação
- **`STEP_A_CLAUDE_INTEGRATION.md`** - Guia Passo A
- **`STEP_B_TELEGRAM_WEBHOOK.md`** - Guia Passo B
- **`STEP_C_OBSIDIAN_INTEGRATION.md`** - Guia Passo C
- **`TELEGRAM_INTEGRATION.md`** - Visão geral técnica
- **`CLAUDE.md`** - Documentação do projeto

### Configuração
- **`requirements.txt`** - Dependências Python
- **`.env.example`** - Exemplo de variáveis de ambiente

## 🚀 Instalação Rápida

### 1. Clonar/Preparar

```bash
git clone <repo>
cd telegram-integration
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Ambiente

```bash
cp .env.example .env
# Editar .env com seus valores
```

### 4. Iniciar Sistema

#### Terminal 1: Webhook Server
```bash
python telegram_webhook_server.py
# Output: 🚀 Starting Telegram Webhook Server on 0.0.0.0:8000
```

#### Terminal 2: Monitorar Obsidian (opcional)
```bash
python -c "from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator; i = TelegramHermesObsidianIntegrator(); print(i.get_vault_stats())"
```

## 📝 Exemplos de Uso

### Exemplo 1: Enviar Texto via Telegram

```
User (Telegram): "Analise este código"
    ↓
Bot (responde): "✅ Mensagem enviada para Claude Code!"
    ↓
Obsidian (salva): Session + Message + Interaction
    ↓
Claude (analisa): Processa e responde
```

### Exemplo 2: Enviar Imagem via Telegram

```
User (Telegram): [envia screenshot.jpg]
    ↓
Bot (processa): Download + Send
    ↓
Claude (analisa): Vision analysis
    ↓
Obsidian (registra): Interaction type=image
```

### Exemplo 3: Enviar Código via Telegram

```
User (Telegram): /code def hello(): return "world"
    ↓
Bot (processa): Extrai código
    ↓
Claude (analisa): Code review + suggestions
    ↓
Obsidian (salva): Interaction type=code
```

## 🎯 Componentes Detalhados

### A) Hermes Bridge (`hermes_claude_bridge.py`)

```python
from hermes_claude_bridge import HermesClaudeBridge

bridge = HermesClaudeBridge()

# Enviar texto
result = bridge.send_text_prompt("Seu prompt aqui")

# Enviar código
result = bridge.send_code("def foo(): pass", language="python")

# Enviar imagem
result = bridge.send_image_analysis("path/to/image.jpg")
```

**Features:**
- Health check do Hermes
- Encoding base64 de imagens
- Metadados automáticos
- Timeout configurável

### B) Webhook Server (`telegram_webhook_server.py`)

```bash
# Inicia server
python telegram_webhook_server.py

# Health check
curl http://localhost:8000/health

# Set webhook
curl -X POST "http://localhost:8000/set-webhook?webhook_url=https://seu-dominio.com/webhook/telegram"
```

**Endpoints:**
- `GET /` - Status
- `GET /health` - Health check
- `POST /webhook/telegram` - Receive messages
- `POST /set-webhook` - Configure webhook

**Tipos de Mensagem:**
- Text → `process_text_message()`
- Photo → `process_photo_message()`
- Document → `process_document_message()`
- `/code` command → `process_code_command()`

### C) Obsidian Manager (`obsidian_vault_manager.py`)

```python
from obsidian_vault_manager import ObsidianVaultManager, SessionType, SessionStatus

vault = ObsidianVaultManager("./obsidian_vault")

# Criar sessão
session = vault.create_session(
    session_type=SessionType.HERMES_OBSIDIAN,
    description="Minha sessão",
    user="danrcosta"
)

# Adicionar mensagem
vault.add_message(
    session_id=session["id"],
    role="user",
    content="Olá Claude!"
)

# Listar sessões
sessions = vault.list_sessions()

# Estatísticas
stats = vault.get_vault_stats()
```

**Tipos de Sessão:**
- `HERMES_OBSIDIAN` - Interação Hermes ↔ Obsidian
- `FIX_HERMES` - Troubleshooting
- `CLAUDE_ANALYSIS` - Análise por Claude
- `TELEGRAM_INTERACTION` - Interação via Telegram

**Status:**
- `active` - Em uso
- `inactive` - Fechada
- `disconnected` - Sem conexão
- `error` - Erro

### D) Integrador Completo (`telegram_hermes_obsidian_integrator.py`)

```python
from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator

integrator = TelegramHermesObsidianIntegrator()

# Processar mensagem Telegram
result = integrator.process_telegram_message(
    user="danrcosta",
    message_text="Seu prompt",
    chat_id=12345
)

# Processar código
result = integrator.process_code_snippet(
    user="danrcosta",
    code="def foo(): pass",
    language="python"
)

# Obter sessões do usuário
sessions = integrator.get_user_sessions("danrcosta")

# Detalhes da sessão
details = integrator.get_session_details("session_id")

# Fechar sessão
integrator.close_session("session_id")

# Exportar para Markdown
path = integrator.export_session_to_obsidian("session_id")

# Stats
stats = integrator.get_vault_stats()
```

## 📊 Fluxo de Dados Completo

```
TELEGRAM MESSAGE
  ↓
telegram_webhook_server.py
  ├─ Extract: user, text, chat_id, file_id
  ├─ Download media (if photo/document)
  ├─ Call integrator.process_telegram_message()
  │   ↓
  │   Get or Create Session (Obsidian)
  │   ├─ Create session JSON
  │   ├─ Create session Markdown
  │   ├─ Add to vault
  │   ↓
  │   Add Message to Vault
  │   ├─ Store in session.messages[]
  │   ├─ Update session JSON
  │   ├─ Append to session Markdown
  │   ↓
  │   Send to Claude via Hermes
  │   ├─ Prepare payload
  │   ├─ POST to Hermes MCP
  │   ├─ Get response
  │   ↓
  │   Add Interaction to Vault
  │   ├─ Store in session.interactions[]
  │   ├─ Update session JSON
  │   ├─ Append to session Markdown
  │   ↓
  │   Return result
  │
  ├─ Send response back to Telegram
  │   └─ "✅ Message sent to Claude Code"
  │
OBSIDIAN VAULT UPDATED
  └─ New/Updated session with all data
```

## 🔧 Configuração de Ambiente

### `.env` Obrigatórios:
```env
TELEGRAM_BOT_TOKEN=8913080097:AAGaQaB0hFSK-sPyjNxn0f62mqjZIW9aQXI
HERMES_URL=http://100.86.232.77:8080
```

### `.env` Opcionais:
```env
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
WEBHOOK_URL=https://seu-dominio.com/webhook/telegram
HERMES_TIMEOUT=30
LOG_LEVEL=INFO
```

## 📁 Estrutura do Vault

```
obsidian_vault/
├── sessions/
│   ├── hermes_obsidian_1723123456.json
│   ├── hermes_obsidian_1723123456.md
│   ├── fix_hermes_1723123457.json
│   ├── fix_hermes_1723123457.md
│   ├── claude_analysis_1723123458.json
│   └── claude_analysis_1723123458.md
├── interactions/
│   └── [logs de interações]
├── archive/
│   ├── hermes_obsidian_1723123456_1723200000.json
│   └── hermes_obsidian_1723123456_1723200001.md
└── .metadata/
    └── vault_metadata.json
```

## 🧪 Testes

### 1. Testar Hermes Bridge

```bash
python hermes_claude_bridge.py
```

### 2. Testar Webhook Server

```bash
python telegram_webhook_server.py
curl http://localhost:8000/health
```

### 3. Testar Obsidian Manager

```bash
python obsidian_vault_manager.py
```

### 4. Testar Integrador Completo

```bash
python telegram_hermes_obsidian_integrator.py
```

## 📈 Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
```

Esperado:
```json
{
  "status": "healthy",
  "hermes": "connected",
  "timestamp": "2026-08-02T15:35:00.000000"
}
```

### Ver Sessões

```python
from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator
i = TelegramHermesObsidianIntegrator()
print(i.get_vault_stats())
```

## 🐛 Troubleshooting

### Hermes não conecta
```bash
curl http://100.86.232.77:8080/health
# Se timeout: verificar firewall/rede
```

### Webhook não recebe mensagens
```bash
# 1. Verificar server está rodando
curl http://localhost:8000/health

# 2. Verificar webhook configurado no Telegram
curl https://api.telegram.org/bot{TOKEN}/getWebhookInfo

# 3. Verificar logs no server
# (Deve mostrar 📨 Received update: ...)
```

### Obsidian não salva
```bash
# Verificar permissões
chmod -R 755 obsidian_vault/

# Verificar espaço em disco
df -h

# Verificar JSON encoding
python -c "import json; json.dumps({'test': 'utf-8 ñ'})"
```

## 🔐 Segurança

### Token Management
- Usar `.env` para armazenar tokens
- Não commitar `.env` (usar `.env.example`)
- Rotacionar tokens periodicamente

### Rate Limiting (Opcional)
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Validação de Input
- Mensagens truncadas em 500 chars (preview)
- Limite de tamanho de arquivo: 5MB
- Validação de tipo MIME

## 📦 Deployment

### Local (Development)
```bash
python telegram_webhook_server.py
```

### Production (ngrok - teste)
```bash
pip install ngrok
ngrok http 8000
# Use URL fornecida para webhook
```

### Production (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "telegram_webhook_server.py"]
```

## 📚 Documentação Detalhada

- [Passo A: Claude Bridge](STEP_A_CLAUDE_INTEGRATION.md)
- [Passo B: Telegram Webhook](STEP_B_TELEGRAM_WEBHOOK.md)
- [Passo C: Obsidian Integration](STEP_C_OBSIDIAN_INTEGRATION.md)
- [Visão Técnica Geral](TELEGRAM_INTEGRATION.md)

## 🎯 Próximas Etapas

1. ✅ **Passo A**: Script Python de Envio
2. ✅ **Passo B**: Webhook do Telegram
3. ✅ **Passo C**: Integração Obsidian
4. ⏳ **Deploy**: Colocar em produção
5. ⏳ **Monitoramento**: Dashboard de sessões
6. ⏳ **Automação**: Respostas automáticas
7. ⏳ **Backup**: Sistema de backup automático

## 📞 Suporte

Para problemas:
1. Verificar logs do server
2. Rodar health checks
3. Revisar documentação específica do passo
4. Verificar variáveis de ambiente

## 📄 Licença

Desenvolvido para danrcosta/test
