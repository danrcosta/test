# Passo B: Webhook do Telegram

Servidor que recebe mensagens do Telegram e as envia para Claude Code via Hermes.

## Arquitetura

```
Telegram Bot (@Danrcbh_bot)
    ↓ (webhook POST)
telegram_webhook_server.py (FastAPI)
    ↓
hermes_claude_bridge.py
    ↓
Hermes MCP (100.86.232.77:8080)
    ↓
Claude Code
```

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

### 1. Variáveis de Ambiente

Crie arquivo `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
HERMES_URL=http://100.86.232.77:8080
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
```

### 2. Iniciar Servidor

```bash
python telegram_webhook_server.py
```

Output esperado:
```
🚀 Starting Telegram Webhook Server on 0.0.0.0:8000
📍 Webhook path: /webhook/telegram
🤖 Bot token configured: <bot-id>...
```

### 3. Configurar Webhook no Telegram

Você pode usar a API do Telegram para registrar o webhook:

```bash
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://seu-dominio.com/webhook/telegram"}'
```

Ou usar o endpoint POST `/set-webhook` do servidor:

```bash
curl -X POST http://localhost:8000/set-webhook?webhook_url=https://seu-dominio.com/webhook/telegram
```

## Tipos de Mensagens Suportadas

### 1. Mensagens de Texto

```
User: "Analise este código"
Bot: "✅ Mensagem enviada para Claude Code com sucesso!"
```

### 2. Imagens/Screenshots

```
User: [envia imagem]
Bot: "✅ Imagem enviada para Claude Code!"
```

### 3. Comandos de Código

```
User: /code def hello(): return "world"
Bot: "✅ Código enviado para Claude Code!"
```

### 4. Documentos/Arquivos

```
User: [envia arquivo.txt]
Bot: "✅ Arquivo 'arquivo.txt' enviado para Claude Code!"
```

## Endpoints

### GET `/`
Status do servidor

```bash
curl http://localhost:8000/
```

Resposta:
```json
{
  "service": "Telegram to Claude Code Bridge",
  "version": "1.0",
  "webhook_path": "/webhook/telegram",
  "status": "running"
}
```

### GET `/health`
Verifica saúde do Hermes

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "healthy",
  "hermes": "connected",
  "timestamp": "2026-08-02T15:35:00.000000"
}
```

### POST `/webhook/telegram`
Webhook que Telegram envia mensagens (automático)

### POST `/set-webhook`
Registra webhook no Telegram

```bash
curl -X POST "http://localhost:8000/set-webhook?webhook_url=https://seu-dominio.com/webhook/telegram"
```

## Fluxo de Processamento

### Mensagem de Texto

```
[Telegram] "Analise este código"
    ↓
[webhook_server] process_text_message()
    ↓
[hermes_bridge] send_text_prompt()
    ↓
[Hermes] recebe no MCP
    ↓
[Claude Code] processa e responde
    ↓
[Telegram] envia resposta ao usuário
```

### Foto/Imagem

```
[Telegram] [envia imagem.jpg]
    ↓
[webhook_server] process_photo_message()
    ↓
[telegram_webhook_server] get_file() → download
    ↓
[MEDIA_CACHE_DIR] armazena localmente
    ↓
[hermes_bridge] send_image_analysis()
    ↓
[Hermes + Claude Code] análise
    ↓
[Telegram] resposta
```

## Cache de Mídia

Arquivos baixados do Telegram são salvos em:
```
./telegram_media_cache/
```

Estrutura:
```
telegram_media_cache/
├── img_d654554f7e77.jpg
├── documento.pdf
└── screenshot.png
```

## Tratamento de Erros

O servidor trata automaticamente:

- ✅ Hermes indisponível → responde com erro ao usuário
- ✅ Arquivo não baixável → notifica usuário
- ✅ Tipo de mensagem não suportado → ignora silenciosamente
- ✅ Timeout → responde com erro

## Segurança

### Validação de Token

O servidor valida o token do Telegram:
- Apenas requisições do Telegram são processadas
- Verificação via `signature` (opcional, pode ser adicionada)

### Limites de Arquivo

Padrão do Telegram:
- Documentos: até 2GB
- Fotos: até 10MB
- Recomendado limitar a ~5MB por segurança

### Rate Limiting

Adicione rate limiting via middleware se necessário:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

## Logs

O servidor registra tudo:

```
2026-08-02 15:35:45 - telegram_webhook_server - INFO - 📝 Text from @danrcosta: Analise este código
2026-08-02 15:35:46 - hermes_claude_bridge - INFO - ✅ Successfully sent text to Claude Code
```

## Troubleshooting

### Webhook não recebe mensagens

1. Verifique se o servidor está rodando:
   ```bash
   curl http://localhost:8000/health
   ```

2. Valide webhook no Telegram:
   ```bash
   curl https://api.telegram.org/bot{TOKEN}/getWebhookInfo
   ```

3. Verifique firewall/porta 8000

### Imagens não baixam

1. Confirme token válido
2. Verifique permissões de escrita em `./telegram_media_cache/`
3. Verifique conectividade com API do Telegram

### Hermes não recebe mensagens

1. Verifique saúde: `curl http://localhost:8000/health`
2. Confirme URL: `http://100.86.232.77:8080`
3. Verifique MCP configuration

## Próximas Etapas

- **Passo C**: Integração com Obsidian Vault para gerenciar sessões
- Deploy em produção (ngrok para teste local)
- Adicionar autenticação e rate limiting
