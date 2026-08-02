# Passo A: Script de Envio para Claude Code

Script Python que envia dados, imagens e código do Telegram (via Hermes) para Claude Code.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso Básico

### 1. Enviar Prompt de Texto

```python
from hermes_claude_bridge import HermesClaudeBridge

bridge = HermesClaudeBridge()

# Enviar prompt simples
result = bridge.send_text_prompt(
    "Analise este código e sugira melhorias"
)
```

### 2. Enviar Código para Análise

```python
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

result = bridge.send_code(
    code,
    language="python",
    metadata={"source": "telegram"}
)
```

### 3. Enviar Imagem para Análise

```python
result = bridge.send_image_analysis(
    image_path="path/to/image.jpg",
    description="Analise este screenshot",
    metadata={"source": "telegram", "user": "danrcosta"}
)
```

### 4. Enviar Arquivo

```python
with open("file.txt", "r") as f:
    content = f.read()

result = bridge.send_file(
    file_path="file.txt",
    content=content
)
```

## Configuração

O script usa as seguintes variáveis padrão:

- **HERMES_URL**: `http://100.86.232.77:8080` (padrão)
- **TIMEOUT**: 30 segundos (padrão)

Para customizar, crie um arquivo `.env`:

```env
HERMES_URL=http://100.86.232.77:8080
HERMES_TIMEOUT=60
```

E carregue com:

```python
from dotenv import load_dotenv
import os

load_dotenv()
hermes_url = os.getenv("HERMES_URL")
```

## Estrutura da Resposta

Todas as chamadas retornam um dicionário com:

```json
{
  "success": true/false,
  "response": {
    "message": "Success message",
    "data": {}
  },
  "timestamp": "2026-08-02T15:30:00.000000",
  "error": "Error message (if failed)"
}
```

## Tipos de Conteúdo Suportados

| Tipo | Método | Descrição |
|------|--------|-----------|
| TEXT | `send_text_prompt()` | Prompts e instruções |
| CODE | `send_code()` | Snippets de código |
| IMAGE | `send_image_analysis()` | Imagens e screenshots |
| FILE | `send_file()` | Arquivos e documentos |

## Fluxo de Dados

```
Telegram Bot (@Danrcbh_bot)
    ↓
Hermes MCP Server (100.86.232.77:8080)
    ↓
hermes_claude_bridge.py (este script)
    ↓
Claude Code Session
    ↓
Resposta → Telegram
```

## Exemplo Completo

```python
from hermes_claude_bridge import HermesClaudeBridge
from datetime import datetime

# Inicializar bridge
bridge = HermesClaudeBridge(hermes_url="http://100.86.232.77:8080")

# Verificar saúde do Hermes
if not bridge.health_check():
    print("Hermes não está disponível!")
    exit(1)

# Enviar imagem com metadados
metadata = {
    "source": "telegram",
    "user": "danrcosta",
    "timestamp": datetime.now().isoformat(),
    "chat_id": "12345"
}

result = bridge.send_image_analysis(
    image_path="C:\\Users\\SERVER\\AppData\\Local\\hermes\\cache\\images\\img_d654554f7e77.jpg",
    description="Analise este screenshot do Hermes e Obsidian",
    metadata=metadata
)

if result["success"]:
    print(f"✅ Enviado com sucesso!")
    print(f"Resposta: {result['response']}")
else:
    print(f"❌ Erro: {result['error']}")
```

## Tratamento de Erros

```python
try:
    result = bridge.send_text_prompt("Your prompt")
    if result["success"]:
        print("Success!")
    else:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Exception: {e}")
```

## Integração com Webhook do Telegram

Ver `STEP_B_TELEGRAM_WEBHOOK.md` para integração com webhooks.

## Próximas Etapas

- **Passo B**: Implementar webhook do Telegram para capturar mensagens
- **Passo C**: Integração com Obsidian Vault para gerenciar sessões
