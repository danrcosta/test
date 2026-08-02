import OllamaClient from './ollama-client.js';
import ObsidianClient from './obsidian-client.js';
import TelegramClient from './telegram-client.js';

class Hermes {
  constructor(config) {
    this.config = config;
    this.ollama = null;
    this.obsidian = null;
    this.telegram = null;
    this.isInitialized = false;
  }

  async initialize() {
    try {
      console.log('🔨 Initializing Hermes...');

      // Initialize Ollama
      if (this.config.ollama?.enabled) {
        this.ollama = new OllamaClient(this.config.ollama.baseUrl);
        const isHealthy = await this.ollama.isHealthy();
        if (isHealthy) {
          console.log('✓ Ollama connected');
        } else {
          console.warn('⚠ Ollama unreachable');
        }
      }

      // Initialize Obsidian
      if (this.config.obsidian?.enabled) {
        this.obsidian = new ObsidianClient(this.config.obsidian.vaultPath);
        const exists = await this.obsidian.vaultExists();
        if (exists) {
          const stats = await this.obsidian.getVaultStats();
          console.log('✓ Obsidian vault connected');
          console.log('  Vault stats:', stats);
        } else {
          console.warn('⚠ Obsidian vault not found');
        }
      }

      // Initialize Telegram (optional)
      if (this.config.telegram?.enabled && this.config.telegram.hermesBotToken) {
        this.telegram = new TelegramClient(this.config.telegram.hermesBotToken);
        console.log('✓ Telegram bot connected');
        this.setupTelegramHandlers();
      }

      this.isInitialized = true;
      console.log('✓ Hermes initialized successfully\n');
    } catch (error) {
      console.error('❌ Initialization error:', error);
      throw error;
    }
  }

  setupTelegramHandlers() {
    this.telegram.on('start', async (msg) => {
      const welcome = `
🚀 **Hermes Central Hub**

I'm your AI orchestration agent. Use these commands:

**/ask** - Query with general model
**/think** - Deep reasoning (deepseek-r1)
**/code** - Code generation
**/search** - Search Obsidian vault
**/note** - Save to inbox
**/status** - System status

Type **/help** for more info.
`;
      await this.telegram.sendMarkdown(msg.chat.id, welcome);
    });

    this.telegram.on('help', async (msg) => {
      const help = `
📚 **Hermes Commands**

**/ask [text]** - Ask a general question
**/think [text]** - Complex reasoning
**/code [text]** - Generate code
**/search [query]** - Search notes
**/note [text]** - Add to inbox
**/status** - System health

Example: \`/ask What is Node.js?\`
`;
      await this.telegram.sendMarkdown(msg.chat.id, help);
    });

    this.telegram.on('text', async (msg) => {
      const text = msg.text.trim();

      if (text.startsWith('/ask ')) {
        await this.handleAsk(msg, text.substring(5));
      } else if (text.startsWith('/think ')) {
        await this.handleThink(msg, text.substring(7));
      } else if (text.startsWith('/code ')) {
        await this.handleCode(msg, text.substring(6));
      } else if (text.startsWith('/note ')) {
        await this.handleNote(msg, text.substring(6));
      } else if (text === '/status') {
        await this.handleStatus(msg);
      }
    });
  }

  async handleAsk(msg, query) {
    try {
      await this.telegram.sendMessage(
        msg.chat.id,
        '⏳ Thinking with Hermes...',
      );

      const model = this.config.ollama.models.general;
      const response = await this.ollama.query(model, query);

      await this.telegram.sendMarkdown(msg.chat.id, `*Answer:*\n\n${response}`);

      // Save to daily note
      if (this.obsidian) {
        const note = `**Q**: ${query}\n**A**: ${response}`;
        await this.obsidian.saveToDailyNote(note);
      }
    } catch (error) {
      await this.telegram.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  }

  async handleThink(msg, query) {
    try {
      await this.telegram.sendMessage(
        msg.chat.id,
        '🧠 Deep thinking (this may take a while)...',
      );

      const model = this.config.ollama.models.reasoning;
      const response = await this.ollama.query(model, query);

      await this.telegram.sendMarkdown(msg.chat.id, `*Deep Analysis:*\n\n${response}`);

      // Save to knowledge folder
      if (this.obsidian) {
        await this.obsidian.createNote('knowledge', query, response, {
          tags: ['reasoning', 'hermes'],
        });
      }
    } catch (error) {
      await this.telegram.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  }

  async handleCode(msg, query) {
    try {
      await this.telegram.sendMessage(msg.chat.id, '🤖 Generating code...');

      const model = this.config.ollama.models.coding;
      const response = await this.ollama.query(model, query);

      await this.telegram.sendMarkdown(msg.chat.id, `*Code:*\n\n\`\`\`\n${response}\n\`\`\``);

      // Save to projects folder
      if (this.obsidian) {
        await this.obsidian.createNote('projects', 'Code Snippet', response, {
          tags: ['code', 'hermes'],
        });
      }
    } catch (error) {
      await this.telegram.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  }

  async handleNote(msg, text) {
    try {
      if (this.obsidian) {
        const result = await this.obsidian.saveToInbox(
          'Telegram Note',
          text,
          ['telegram', 'inbox'],
        );
        await this.telegram.sendMessage(msg.chat.id, '✓ Saved to inbox');
      }
    } catch (error) {
      await this.telegram.sendMessage(msg.chat.id, `❌ Error: ${error.message}`);
    }
  }

  async handleStatus(msg) {
    let status = '📊 **System Status**\n\n';

    if (this.ollama) {
      const isHealthy = await this.ollama.isHealthy();
      status += `Ollama: ${isHealthy ? '✓ Online' : '❌ Offline'}\n`;
    }

    if (this.obsidian) {
      const exists = await this.obsidian.vaultExists();
      status += `Obsidian: ${exists ? '✓ Connected' : '❌ Disconnected'}\n`;
      if (exists) {
        const stats = await this.obsidian.getVaultStats();
        status += `  Notes: ${JSON.stringify(stats).substring(0, 50)}...\n`;
      }
    }

    status += `\nTelegram: ✓ Connected`;

    await this.telegram.sendMarkdown(msg.chat.id, status);
  }

  async query(prompt, options = {}) {
    if (!this.ollama) {
      throw new Error('Ollama not initialized');
    }

    const model = options.model || this.config.ollama.models.general;
    return this.ollama.query(model, prompt, options);
  }

  async close() {
    if (this.telegram) {
      this.telegram.close();
    }
    console.log('Hermes closed');
  }
}

export default Hermes;
