import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import Hermes from './hermes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function loadConfig() {
  const configPath = path.join(__dirname, '../config/hermes-config.json');
  const configData = await fs.readFile(configPath, 'utf-8');
  return JSON.parse(configData);
}

async function main() {
  try {
    console.clear();
    console.log('╔════════════════════════════════════════╗');
    console.log('║  🚀 HERMES - Central Orchestration Hub║');
    console.log('║  Powered by Nous Agent + Ollama         ║');
    console.log('╚════════════════════════════════════════╝\n');

    const config = await loadConfig();

    const hermes = new Hermes(config);
    await hermes.initialize();

    console.log('💬 Telegram bot listening for commands...');
    console.log('📁 Connected to Obsidian vault');
    console.log('🧠 Local Ollama models ready\n');
    console.log('Press Ctrl+C to stop\n');

    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n\nShutting down Hermes...');
      await hermes.close();
      process.exit(0);
    });
  } catch (error) {
    console.error('❌ Fatal error:', error);
    process.exit(1);
  }
}

main();
