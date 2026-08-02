# Passo C: Integração com Obsidian Vault

Gerencia sessões, notas e interações entre Telegram, Hermes e Claude Code no Obsidian.

## Arquitetura Completa

```
Telegram (@Danrcbh_bot)
    ↓
telegram_webhook_server.py
    ↓
telegram_hermes_obsidian_integrator.py
    ├→ hermes_claude_bridge.py → Claude Code
    └→ obsidian_vault_manager.py → Obsidian Vault
    ↓
Obsidian (./obsidian_vault/)
```

## Estrutura do Vault

```
obsidian_vault/
├── sessions/
│   ├── hermes_obsidian_1723123456.json
│   ├── hermes_obsidian_1723123456.md
│   ├── fix_hermes_1723123457.json
│   ├── fix_hermes_1723123457.md
│   └── ...
├── interactions/
│   └── [interação logs]
├── archive/
│   └── [sessões exportadas]
└── .metadata/
    └── vault_metadata.json
```

## Tipos de Sessão

| Tipo | Descrição | Uso |
|------|-----------|-----|
| `hermes_obsidian` | Interação Hermes ↔ Obsidian | Perguntas sobre integração |
| `fix_hermes` | Correção de problemas | Troubleshooting |
| `claude_analysis` | Análise por Claude | Análise de código |
| `telegram_interaction` | Interação via Telegram | Conversas gerais |

## Status de Sessão

- **active**: Sessão em uso
- **inactive**: Sessão fechada
- **disconnected**: Conexão perdida (ex: Hermes offline)
- **error**: Erro durante processamento

## Uso Básico

### 1. Inicializar

```python
from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator

integrator = TelegramHermesObsidianIntegrator()
```

### 2. Processar Mensagem de Texto

```python
result = integrator.process_telegram_message(
    user="danrcosta",
    message_text="Analise este código",
    chat_id=12345
)

# Retorna:
# {
#   "success": true,
#   "session_id": "telegram_interaction_1723123456",
#   "vault_message": {...},
#   "hermes_result": {...}
# }
```

### 3. Processar Código

```python
code = """
def fibonacci(n):
    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
"""

result = integrator.process_code_snippet(
    user="danrcosta",
    code=code,
    language="python"
)
```

### 4. Obter Sessões do Usuário

```python
sessions = integrator.get_user_sessions("danrcosta")

# Retorna:
# {
#   "user": "danrcosta",
#   "total_sessions": 3,
#   "sessions": [
#     {
#       "id": "...",
#       "description": "...",
#       "status": "active",
#       "interactions_count": 5
#     }
#   ]
# }
```

### 5. Obter Detalhes da Sessão

```python
details = integrator.get_session_details("telegram_interaction_1723123456")

# Inclui: summary, messages, interactions, metadata
```

### 6. Fechar Sessão

```python
integrator.close_session("telegram_interaction_1723123456")
```

### 7. Exportar para Markdown

```python
export_path = integrator.export_session_to_obsidian("session_id")
# Salva em: archive/session_id_timestamp.md
```

### 8. Estatísticas do Vault

```python
stats = integrator.get_vault_stats()

# Retorna:
# {
#   "total_sessions": 10,
#   "active_sessions": 3,
#   "total_interactions": 45,
#   "sessions_by_type": {...},
#   "interactions_by_type": {...}
# }
```

## Fluxo Completo de Mensagem

```
1. Telegram recebe mensagem
   ↓
2. webhook_server.py processa
   ↓
3. telegram_hermes_obsidian_integrator.py route
   ├→ Cria/obtém session no Obsidian
   ├→ Adiciona message à vault
   ├→ Envia para Claude via Hermes Bridge
   ├→ Adiciona interaction à vault
   └→ Retorna resultado
   ↓
4. telegram_webhook_server.py envia resposta ao Telegram
   ↓
5. Usuario recebe no Telegram
   ↓
6. Tudo armazenado no Obsidian Vault
```

## Arquivo JSON da Sessão

Cada sessão é armazenada como JSON:

```json
{
  "id": "hermes_obsidian_1723123456",
  "type": "hermes_obsidian",
  "status": "active",
  "description": "Hermes e Obsidian",
  "user": "danrcosta",
  "created_at": "2026-08-02T15:35:00.000000",
  "updated_at": "2026-08-02T15:40:00.000000",
  "interactions": [
    {
      "id": "interaction_1723123456000",
      "type": "text",
      "source": "telegram",
      "content": "Solicita mais detalhes sobre a interação...",
      "timestamp": "2026-08-02T15:35:10.000000",
      "metadata": {...}
    }
  ],
  "messages": [
    {
      "id": "msg_1723123456000",
      "role": "user",
      "content": "Como integrar Hermes com Obsidian?",
      "source": "telegram",
      "timestamp": "2026-08-02T15:35:10.000000"
    }
  ],
  "metadata": {
    "topic": "Integração Hermes-Obsidian"
  }
}
```

## Arquivo Markdown da Sessão

Cada sessão também tem um arquivo `.md`:

```markdown
---
id: hermes_obsidian_1723123456
type: hermes_obsidian
status: active
created: 2026-08-02T15:35:00.000000
user: danrcosta
---

# Hermes e Obsidian

## Status
**active**

## Information
- **Type**: hermes_obsidian
- **User**: danrcosta
- **Created**: 2026-08-02T15:35:00.000000

## Interactions

### TEXT - 2026-08-02T15:35:10.000000
**Source**: telegram

Solicita mais detalhes sobre a interação entre Hermes e o Vault de notas.

## Messages

## Notes
```

## Integração com Webhook

Modificar `telegram_webhook_server.py` para usar o integrador:

```python
from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator

integrator = TelegramHermesObsidianIntegrator()

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    update = await request.json()
    message = update["message"]
    
    # Usar integrador
    result = integrator.process_telegram_message(
        user=message["from"]["username"],
        message_text=message["text"],
        chat_id=message["chat"]["id"]
    )
    
    return JSONResponse({"ok": result["success"]})
```

## Dashboard de Sessões

Ver todas as sessões ativas:

```python
all_sessions = vault_manager.list_sessions(status=SessionStatus.ACTIVE)

for session in all_sessions:
    summary = vault_manager.get_session_summary(session["id"])
    print(f"{summary['description']} - {summary['interactions_count']} interactions")
```

## Busca e Filtros

```python
# Sessões por tipo
hermes_sessions = vault_manager.list_sessions(
    session_type=SessionType.HERMES_OBSIDIAN
)

# Sessões por status
active = vault_manager.list_sessions(
    status=SessionStatus.ACTIVE
)

# Sessões por usuário (manual filter)
user_sessions = [s for s in vault_manager.list_sessions() if s["user"] == "danrcosta"]
```

## Monitoramento

```python
# Verificar saúde
stats = integrator.get_vault_stats()
print(f"Sessions: {stats['total_sessions']}")
print(f"Active: {stats['active_sessions']}")
print(f"Interactions: {stats['total_interactions']}")

# Limpar sessões antigas (manual)
import shutil
shutil.rmtree("./obsidian_vault/archive/*")  # Limpar archive
```

## Backup do Vault

```bash
# Backup manual
cp -r obsidian_vault obsidian_vault_backup_$(date +%s)

# Exportar todas as sessões
python -c "
from telegram_hermes_obsidian_integrator import TelegramHermesObsidianIntegrator
i = TelegramHermesObsidianIntegrator()
for s in i.vault_manager.list_sessions():
    i.export_session_to_obsidian(s['id'])
"
```

## Próximas Etapas

1. Integrar com webhook do Telegram
2. Adicionar suporte a Obsidian API (opcional)
3. Dashboard web para visualizar sessões
4. Backup automático de sessões
5. Sincronização multi-dispositivo (opcional)

## Troubleshooting

### Vault não criado
```python
# Verificar permissões
import os
os.chmod("./obsidian_vault", 0o755)
```

### Sessões não salvam
- Verificar espaço em disco
- Verificar permissões de arquivo
- Verificar JSON encoding

### Conflitos de ID
- IDs são baseados em timestamp e únicos
- Se conflitos ocorrem, adicione random suffix

## Conclusão

Sistema completo de gerenciamento de sessões que conecta:
- 📱 Telegram (entrada)
- 🧠 Hermes (processamento)
- 📝 Obsidian (armazenamento)
- 🤖 Claude Code (análise)
