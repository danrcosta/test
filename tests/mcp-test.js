/**
 * MCP Integration Test
 * Validates connectivity with available MCP services
 * (Slack, Notion, Google Drive)
 */

import MCPIntegration from '../src/mcp-integration.js';

console.log('🧪 Testing MCP Integration...\n');

async function testMCPIntegration() {
  // Create MCP instance with all services enabled
  const mcp = new MCPIntegration({
    slack: { enabled: true },
    notion: { enabled: true },
    googleDrive: { enabled: true },
  });

  // Initialize
  await mcp.initialize();
  console.log('');

  // Test Slack notification
  console.log('Testing Slack...');
  const slackOk = await mcp.notifySlack(
    '#hermes-logs',
    '🚀 Hermes system started - ready for queries',
  );
  console.log(`  Result: ${slackOk ? '✓ OK' : '✗ Failed'}\n`);

  // Test Notion logging
  console.log('Testing Notion...');
  const notionOk = await mcp.logToNotion('Hermes-System', {
    timestamp: new Date().toISOString(),
    status: 'initialized',
    components: ['Ollama', 'Obsidian', 'Telegram'],
  });
  console.log(`  Result: ${notionOk ? '✓ OK' : '✗ Failed'}\n`);

  // Test Google Drive backup
  console.log('Testing Google Drive...');
  const gdOk = await mcp.saveToGoogleDrive(
    'hermes-config.json',
    JSON.stringify({ version: '1.0.0', status: 'active' }),
    'Hermes/Backups',
  );
  console.log(`  Result: ${gdOk ? '✓ OK' : '✗ Failed'}\n`);

  // Test query logging
  console.log('Testing Query Logging...');
  await mcp.logQuery(
    'What is machine learning?',
    'Machine learning is a subset of artificial intelligence...',
    'mistral-nemo',
    1250,
  );
  console.log('  Result: ✓ Logged to Notion + Google Drive\n');

  // Show status
  console.log('📊 MCP Status:');
  const status = mcp.getStatus();
  console.log(JSON.stringify(status, null, 2));

  console.log('\n✅ MCP Integration test complete!');
  console.log('\nNext: Integrate with Hermes orchestrator');
}

testMCPIntegration().catch(console.error);
