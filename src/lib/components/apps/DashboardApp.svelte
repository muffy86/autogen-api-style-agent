<script lang="ts">
  import {
    BarChart3,
    Sparkles,
    Send,
    Code,
    GitBranch,
    Boxes,
    Activity,
    Zap,
    Clock,
    MessageCircle,
    ChevronRight,
    Copy,
    Check,
    Trash2,
    Play,
    Search
  } from 'lucide-svelte';

  let activeTab = $state('overview');
  let promptInput = $state('');
  let promptStyle = $state('detailed');
  let enhancedResult = $state('');
  let codeInput = $state('');
  let codeOutput = $state('');
  let codeAction = $state('');
  let copiedId = $state('');
  let botToken = $state('');
  let ownerChatId = $state('');

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'prompt', name: 'Prompt Enhancer', icon: Sparkles },
    { id: 'telegram', name: 'Telegram', icon: Send },
    { id: 'vibe', name: 'Vibe Coding', icon: Code },
    { id: 'automation', name: 'Automation', icon: GitBranch },
    { id: 'n8n', name: 'n8n Workflows', icon: Boxes }
  ];

  const statusCards = [
    { label: 'Services', value: '3 active', icon: Activity, color: '#10b981' },
    { label: 'Workflows', value: '6 templates', icon: Boxes, color: '#3b82f6' },
    { label: 'Uptime', value: '99.9%', icon: Clock, color: '#f59e0b' },
    { label: 'Messages', value: '1,247', icon: MessageCircle, color: '#8b5cf6' }
  ];

  const recentActivity = [
    { time: '2 min ago', text: 'Telegram bot processed incoming message', type: 'info' },
    { time: '15 min ago', text: 'Health check passed — all services operational', type: 'success' },
    { time: '1 hour ago', text: 'Batch prompt enhancement completed (12 prompts)', type: 'info' },
    { time: '3 hours ago', text: 'n8n workflow "Research & Save" triggered', type: 'info' },
    { time: '6 hours ago', text: 'System backup completed successfully', type: 'success' }
  ];

  const telegramCommands = [
    { cmd: '/start', desc: 'Initialize the bot and show welcome message' },
    { cmd: '/configure', desc: 'Open configuration wizard' },
    { cmd: '/keys', desc: 'Manage API keys and tokens' },
    { cmd: '/status', desc: 'Show current system status' },
    { cmd: '/agents', desc: 'List and manage AI agents' },
    { cmd: '/shell', desc: 'Execute shell commands remotely' },
    { cmd: '/logs', desc: 'View recent system logs' },
    { cmd: '/notify', desc: 'Configure notification preferences' },
    { cmd: '/update', desc: 'Check for and apply updates' },
    { cmd: '/backup', desc: 'Create or restore system backup' },
    { cmd: '/eliza', desc: 'Interact with ElizaOS personalities' },
    { cmd: '/help', desc: 'Show all available commands' }
  ];

  const automationRecipes = [
    { id: 'auto-enhance', title: 'Auto-Enhance Prompts', desc: 'Automatically enhance all prompts before sending to AI', enabled: true },
    { id: 'health-mon', title: 'Health Monitor', desc: 'Periodically check service status and alert on failures', enabled: true },
    { id: 'research-save', title: 'Research & Save', desc: 'Search the web, summarize findings, save to knowledge base', enabled: false },
    { id: 'code-review', title: 'Code Review Pipeline', desc: 'Auto-review PRs with AI feedback', enabled: false },
    { id: 'telegram-alerts', title: 'Telegram Alerts', desc: 'Forward important events to Telegram', enabled: true }
  ];

  const n8nWorkflows = [
    {
      id: 'telegram-ai',
      title: 'Telegram AI Router',
      desc: 'Routes messages through AI models based on content',
      badge: 'Telegram',
      badgeColor: '#0088cc',
      json: { name: 'Telegram AI Router', nodes: [{ type: 'n8n-nodes-base.telegramTrigger', name: 'Telegram Trigger', position: [250, 300] }, { type: 'n8n-nodes-base.if', name: 'Route by Content', position: [450, 300] }, { type: 'n8n-nodes-base.openAi', name: 'AI Process', position: [650, 300] }, { type: 'n8n-nodes-base.telegram', name: 'Send Response', position: [850, 300] }], connections: {} }
    },
    {
      id: 'batch-enhance',
      title: 'Batch Prompt Enhancer',
      desc: 'Enhance multiple prompts in batch via webhook',
      badge: 'AI',
      badgeColor: '#8b5cf6',
      json: { name: 'Batch Prompt Enhancer', nodes: [{ type: 'n8n-nodes-base.webhook', name: 'Webhook Trigger', position: [250, 300] }, { type: 'n8n-nodes-base.splitInBatches', name: 'Split Prompts', position: [450, 300] }, { type: 'n8n-nodes-base.openAi', name: 'Enhance Prompt', position: [650, 300] }, { type: 'n8n-nodes-base.respondToWebhook', name: 'Return Results', position: [850, 300] }], connections: {} }
    },
    {
      id: 'health-monitor',
      title: 'Service Health Monitor',
      desc: 'Periodic health checks with Telegram alerts',
      badge: 'DevOps',
      badgeColor: '#10b981',
      json: { name: 'Service Health Monitor', nodes: [{ type: 'n8n-nodes-base.cron', name: 'Schedule (5min)', position: [250, 300] }, { type: 'n8n-nodes-base.httpRequest', name: 'Health Check', position: [450, 300] }, { type: 'n8n-nodes-base.if', name: 'Check Status', position: [650, 300] }, { type: 'n8n-nodes-base.telegram', name: 'Alert on Failure', position: [850, 300] }], connections: {} }
    },
    {
      id: 'research-save',
      title: 'Research & Save Pipeline',
      desc: 'Web research → summarize → save to database',
      badge: 'AI',
      badgeColor: '#8b5cf6',
      json: { name: 'Research & Save Pipeline', nodes: [{ type: 'n8n-nodes-base.webhook', name: 'Research Request', position: [250, 300] }, { type: 'n8n-nodes-base.httpRequest', name: 'Web Search', position: [450, 300] }, { type: 'n8n-nodes-base.openAi', name: 'Summarize', position: [650, 300] }, { type: 'n8n-nodes-base.postgres', name: 'Save to DB', position: [850, 300] }], connections: {} }
    },
    {
      id: 'eliza-router',
      title: 'ElizaOS Personality Router',
      desc: 'Route messages to different ElizaOS personalities',
      badge: 'AI',
      badgeColor: '#8b5cf6',
      json: { name: 'ElizaOS Personality Router', nodes: [{ type: 'n8n-nodes-base.webhook', name: 'Message Input', position: [250, 300] }, { type: 'n8n-nodes-base.switch', name: 'Personality Router', position: [450, 300] }, { type: 'n8n-nodes-base.httpRequest', name: 'ElizaOS API', position: [650, 300] }, { type: 'n8n-nodes-base.respondToWebhook', name: 'Return Response', position: [850, 300] }], connections: {} }
    },
    {
      id: 'vibe-review',
      title: 'Vibe Code Review',
      desc: 'Automated code review with AI feedback',
      badge: 'DevOps',
      badgeColor: '#10b981',
      json: { name: 'Vibe Code Review', nodes: [{ type: 'n8n-nodes-base.githubTrigger', name: 'PR Trigger', position: [250, 300] }, { type: 'n8n-nodes-base.httpRequest', name: 'Fetch Diff', position: [450, 300] }, { type: 'n8n-nodes-base.openAi', name: 'AI Review', position: [650, 300] }, { type: 'n8n-nodes-base.github', name: 'Post Comment', position: [850, 300] }], connections: {} }
    }
  ];

  const enhancementStyles: Record<string, (input: string) => string> = {
    concise: (input: string) => `[Enhanced — Concise]\n\n${input.trim()}\n\nBe direct and specific. Provide only the essential information requested.`,
    detailed: (input: string) => `[Enhanced — Detailed]\n\nContext: You are an expert assistant.\n\nTask: ${input.trim()}\n\nRequirements:\n- Provide comprehensive, well-structured output\n- Include relevant examples where appropriate\n- Consider edge cases and alternatives\n- Format the response for readability`,
    creative: (input: string) => `[Enhanced — Creative]\n\nImagine you are a brilliantly creative thinker. Your task:\n\n${input.trim()}\n\nApproach this with originality and flair. Think outside the box, draw unexpected connections, and present ideas in an engaging, memorable way.`,
    technical: (input: string) => `[Enhanced — Technical]\n\nYou are a senior technical expert. Analyze and respond to the following with precision:\n\n${input.trim()}\n\nInclude:\n- Technical specifications and implementation details\n- Code examples where applicable\n- Performance considerations\n- Best practices and potential pitfalls`
  };

  function handleEnhance() {
    if (!promptInput.trim()) return;
    const fn = enhancementStyles[promptStyle];
    enhancedResult = fn ? fn(promptInput) : promptInput;
  }

  function handleCodeAction(action: string) {
    if (!codeInput.trim()) return;
    codeAction = action;
    if (action === 'explain') {
      codeOutput = `## Code Explanation\n\nThis code performs the following operations:\n\n1. **Input Processing** — The code accepts input and validates the structure\n2. **Core Logic** — Processes the data through the main algorithm\n3. **Output** — Returns the formatted result\n\n> This is a placeholder explanation. Connect an AI model to get real analysis.`;
    } else if (action === 'review') {
      codeOutput = `## Code Review\n\n✅ **Strengths:**\n- Clean structure and readable formatting\n- Good separation of concerns\n\n⚠️ **Suggestions:**\n- Consider adding error handling for edge cases\n- Add input validation before processing\n- Consider extracting magic numbers into constants\n\n> This is a placeholder review. Connect an AI model to get real feedback.`;
    } else if (action === 'tests') {
      codeOutput = `// Generated Test Suite\n\ndescribe('Module', () => {\n  test('should handle valid input', () => {\n    const result = processInput(validData);\n    expect(result).toBeDefined();\n    expect(result.status).toBe('success');\n  });\n\n  test('should handle empty input', () => {\n    expect(() => processInput(null)).toThrow();\n  });\n\n  test('should handle edge cases', () => {\n    const edge = processInput(edgeCaseData);\n    expect(edge.status).toBe('handled');\n  });\n});\n\n// Placeholder tests — connect an AI model for real test generation.`;
    }
  }

  function clearOutput() {
    codeOutput = '';
    codeAction = '';
  }

  async function copyOutput() {
    try {
      await navigator.clipboard.writeText(codeOutput);
      copiedId = 'output';
      setTimeout(() => (copiedId = ''), 2000);
    } catch {}
  }

  async function copyWorkflowJson(id: string, json: object) {
    try {
      await navigator.clipboard.writeText(JSON.stringify(json, null, 2));
      copiedId = id;
      setTimeout(() => (copiedId = ''), 2000);
    } catch {}
  }

  let automationToggles = $state<Record<string, boolean>>(
    Object.fromEntries(automationRecipes.map((r) => [r.id, r.enabled]))
  );

  function toggleAutomation(id: string) {
    automationToggles[id] = !automationToggles[id];
  }
</script>

<div class="dashboard-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Dashboard</span>
    </div>
    <div class="nav-list">
      {#each tabs as tab}
        <button
          class="nav-item"
          class:active={activeTab === tab.id}
          onclick={() => (activeTab = tab.id)}
        >
          <tab.icon size={15} strokeWidth={1.5} />
          <span>{tab.name}</span>
        </button>
      {/each}
    </div>
  </div>

  <div class="main scrollbar-thin">
    {#if activeTab === 'overview'}
      <div class="section">
        <h3 class="section-title">Overview</h3>
        <p class="section-desc">System status and quick actions</p>

        <div class="status-grid">
          {#each statusCards as card}
            <div class="status-card">
              <div class="status-card-icon" style="color: {card.color}; background: {card.color}1a;">
                <card.icon size={20} strokeWidth={1.5} />
              </div>
              <div class="status-card-info">
                <span class="status-card-label">{card.label}</span>
                <span class="status-card-value">{card.value}</span>
              </div>
            </div>
          {/each}
        </div>

        <div class="sub-section">
          <span class="sub-title">Quick Actions</span>
          <div class="quick-actions">
            <button class="action-btn" onclick={() => (activeTab = 'prompt')}>
              <Sparkles size={14} strokeWidth={1.5} />
              Enhance Prompt
            </button>
            <button class="action-btn" onclick={() => (activeTab = 'telegram')}>
              <Send size={14} strokeWidth={1.5} />
              Telegram Bot
            </button>
            <button class="action-btn" onclick={() => (activeTab = 'vibe')}>
              <Code size={14} strokeWidth={1.5} />
              Vibe Coding
            </button>
            <button class="action-btn" onclick={() => (activeTab = 'n8n')}>
              <Boxes size={14} strokeWidth={1.5} />
              Browse Workflows
            </button>
          </div>
        </div>

        <div class="sub-section">
          <span class="sub-title">Recent Activity</span>
          <div class="activity-list">
            {#each recentActivity as entry}
              <div class="activity-item">
                <div class="activity-dot" class:success={entry.type === 'success'}></div>
                <span class="activity-text">{entry.text}</span>
                <span class="activity-time">{entry.time}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>

    {:else if activeTab === 'prompt'}
      <div class="section">
        <h3 class="section-title">Prompt Enhancer</h3>
        <p class="section-desc">Transform basic prompts into optimized instructions</p>

        <div class="prompt-input-group">
          <label class="field-label" for="prompt-input">Input Prompt</label>
          <textarea
            id="prompt-input"
            class="text-area"
            rows="4"
            placeholder="Enter your prompt here..."
            bind:value={promptInput}
          ></textarea>
        </div>

        <div class="prompt-controls">
          <div class="select-group">
            <label class="field-label" for="prompt-style">Enhancement Style</label>
            <select id="prompt-style" class="select-input" bind:value={promptStyle}>
              <option value="concise">Concise</option>
              <option value="detailed">Detailed</option>
              <option value="creative">Creative</option>
              <option value="technical">Technical</option>
            </select>
          </div>
          <button class="primary-btn" onclick={handleEnhance}>
            <Sparkles size={14} strokeWidth={1.5} />
            Enhance
          </button>
        </div>

        {#if enhancedResult}
          <div class="result-box">
            <div class="result-header">
              <span class="field-label">Enhanced Result</span>
              <button class="icon-btn" onclick={() => { navigator.clipboard.writeText(enhancedResult); copiedId = 'enhanced'; setTimeout(() => (copiedId = ''), 2000); }}>
                {#if copiedId === 'enhanced'}
                  <Check size={14} strokeWidth={1.5} />
                {:else}
                  <Copy size={14} strokeWidth={1.5} />
                {/if}
              </button>
            </div>
            <pre class="result-pre">{enhancedResult}</pre>
          </div>
        {/if}
      </div>

    {:else if activeTab === 'telegram'}
      <div class="section">
        <h3 class="section-title">Telegram</h3>
        <p class="section-desc">NanoClaw bot management and configuration</p>

        <div class="info-card">
          <div class="info-card-header">
            <Send size={18} strokeWidth={1.5} />
            <span>Bot Status</span>
          </div>
          <p class="info-card-text">Configure bot token to connect</p>
          <div class="status-badge offline">Offline</div>
        </div>

        <div class="sub-section">
          <span class="sub-title">Commands</span>
          <div class="commands-table">
            <div class="commands-header">
              <span>Command</span>
              <span>Description</span>
            </div>
            {#each telegramCommands as cmd}
              <div class="command-row">
                <code class="command-name">{cmd.cmd}</code>
                <span class="command-desc">{cmd.desc}</span>
              </div>
            {/each}
          </div>
        </div>

        <div class="sub-section">
          <span class="sub-title">Quick Configure</span>
          <div class="config-fields">
            <div class="field-group">
              <label class="field-label" for="bot-token">Bot Token</label>
              <input
                id="bot-token"
                type="password"
                class="text-input"
                placeholder="Enter Telegram bot token"
                bind:value={botToken}
              />
            </div>
            <div class="field-group">
              <label class="field-label" for="owner-chat-id">Owner Chat ID</label>
              <input
                id="owner-chat-id"
                type="text"
                class="text-input"
                placeholder="Enter your chat ID"
                bind:value={ownerChatId}
              />
            </div>
            <button class="primary-btn" disabled>
              <Send size={14} strokeWidth={1.5} />
              Save Configuration
            </button>
          </div>
        </div>
      </div>

    {:else if activeTab === 'vibe'}
      <div class="section">
        <h3 class="section-title">Vibe Coding</h3>
        <p class="section-desc">AI-powered code analysis and generation</p>

        <div class="prompt-input-group">
          <label class="field-label" for="code-input">Code Input</label>
          <textarea
            id="code-input"
            class="text-area code-area"
            rows="8"
            placeholder="Paste your code here..."
            bind:value={codeInput}
          ></textarea>
        </div>

        <div class="code-actions">
          <button class="action-btn" class:active={codeAction === 'explain'} onclick={() => handleCodeAction('explain')}>
            <Search size={14} strokeWidth={1.5} />
            Explain Code
          </button>
          <button class="action-btn" class:active={codeAction === 'review'} onclick={() => handleCodeAction('review')}>
            <Play size={14} strokeWidth={1.5} />
            Review Code
          </button>
          <button class="action-btn" class:active={codeAction === 'tests'} onclick={() => handleCodeAction('tests')}>
            <Code size={14} strokeWidth={1.5} />
            Generate Tests
          </button>
        </div>

        {#if codeOutput}
          <div class="result-box code-result">
            <div class="result-header">
              <span class="field-label">Output</span>
              <div class="result-actions">
                <button class="icon-btn" onclick={copyOutput}>
                  {#if copiedId === 'output'}
                    <Check size={14} strokeWidth={1.5} />
                  {:else}
                    <Copy size={14} strokeWidth={1.5} />
                  {/if}
                </button>
                <button class="icon-btn" onclick={clearOutput}>
                  <Trash2 size={14} strokeWidth={1.5} />
                </button>
              </div>
            </div>
            <pre class="result-pre code-pre">{codeOutput}</pre>
          </div>
        {/if}
      </div>

    {:else if activeTab === 'automation'}
      <div class="section">
        <h3 class="section-title">Automation</h3>
        <p class="section-desc">Configure automated workflows and pipelines</p>

        <div class="automation-list">
          {#each automationRecipes as recipe}
            <div class="automation-card">
              <div class="automation-info">
                <span class="automation-title">{recipe.title}</span>
                <span class="automation-desc">{recipe.desc}</span>
              </div>
              <div class="automation-controls">
                <button
                  class="toggle-btn"
                  class:active={automationToggles[recipe.id]}
                  onclick={() => toggleAutomation(recipe.id)}
                  aria-label="Toggle {recipe.title}"
                >
                  <div class="toggle-track">
                    <div class="toggle-thumb"></div>
                  </div>
                </button>
                <button class="action-btn small">
                  Configure
                  <ChevronRight size={12} strokeWidth={2} />
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>

    {:else if activeTab === 'n8n'}
      <div class="section">
        <h3 class="section-title">n8n Workflows</h3>
        <p class="section-desc">Pre-built workflow templates for common automations</p>

        <div class="workflow-grid">
          {#each n8nWorkflows as wf}
            <div class="workflow-card">
              <div class="workflow-header">
                <span class="workflow-title">{wf.title}</span>
                <span class="workflow-badge" style="background: {wf.badgeColor}1a; color: {wf.badgeColor};">{wf.badge}</span>
              </div>
              <p class="workflow-desc">{wf.desc}</p>
              <div class="workflow-nodes">
                {#each wf.json.nodes as node}
                  <span class="node-tag">{node.name}</span>
                {/each}
              </div>
              <button class="action-btn" onclick={() => copyWorkflowJson(wf.id, wf.json)}>
                {#if copiedId === wf.id}
                  <Check size={14} strokeWidth={1.5} />
                  Copied!
                {:else}
                  <Copy size={14} strokeWidth={1.5} />
                  Copy JSON
                {/if}
              </button>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .dashboard-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 200px;
    border-right: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .nav-list {
    padding: 4px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    text-align: left;
  }

  .nav-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .nav-item.active {
    background: var(--accent-subtle);
    color: var(--accent-glow);
  }

  .main {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .section-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 24px;
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 28px;
  }

  .status-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
  }

  .status-card:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-default);
  }

  .status-card-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .status-card-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .status-card-label {
    font-size: 12px;
    color: var(--text-muted);
  }

  .status-card-value {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .sub-section {
    margin-bottom: 24px;
  }

  .sub-title {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }

  .quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .action-btn:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-default);
    color: var(--text-primary);
  }

  .action-btn.active {
    background: var(--accent-subtle);
    border-color: var(--accent);
    color: var(--accent-glow);
  }

  .action-btn.small {
    padding: 5px 10px;
    font-size: 12px;
  }

  .activity-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .activity-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.01);
    transition: background var(--transition-fast);
  }

  .activity-item:hover {
    background: var(--bg-surface-hover);
  }

  .activity-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
  }

  .activity-dot.success {
    background: #10b981;
  }

  .activity-text {
    flex: 1;
    font-size: 13px;
    color: var(--text-secondary);
  }

  .activity-time {
    font-size: 11px;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .prompt-input-group {
    margin-bottom: 16px;
  }

  .field-label {
    display: block;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
    margin-bottom: 6px;
  }

  .text-area {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    resize: vertical;
    transition: border-color var(--transition-fast);
    line-height: 1.5;
  }

  .text-area:focus {
    outline: none;
    border-color: var(--accent);
  }

  .text-area.code-area {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 12px;
    line-height: 1.6;
    tab-size: 2;
  }

  .prompt-controls {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    margin-bottom: 20px;
  }

  .select-group {
    flex: 1;
    max-width: 200px;
  }

  .select-input {
    width: 100%;
    padding: 8px 12px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
    transition: border-color var(--transition-fast);
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2371717a' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 30px;
  }

  .select-input:focus {
    outline: none;
    border-color: var(--accent);
  }

  .primary-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 18px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .primary-btn:hover:not(:disabled) {
    background: var(--accent-glow);
    box-shadow: var(--shadow-glow);
  }

  .primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .result-box {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .result-header .field-label {
    margin-bottom: 0;
  }

  .result-actions {
    display: flex;
    gap: 4px;
  }

  .result-pre {
    padding: 14px;
    font-size: 13px;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.6;
    max-height: 300px;
    overflow-y: auto;
    margin: 0;
    font-family: inherit;
  }

  .code-pre {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 12px;
  }

  .icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .icon-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .code-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
  }

  .info-card {
    padding: 16px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 24px;
  }

  .info-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
    font-weight: 500;
    font-size: 14px;
    margin-bottom: 8px;
  }

  .info-card-text {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
  }

  .status-badge.offline {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
  }

  .commands-table {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .commands-header {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 16px;
    padding: 8px 14px;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .command-row {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 16px;
    padding: 8px 14px;
    font-size: 13px;
    transition: background var(--transition-fast);
  }

  .command-row:hover {
    background: var(--bg-surface-hover);
  }

  .command-name {
    color: var(--accent-glow);
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 12px;
  }

  .command-desc {
    color: var(--text-secondary);
  }

  .config-fields {
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-width: 400px;
  }

  .field-group {
    display: flex;
    flex-direction: column;
  }

  .text-input {
    width: 100%;
    padding: 8px 12px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 13px;
    transition: border-color var(--transition-fast);
  }

  .text-input:focus {
    outline: none;
    border-color: var(--accent);
  }

  .text-input::placeholder {
    color: var(--text-muted);
  }

  .automation-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .automation-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 16px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
  }

  .automation-card:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-default);
  }

  .automation-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }

  .automation-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .automation-desc {
    font-size: 12px;
    color: var(--text-muted);
  }

  .automation-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .toggle-btn {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .toggle-track {
    width: 36px;
    height: 20px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    position: relative;
    transition: background var(--transition-fast);
  }

  .toggle-btn.active .toggle-track {
    background: var(--accent);
  }

  .toggle-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: white;
    position: absolute;
    top: 2px;
    left: 2px;
    transition: transform var(--transition-fast);
  }

  .toggle-btn.active .toggle-thumb {
    transform: translateX(16px);
  }

  .workflow-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .workflow-card {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 16px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
  }

  .workflow-card:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-default);
  }

  .workflow-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  .workflow-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .workflow-badge {
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
  }

  .workflow-desc {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.4;
  }

  .workflow-nodes {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .node-tag {
    padding: 2px 7px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    font-size: 10px;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .workflow-card .action-btn {
    align-self: flex-start;
    margin-top: auto;
  }
</style>
