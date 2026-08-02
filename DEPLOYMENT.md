# 🚀 Deployment Guide

Complete deployment guide for Telegram + Hermes + Claude Code Integration

---

## 📋 Prerequisites

- Docker installed (v20.10+)
- Docker Compose installed (v1.29+)
- Telegram Bot Token (from @BotFather)
- Hermes server running at `100.86.232.77:8080`
- (Optional) Domain for production deployment

---

## 🏠 Local Deployment

### Option 1: Direct Python (Development)

```bash
# 1. Clone/setup repository
cd /path/to/repo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your values

# 4. Start webhook server
python telegram_webhook_server.py

# Output:
# 🚀 Starting Telegram Webhook Server on 0.0.0.0:8000
# 📍 Webhook path: /webhook/telegram
# 🤖 Bot token configured: 8913080097...
```

### Option 2: Docker (Recommended)

```bash
# 1. Make deploy script executable
chmod +x deploy.sh

# 2. Run deployment
./deploy.sh

# 3. Follow prompts to configure .env

# Output:
# ✅ Docker image built successfully
# ✅ Containers started successfully
# ✅ Webhook server is healthy
# 📍 Webhook URL: http://localhost:8000
```

---

## 🌐 Production Deployment

### Step 1: Configure Environment

```bash
# Edit .env with production values
TELEGRAM_BOT_TOKEN=your_bot_token_here
HERMES_URL=http://100.86.232.77:8080
WEBHOOK_URL=https://your-domain.com
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
```

### Step 2: Setup Domain & SSL

```bash
# Using Let's Encrypt with Certbot
certbot certonly --standalone -d your-domain.com

# Or manually create certs directory
mkdir -p certs
# Place your SSL certificates in certs/
```

### Step 3: Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Verify deployment
docker ps
docker logs telegram-hermes-webhook

# Health check
curl https://your-domain.com/health
```

### Step 4: Configure Telegram Webhook

```bash
# Set webhook on Telegram
curl -X POST "http://localhost:8000/set-webhook?webhook_url=https://your-domain.com/webhook/telegram"

# Verify webhook
curl -s https://api.telegram.org/bot{TOKEN}/getWebhookInfo | jq .
```

---

## 📊 Deployment Architecture

```
┌─────────────────┐
│   Telegram      │
│  Bot Server     │
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────────────────────────────┐
│         Nginx (Reverse Proxy)           │
│    (SSL Termination, Load Balancing)    │
└────────────┬────────────────────────────┘
             │ HTTP (Internal)
             ↓
┌──────────────────────────────────────────────┐
│    Docker Container (telegram-hermes-webhook)│
├──────────────────────────────────────────────┤
│  • FastAPI webhook server (port 8000)        │
│  • Hermes bridge integration                 │
│  • Obsidian vault management                 │
│  • GitHub automation                         │
└────────┬─────────────────────────────────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ↓         ↓            ↓          ↓
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────┐
│ Hermes │ │Obsidian│ │ GitHub   │ │ Logs │
│ (MCP)  │ │ Vault  │ │ Actions  │ │      │
└────────┘ └────────┘ └──────────┘ └──────┘
```

---

## 🔧 Configuration Files

### docker-compose.yml

```yaml
version: '3.8'
services:
  telegram-hermes-webhook:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - HERMES_URL=${HERMES_URL}
    volumes:
      - ./obsidian_vault:/app/obsidian_vault
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "telegram_webhook_server.py"]
```

---

## 🧪 Testing Deployment

### 1. Health Check

```bash
# Local
curl http://localhost:8000/health

# Production
curl https://your-domain.com/health

# Expected response:
# {
#   "status": "healthy",
#   "hermes": "connected",
#   "timestamp": "2026-08-02T15:38:00.000000"
# }
```

### 2. Send Test Message

```bash
# Via Telegram
Send message to @Danrcbh_bot:
"Test message from deployment"

# Expected response:
"✅ Mensagem enviada para Claude Code com sucesso!"

# Check logs
docker logs telegram-hermes-webhook
```

### 3. Monitor Containers

```bash
# View running containers
docker ps

# View logs (live)
docker logs -f telegram-hermes-webhook

# View system stats
docker stats telegram-hermes-webhook

# View vault
ls -la obsidian_vault/sessions/
```

---

## 📈 Monitoring & Maintenance

### View Logs

```bash
# Last 100 lines
docker logs --tail 100 telegram-hermes-webhook

# Follow logs (live)
docker logs -f telegram-hermes-webhook

# Logs with timestamps
docker logs -t telegram-hermes-webhook | tail -50
```

### Health Monitoring

```bash
# Setup monitoring script
while true; do
  STATUS=$(curl -s http://localhost:8000/health | jq -r .status)
  echo "$(date): $STATUS"
  sleep 300  # Check every 5 minutes
done
```

### Vault Management

```bash
# View sessions
ls obsidian_vault/sessions/

# Export session
python -c "
from obsidian_vault_manager import ObsidianVaultManager
vault = ObsidianVaultManager()
vault.export_session('session_id_here')
"

# Backup vault
tar -czf obsidian_vault_backup_$(date +%s).tar.gz obsidian_vault/
```

---

## 🔄 Scaling

### Horizontal Scaling (Multiple Instances)

```bash
# Edit docker-compose.yml
services:
  telegram-hermes-webhook-1:
    ...
    ports:
      - "8001:8000"
  
  telegram-hermes-webhook-2:
    ...
    ports:
      - "8002:8000"

# Nginx load balancing
upstream webhook_backend {
    server telegram-hermes-webhook-1:8000;
    server telegram-hermes-webhook-2:8000;
    server telegram-hermes-webhook-3:8000;
}

server {
    listen 443 ssl;
    location /webhook/telegram {
        proxy_pass http://webhook_backend;
    }
}
```

### Vertical Scaling (Increase Resources)

```bash
# Edit docker-compose.yml
services:
  telegram-hermes-webhook:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs telegram-hermes-webhook

# Common issues:
# - Port 8000 already in use
#   → Change WEBHOOK_PORT in .env

# - Missing environment variables
#   → Check .env file

# - Hermes not reachable
#   → Verify HERMES_URL and network connectivity
```

### Webhook Not Receiving Messages

```bash
# 1. Verify webhook is configured
curl -s https://api.telegram.org/bot{TOKEN}/getWebhookInfo | jq .

# 2. Check if webhook URL is correct
# Should point to your domain/webhook/telegram

# 3. Test webhook endpoint
curl -X POST http://localhost:8000/webhook/telegram \
  -H "Content-Type: application/json" \
  -d '{"update_id": 123, "message": {"text": "test"}}'
```

### High Memory Usage

```bash
# Check memory consumption
docker stats telegram-hermes-webhook

# Clean up old sessions
python -c "
import shutil
shutil.rmtree('./obsidian_vault/archive')
# Then recreate directory
"

# Restart container
docker restart telegram-hermes-webhook
```

---

## 🛡️ Security

### Secrets Management

```bash
# Don't commit .env
echo ".env" >> .gitignore

# Use secure secret management
# Option 1: Docker Secrets (Swarm)
# Option 2: Environment variables (K8s)
# Option 3: HashiCorp Vault
```

### SSL/TLS

```bash
# Always use HTTPS in production
# Generate certificates via Let's Encrypt

certbot certonly --standalone -d your-domain.com
certbot renew --dry-run  # Test renewal
```

### Rate Limiting

```python
# Add to telegram_webhook_server.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post(WEBHOOK_PATH)
@limiter.limit("100/minute")
async def webhook(request: Request):
    ...
```

---

## 📅 Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup vault
tar -czf $BACKUP_DIR/vault_$TIMESTAMP.tar.gz obsidian_vault/

# Keep only last 30 days
find $BACKUP_DIR -name "vault_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/vault_$TIMESTAMP.tar.gz"
```

### Scheduled Backups (Cron)

```bash
# Add to crontab (0 2 * * * = 2 AM daily)
0 2 * * * /path/to/backup.sh
```

---

## 📊 Performance Tuning

### Optimize FastAPI

```python
# telegram_webhook_server.py
app = FastAPI(
    title="Telegram Webhook",
    docs_url=None,  # Disable docs in production
    openapi_url=None,
    redoc_url=None
)

# Use async for I/O operations
async def process_message():
    ...
```

### Optimize Database (Obsidian Vault)

```bash
# Compress old sessions
find obsidian_vault/archive -name "*.json" -exec gzip {} \;

# Index sessions for faster search
python -c "
from obsidian_vault_manager import ObsidianVaultManager
vault = ObsidianVaultManager()
index = vault.create_interaction_index()
"
```

---

## ✅ Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] .env configured with all required variables
- [ ] SSL certificates obtained (for production)
- [ ] Telegram bot token set
- [ ] Hermes server tested and accessible
- [ ] deploy.sh executed successfully
- [ ] Health check returning 200 OK
- [ ] Test message sent to bot
- [ ] Logs monitored and no errors
- [ ] Obsidian vault created and writable
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team trained on deployment

---

## 📞 Support

For deployment issues:

1. Check logs: `docker logs telegram-hermes-webhook`
2. Run health check: `curl http://localhost:8000/health`
3. Test Hermes connectivity: `curl http://100.86.232.77:8080/health`
4. Review this guide: DEPLOYMENT.md
5. Check CLAUDE.md for project overview

---

**Deployment Date**: 2026-08-02  
**Version**: 1.0  
**Status**: ✅ Ready for Production
