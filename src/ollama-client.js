import axios from 'axios';

class OllamaClient {
  constructor(baseUrl = 'http://localhost:11434') {
    this.baseUrl = baseUrl;
    this.client = axios.create({ baseURL: this.baseUrl });
  }

  async query(model, prompt, options = {}) {
    try {
      const response = await this.client.post('/api/generate', {
        model,
        prompt,
        stream: false,
        ...options,
      });
      return response.data.response;
    } catch (error) {
      console.error(`Ollama error with model ${model}:`, error.message);
      throw error;
    }
  }

  async embed(text, model = 'nomic-embed-text:latest') {
    try {
      const response = await this.client.post('/api/embeddings', {
        model,
        prompt: text,
      });
      return response.data.embedding;
    } catch (error) {
      console.error('Embedding error:', error.message);
      throw error;
    }
  }

  async listModels() {
    try {
      const response = await this.client.get('/api/tags');
      return response.data.models;
    } catch (error) {
      console.error('Error listing models:', error.message);
      throw error;
    }
  }

  async isHealthy() {
    try {
      await this.client.get('/');
      return true;
    } catch {
      return false;
    }
  }
}

export default OllamaClient;
