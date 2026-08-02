import fs from 'fs/promises';
import path from 'path';

class ObsidianClient {
  constructor(vaultPath) {
    this.vaultPath = vaultPath;
    this.folders = {
      inbox: '00-inbox',
      daily: '01-daily',
      projects: '02-projects',
      people: '03-people',
      knowledge: '04-knowledge',
      hermes: '05-hermes',
      financial: '06-financial',
      health: '07-health',
      templates: '08-templates',
      attachments: '09-attachments',
    };
  }

  async saveToDailyNote(content, date = new Date()) {
    const dateStr = date.toISOString().split('T')[0];
    const filename = `${dateStr}.md`;
    const filepath = path.join(this.vaultPath, this.folders.daily, filename);

    const header = `# ${dateStr}\n\n`;
    const fullContent = `${header}${content}`;

    try {
      await fs.writeFile(filepath, fullContent, 'utf-8');
      return { success: true, filepath };
    } catch (error) {
      console.error('Error saving to daily note:', error);
      throw error;
    }
  }

  async saveToInbox(title, content, tags = []) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${timestamp}-${title.replace(/\s+/g, '-')}.md`;
    const filepath = path.join(this.vaultPath, this.folders.inbox, filename);

    const tagsStr = tags.length ? `\ntags: [${tags.join(', ')}]` : '';
    const fullContent = `# ${title}\n\nAdded: ${new Date().toISOString()}${tagsStr}\n\n${content}`;

    try {
      await fs.writeFile(filepath, fullContent, 'utf-8');
      return { success: true, filepath };
    } catch (error) {
      console.error('Error saving to inbox:', error);
      throw error;
    }
  }

  async readFile(folderKey, filename) {
    const folder = this.folders[folderKey];
    const filepath = path.join(this.vaultPath, folder, filename);

    try {
      const content = await fs.readFile(filepath, 'utf-8');
      return content;
    } catch (error) {
      console.error(`Error reading file ${filename}:`, error);
      throw error;
    }
  }

  async listFiles(folderKey) {
    const folder = this.folders[folderKey];
    const folderPath = path.join(this.vaultPath, folder);

    try {
      const files = await fs.readdir(folderPath);
      return files.filter(f => f.endsWith('.md'));
    } catch (error) {
      console.error(`Error listing files in ${folderKey}:`, error);
      throw error;
    }
  }

  async createNote(folderKey, title, content, metadata = {}) {
    const folder = this.folders[folderKey];
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${timestamp}-${title.replace(/\s+/g, '-')}.md`;
    const filepath = path.join(this.vaultPath, folder, filename);

    let fullContent = `# ${title}\n\n`;
    fullContent += `**Created**: ${new Date().toISOString()}\n`;

    if (metadata.tags) {
      fullContent += `**Tags**: ${metadata.tags.join(', ')}\n`;
    }
    if (metadata.related) {
      fullContent += `**Related**: ${metadata.related.join(', ')}\n`;
    }

    fullContent += `\n---\n\n${content}`;

    try {
      await fs.writeFile(filepath, fullContent, 'utf-8');
      return { success: true, filepath, filename };
    } catch (error) {
      console.error('Error creating note:', error);
      throw error;
    }
  }

  async vaultExists() {
    try {
      await fs.access(this.vaultPath);
      return true;
    } catch {
      return false;
    }
  }

  async getVaultStats() {
    const stats = {};

    try {
      for (const [key, folder] of Object.entries(this.folders)) {
        const folderPath = path.join(this.vaultPath, folder);
        try {
          const files = await fs.readdir(folderPath);
          stats[key] = files.filter(f => f.endsWith('.md')).length;
        } catch {
          stats[key] = 0;
        }
      }
      return stats;
    } catch (error) {
      console.error('Error getting vault stats:', error);
      throw error;
    }
  }
}

export default ObsidianClient;
