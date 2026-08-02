import OllamaClient from '../src/ollama-client.js';
import ObsidianClient from '../src/obsidian-client.js';

console.log('🧪 Running integration tests...\n');

async function testOllama() {
  console.log('Testing Ollama connection...');
  const ollama = new OllamaClient('http://localhost:11434');

  try {
    const isHealthy = await ollama.isHealthy();
    console.log(`  Status: ${isHealthy ? '✓ OK' : '✗ Failed'}`);

    if (isHealthy) {
      const models = await ollama.listModels();
      console.log(`  Models found: ${models.length}`);
      models.forEach(m => console.log(`    - ${m.name}`));
    }

    return isHealthy;
  } catch (error) {
    console.log(`  ✗ Error: ${error.message}`);
    return false;
  }
}

async function testObsidian() {
  console.log('\nTesting Obsidian vault...');
  const obsidian = new ObsidianClient('C:\\Users\\SERVER\\Hermes-Workspace\\Hermes-Vault');

  try {
    const exists = await obsidian.vaultExists();
    console.log(`  Vault exists: ${exists ? '✓ Yes' : '✗ No'}`);

    if (exists) {
      const stats = await obsidian.getVaultStats();
      console.log('  Folder stats:');
      Object.entries(stats).forEach(([folder, count]) => {
        console.log(`    - ${folder}: ${count} notes`);
      });
    }

    return exists;
  } catch (error) {
    console.log(`  ✗ Error: ${error.message}`);
    return false;
  }
}

async function runTests() {
  const ollamaOk = await testOllama();
  const obsidianOk = await testObsidian();

  console.log('\n📊 Summary:');
  console.log(`  Ollama: ${ollamaOk ? '✓ OK' : '✗ Failed'}`);
  console.log(`  Obsidian: ${obsidianOk ? '✓ OK' : '✗ Failed'}`);

  if (ollamaOk && obsidianOk) {
    console.log('\n✅ All systems ready!');
    process.exit(0);
  } else {
    console.log('\n⚠️  Some systems need attention');
    process.exit(1);
  }
}

runTests();
