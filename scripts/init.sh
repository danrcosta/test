#!/bin/bash
# Hermes initialization script

echo "🚀 Initializing Hermes..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "✓ Node.js $(node --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check Ollama
echo "🧠 Checking Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
    echo "  Available models:"
    curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4
else
    echo "⚠️  Ollama not running at http://localhost:11434"
    echo "   Start Ollama before running Hermes"
fi

# Check Obsidian vault path
VAULT_PATH="$OBSIDIAN_VAULT_PATH"
if [ -d "$VAULT_PATH" ]; then
    echo "✓ Obsidian vault found at $VAULT_PATH"
else
    echo "⚠️  Obsidian vault not found"
    echo "   Configure path in config/hermes-config.json"
fi

echo ""
echo "✅ Initialization complete!"
echo "Run 'npm start' to begin"
