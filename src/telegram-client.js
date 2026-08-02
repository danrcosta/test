import TelegramBot from 'node-telegram-bot-api';

class TelegramClient {
  constructor(token, options = {}) {
    this.bot = new TelegramBot(token, { polling: true });
    this.handlers = new Map();
    this.setupDefaultHandlers();
  }

  setupDefaultHandlers() {
    this.bot.onText(/\/start/, (msg) => {
      this.handleMessage('start', msg);
    });

    this.bot.onText(/\/help/, (msg) => {
      this.handleMessage('help', msg);
    });

    this.bot.on('message', (msg) => {
      if (!msg.text?.startsWith('/')) {
        this.handleMessage('text', msg);
      }
    });
  }

  on(command, callback) {
    this.handlers.set(command, callback);
  }

  async handleMessage(type, msg) {
    const handler = this.handlers.get(type);
    if (handler) {
      await handler(msg, this);
    }
  }

  async sendMessage(chatId, text, options = {}) {
    try {
      return await this.bot.sendMessage(chatId, text, options);
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async sendMarkdown(chatId, text) {
    return this.sendMessage(chatId, text, { parse_mode: 'Markdown' });
  }

  async sendHTML(chatId, text) {
    return this.sendMessage(chatId, text, { parse_mode: 'HTML' });
  }

  async answerInlineQuery(inlineQueryId, results) {
    try {
      return await this.bot.answerInlineQuery(inlineQueryId, results);
    } catch (error) {
      console.error('Error answering inline query:', error);
      throw error;
    }
  }

  async editMessage(chatId, messageId, text, options = {}) {
    try {
      return await this.bot.editMessageText(text, {
        chat_id: chatId,
        message_id: messageId,
        ...options,
      });
    } catch (error) {
      console.error('Error editing message:', error);
      throw error;
    }
  }

  async deleteMessage(chatId, messageId) {
    try {
      return await this.bot.deleteMessage(chatId, messageId);
    } catch (error) {
      console.error('Error deleting message:', error);
      throw error;
    }
  }

  close() {
    this.bot.stopPolling();
  }
}

export default TelegramClient;
