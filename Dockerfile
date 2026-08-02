FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY hermes_claude_bridge.py .
COPY telegram_webhook_server.py .
COPY obsidian_vault_manager.py .
COPY telegram_hermes_obsidian_integrator.py .
COPY hermes_github_automation.py .
COPY hermes_github_obsidian_bridge.py .

# Create vault directory
RUN mkdir -p obsidian_vault

# Expose webhook port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run webhook server
CMD ["python", "telegram_webhook_server.py"]
