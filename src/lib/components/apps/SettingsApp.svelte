<script lang="ts">
  import { Monitor, Palette, Shield, Info, Cpu, Key, Plug, Plus, Trash2, Wifi, WifiOff, ToggleLeft, ToggleRight, Eye, EyeOff, RotateCcw, Check, Save } from 'lucide-svelte';
  import { themeStore } from '$lib/stores/theme.svelte';
  import { notificationStore } from '$lib/stores/notifications.svelte';
  import { mcpStore } from '$lib/stores/mcp.svelte';
  import { memoryStore } from '$lib/stores/memory.svelte';
  import { settingsStore } from '$lib/stores/settings.svelte';
  import { apiKeyStore } from '$lib/stores/apikeys.svelte';

  let selectedSection = $state('appearance');

  const sections = [
    { id: 'general', name: 'General', icon: Monitor },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'models', name: 'AI Models', icon: Cpu },
    { id: 'apikeys', name: 'API Keys', icon: Key },
    { id: 'mcp', name: 'MCP Servers', icon: Plug },
    { id: 'privacy', name: 'Privacy', icon: Shield },
    { id: 'about', name: 'About', icon: Info }
  ];

  let selectedTheme = $derived(themeStore.theme);
  let selectedAccent = $derived(themeStore.accentColor);

  let mcpName = $state('');
  let mcpUrl = $state('');
  let mcpDesc = $state('');
  let mcpTesting = $state<string | null>(null);
  let editingKey = $state<string | null>(null);
  let keyInputValue = $state('');
  let showKey = $state<Record<string, boolean>>({});

  function addMcpServer() {
    if (!mcpName.trim() || !mcpUrl.trim()) return;
    mcpStore.addServer(mcpName.trim(), mcpUrl.trim(), mcpDesc.trim());
    mcpName = '';
    mcpUrl = '';
    mcpDesc = '';
  }

  async function testMcpServer(id: string) {
    mcpTesting = id;
    await mcpStore.testConnection(id);
    mcpTesting = null;
  }

  function startEditKey(provider: string) {
    editingKey = provider;
    keyInputValue = apiKeyStore.getKey(provider);
    showKey[provider] = false;
  }

  function saveKey(provider: string) {
    if (!keyInputValue.trim()) {
      cancelEditKey();
      return;
    }
    apiKeyStore.setKey(provider, keyInputValue);
    editingKey = null;
    keyInputValue = '';
    notificationStore.push({ type: 'success', title: 'API Key Saved', message: `${provider} key updated`, duration: 3000 });
  }

  function cancelEditKey() {
    editingKey = null;
    keyInputValue = '';
  }

  function toggleShowKey(provider: string) {
    showKey[provider] = !showKey[provider];
  }

  const accentColors = [
    { name: 'Violet', value: '#8b5cf6' },
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Emerald', value: '#10b981' },
    { name: 'Rose', value: '#f43f5e' },
    { name: 'Amber', value: '#f59e0b' }
  ];

  const wallpapers = [
    { name: 'Nebula', color: 'linear-gradient(135deg, #1a0533, #0a0a1a)' },
    { name: 'Ocean', color: 'linear-gradient(135deg, #0a1628, #0a0a1a)' },
    { name: 'Aurora', color: 'linear-gradient(135deg, #0a1a0f, #0a0a1a)' },
    { name: 'Sunset', color: 'linear-gradient(135deg, #1a0f0a, #0a0a1a)' }
  ];

  function handleThemeChange(theme: string) {
    themeStore.setTheme(theme as 'dark' | 'light' | 'system');
    notificationStore.push({ type: 'success', title: 'Theme Changed', message: `Switched to ${theme} theme`, duration: 3000 });
  }

  function handleAccentChange(value: string) {
    themeStore.setAccent(value);
  }
</script>

<div class="settings-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Settings</span>
    </div>
    <div class="nav-list">
      {#each sections as section}
        <button
          class="nav-item"
          class:active={selectedSection === section.id}
          onclick={() => (selectedSection = section.id)}
        >
          <section.icon size={15} strokeWidth={1.5} />
          <span>{section.name}</span>
        </button>
      {/each}
    </div>
  </div>
  <div class="main scrollbar-thin">
    {#if selectedSection === 'appearance'}
      <div class="section">
        <h3 class="section-title">Appearance</h3>
        <p class="section-desc">Customize the look and feel of Elysium</p>

        <div class="setting-group">
          <span class="setting-label">Theme</span>
          <div class="theme-options">
            {#each ['dark', 'light', 'system'] as theme}
              <button
                class="theme-btn"
                class:active={selectedTheme === theme}
                onclick={() => handleThemeChange(theme)}
              >
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </button>
            {/each}
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Accent Color</span>
          <div class="color-options">
            {#each accentColors as color}
              <button
                class="color-swatch"
                class:active={selectedAccent === color.value}
                style="background: {color.value}"
                onclick={() => handleAccentChange(color.value)}
                aria-label={color.name}
              >
                {#if selectedAccent === color.value}
                  <svg viewBox="0 0 16 16" fill="none" class="check">
                    <path d="M3 8l4 4 6-7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Wallpaper</span>
          <div class="wallpaper-grid">
            {#each wallpapers as wp}
              <button class="wallpaper-thumb" style="background: {wp.color}">
                <span class="wp-name">{wp.name}</span>
              </button>
            {/each}
          </div>
        </div>
      </div>
    {:else if selectedSection === 'mcp'}
      <div class="section">
        <h3 class="section-title">MCP Servers</h3>
        <p class="section-desc">Configure Model Context Protocol servers for extended tool capabilities.</p>

        <div class="setting-group">
          <span class="setting-label">Add Server</span>
          <div class="mcp-form">
            <input class="mcp-input" type="text" placeholder="Server name" bind:value={mcpName} />
            <input class="mcp-input" type="url" placeholder="https://example.com/mcp" bind:value={mcpUrl} />
            <input class="mcp-input" type="text" placeholder="Description (optional)" bind:value={mcpDesc} />
            <button class="mcp-add-btn" onclick={addMcpServer} disabled={!mcpName.trim() || !mcpUrl.trim()}>
              <Plus size={14} />
              Add Server
            </button>
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Configured Servers</span>
          {#if mcpStore.servers.length === 0}
            <p class="mcp-empty">No MCP servers configured yet. Add one above to extend Elysium's capabilities.</p>
          {:else}
            <div class="mcp-list">
              {#each mcpStore.servers as server}
                <div class="mcp-card">
                  <div class="mcp-card-header">
                    <div class="mcp-card-info">
                      <span class="mcp-card-name">{server.name}</span>
                      <span class="mcp-card-url">{server.url}</span>
                      {#if server.description}
                        <span class="mcp-card-desc">{server.description}</span>
                      {/if}
                    </div>
                    <div class="mcp-card-status">
                      {#if server.status === 'connected'}
                        <span class="status-badge connected"><Wifi size={10} /> Connected</span>
                      {:else if server.status === 'error'}
                        <span class="status-badge error"><WifiOff size={10} /> Error</span>
                      {:else}
                        <span class="status-badge unknown">Unknown</span>
                      {/if}
                    </div>
                  </div>
                  <div class="mcp-card-actions">
                    <button class="mcp-action-btn" onclick={() => mcpStore.toggleServer(server.id)}>
                      {#if server.enabled}
                        <ToggleRight size={16} />
                        <span>Enabled</span>
                      {:else}
                        <ToggleLeft size={16} />
                        <span>Disabled</span>
                      {/if}
                    </button>
                    <button class="mcp-action-btn" onclick={() => testMcpServer(server.id)} disabled={mcpTesting === server.id}>
                      <Wifi size={13} />
                      {mcpTesting === server.id ? 'Testing...' : 'Test'}
                    </button>
                    <button class="mcp-action-btn danger" onclick={() => mcpStore.removeServer(server.id)}>
                      <Trash2 size={13} />
                      Remove
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {:else if selectedSection === 'privacy'}
      <div class="section">
        <h3 class="section-title">Privacy & Memory</h3>
        <p class="section-desc">Manage AI memory and data preferences.</p>

        <div class="setting-group">
          <span class="setting-label">AI Memory</span>
          <p class="setting-hint">When enabled, the AI can save important facts about you across conversations.</p>
          <button class="toggle-btn" class:active={memoryStore.enabled} onclick={() => memoryStore.toggleEnabled()}>
            {#if memoryStore.enabled}
              <ToggleRight size={18} />
              <span>Memory Enabled</span>
            {:else}
              <ToggleLeft size={18} />
              <span>Memory Disabled</span>
            {/if}
          </button>
        </div>

        {#if memoryStore.memories.length > 0}
          <div class="setting-group">
            <span class="setting-label">Stored Memories ({memoryStore.memories.length})</span>
            <div class="memory-list">
              {#each memoryStore.memories as mem}
                <div class="memory-item">
                  <span class="memory-content">{mem.content}</span>
                  <div class="memory-meta">
                    <span class="memory-importance">{'★'.repeat(mem.importance)}{'☆'.repeat(5 - mem.importance)}</span>
                    <button class="memory-delete" onclick={() => memoryStore.remove(mem.id)}>
                      <Trash2 size={11} />
                    </button>
                  </div>
                </div>
              {/each}
            </div>
            <button class="clear-memory-btn" onclick={() => memoryStore.clear()}>Clear All Memories</button>
          </div>
        {/if}
      </div>
    {:else if selectedSection === 'about'}
      <div class="section">
        <h3 class="section-title">About Elysium</h3>
        <div class="about-card">
          <div class="about-logo">✦</div>
          <h4>Elysium AI OS</h4>
          <p class="version">Version 0.1.0-alpha</p>
          <p class="about-desc">A next-generation AI-powered operating system interface. Built with SvelteKit, designed for the future.</p>
        </div>
      </div>
    {:else if selectedSection === 'general'}
      <div class="section">
        <h3 class="section-title">General</h3>
        <p class="section-desc">Configure default behavior and preferences</p>

        <div class="setting-group">
          <span class="setting-label">Default Team</span>
          <p class="setting-hint">The agent team used for new conversations.</p>
          <div class="theme-options">
            {#each ['productivity', 'code_review', 'research', 'quick'] as team}
              <button
                class="theme-btn"
                class:active={settingsStore.settings.defaultTeam === team}
                onclick={() => settingsStore.update('defaultTeam', team)}
              >
                {team.replace('_', ' ')}
              </button>
            {/each}
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Default Provider</span>
          <p class="setting-hint">Preferred LLM provider. "auto" selects the best available.</p>
          <div class="select-wrapper">
            <select
              class="settings-select"
              value={settingsStore.settings.defaultProvider}
              onchange={(e) => settingsStore.update('defaultProvider', e.currentTarget.value)}
            >
              <option value="auto">Auto (recommended)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google Gemini</option>
              <option value="together">Together.ai</option>
              <option value="openrouter">OpenRouter</option>
              <option value="mistral">Mistral</option>
              <option value="moonshot">Kimi (Moonshot)</option>
            </select>
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Streaming</span>
          <p class="setting-hint">Stream agent responses token-by-token.</p>
          <button class="toggle-btn" class:active={settingsStore.settings.streamResponses} onclick={() => settingsStore.update('streamResponses', !settingsStore.settings.streamResponses)}>
            {#if settingsStore.settings.streamResponses}
              <ToggleRight size={18} />
              <span>Streaming Enabled</span>
            {:else}
              <ToggleLeft size={18} />
              <span>Streaming Disabled</span>
            {/if}
          </button>
        </div>

        <div class="setting-group">
          <span class="setting-label">Notifications</span>
          <button class="toggle-btn" class:active={settingsStore.settings.showNotifications} onclick={() => settingsStore.update('showNotifications', !settingsStore.settings.showNotifications)}>
            {#if settingsStore.settings.showNotifications}
              <ToggleRight size={18} />
              <span>Notifications Enabled</span>
            {:else}
              <ToggleLeft size={18} />
              <span>Notifications Disabled</span>
            {/if}
          </button>
        </div>

        <div class="setting-group">
          <span class="setting-label">Session Timeout</span>
          <p class="setting-hint">Minutes before an idle session expires.</p>
          <div class="select-wrapper">
            <select
              class="settings-select"
              value={settingsStore.settings.sessionTimeoutMinutes}
              onchange={(e) => settingsStore.update('sessionTimeoutMinutes', Number(e.currentTarget.value))}
            >
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>1 hour</option>
              <option value={120}>2 hours</option>
              <option value={480}>8 hours</option>
            </select>
          </div>
        </div>

        <div class="setting-group">
          <button class="clear-memory-btn" onclick={() => { settingsStore.reset(); notificationStore.push({ type: 'success', title: 'Settings Reset', message: 'All general settings restored to defaults', duration: 3000 }); }}>
            <RotateCcw size={13} />
            Reset to Defaults
          </button>
        </div>
      </div>
    {:else if selectedSection === 'models'}
      <div class="section">
        <h3 class="section-title">AI Models</h3>
        <p class="section-desc">Available LLM providers and their default models</p>

        <div class="model-grid">
          {#each apiKeyStore.providers as prov}
            <div class="model-card" class:configured={apiKeyStore.isConfigured(prov.provider)}>
              <div class="model-card-header">
                <span class="model-card-name">{prov.label}</span>
                <span class="status-badge" class:connected={apiKeyStore.isConfigured(prov.provider)} class:unknown={!apiKeyStore.isConfigured(prov.provider)}>
                  {apiKeyStore.isConfigured(prov.provider) ? 'Ready' : 'No Key'}
                </span>
              </div>
              <span class="model-card-model">{prov.model}</span>
              <span class="model-card-id">{prov.provider}</span>
            </div>
          {/each}
        </div>

        <div class="setting-group" style="margin-top: 24px;">
          <p class="setting-hint">
            {apiKeyStore.configuredCount} of {apiKeyStore.providers.length} providers configured. Add API keys in the API Keys section.
          </p>
        </div>
      </div>
    {:else if selectedSection === 'apikeys'}
      <div class="section">
        <h3 class="section-title">API Keys</h3>
        <p class="section-desc">Manage your LLM provider API keys. Keys are stored locally in your browser.</p>

        <div class="apikey-list">
          {#each apiKeyStore.providers as prov}
            <div class="apikey-row">
              <div class="apikey-info">
                <span class="apikey-label">{prov.label}</span>
                <span class="apikey-model">{prov.model}</span>
              </div>
              {#if editingKey === prov.provider}
                <div class="apikey-edit">
                  <input
                    class="mcp-input apikey-input"
                    type={showKey[prov.provider] ? 'text' : 'password'}
                    placeholder="sk-..."
                    bind:value={keyInputValue}
                    onkeydown={(e) => { if (e.key === 'Enter') saveKey(prov.provider); if (e.key === 'Escape') cancelEditKey(); }}
                  />
                  <button class="mcp-action-btn" onclick={() => toggleShowKey(prov.provider)}>
                    {#if showKey[prov.provider]}
                      <EyeOff size={13} />
                    {:else}
                      <Eye size={13} />
                    {/if}
                  </button>
                  <button class="mcp-action-btn" onclick={() => saveKey(prov.provider)}>
                    <Save size={13} />
                    Save
                  </button>
                  <button class="mcp-action-btn" onclick={cancelEditKey}>
                    Cancel
                  </button>
                </div>
              {:else}
                <div class="apikey-display">
                  {#if apiKeyStore.isConfigured(prov.provider)}
                    <span class="apikey-masked">{apiKeyStore.maskKey(apiKeyStore.getKey(prov.provider))}</span>
                    <span class="status-badge connected"><Check size={10} /> Set</span>
                  {:else}
                    <span class="apikey-masked not-set">Not configured</span>
                  {/if}
                  <button class="mcp-action-btn" onclick={() => startEditKey(prov.provider)}>
                    <Key size={13} />
                    {apiKeyStore.isConfigured(prov.provider) ? 'Change' : 'Add Key'}
                  </button>
                  {#if apiKeyStore.isConfigured(prov.provider)}
                    <button class="mcp-action-btn danger" onclick={() => { apiKeyStore.setKey(prov.provider, ''); notificationStore.push({ type: 'success', title: 'Key Removed', message: `${prov.label} key removed`, duration: 3000 }); }}>
                      <Trash2 size={13} />
                    </button>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>

        <div class="setting-group" style="margin-top: 20px;">
          <p class="setting-hint">Keys are stored in your browser's localStorage and never sent to our servers. For server-side keys, configure them in the <code>.env</code> file.</p>
        </div>
      </div>
    {:else}
      <div class="section">
        <h3 class="section-title">{sections.find((s) => s.id === selectedSection)?.name}</h3>
        <p class="section-desc">This section is coming soon.</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .settings-layout {
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

  .setting-group {
    margin-bottom: 24px;
  }

  .setting-label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 10px;
    font-style: normal;
  }

  .theme-options {
    display: flex;
    gap: 8px;
  }

  .theme-btn {
    position: relative;
    padding: 10px 20px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    transition: all var(--transition-fast);
    font-family: inherit;
  }

  .theme-btn:hover {
    border-color: var(--border-default);
    color: var(--text-primary);
  }

  .theme-btn.active {
    border-color: var(--accent);
    color: var(--accent-glow);
    background: var(--accent-subtle);
  }

  .color-options {
    display: flex;
    gap: 10px;
  }

  .color-swatch {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .color-swatch:hover {
    transform: scale(1.1);
  }

  .color-swatch.active {
    border-color: white;
    box-shadow: 0 0 12px currentColor;
  }

  .check {
    width: 14px;
    height: 14px;
  }

  .wallpaper-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .wallpaper-thumb {
    aspect-ratio: 16/10;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    cursor: pointer;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 6px;
    transition: all var(--transition-fast);
  }

  .wallpaper-thumb:hover {
    border-color: var(--accent);
    transform: scale(1.02);
  }

  .wp-name {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.6);
  }

  .about-card {
    text-align: center;
    padding: 32px;
  }

  .about-logo {
    font-size: 48px;
    color: var(--accent-glow);
    margin-bottom: 12px;
  }

  .about-card h4 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .version {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }

  .about-desc {
    font-size: 13px;
    color: var(--text-secondary);
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .mcp-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .mcp-input {
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 13px;
    outline: none;
    transition: border-color var(--transition-fast);
  }

  .mcp-input:focus {
    border-color: var(--accent);
  }

  .mcp-input::placeholder {
    color: var(--text-muted);
  }

  .mcp-add-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--accent);
    background: var(--accent-subtle);
    color: var(--accent-glow);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    align-self: flex-start;
  }

  .mcp-add-btn:hover:not(:disabled) {
    background: rgba(139, 92, 246, 0.25);
  }

  .mcp-add-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .mcp-empty {
    font-size: 13px;
    color: var(--text-muted);
    font-style: italic;
  }

  .mcp-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .mcp-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 12px;
  }

  .mcp-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
  }

  .mcp-card-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    flex: 1;
  }

  .mcp-card-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .mcp-card-url {
    font-size: 11px;
    color: var(--text-muted);
    font-family: 'SF Mono', 'Fira Code', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .mcp-card-desc {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 2px;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    white-space: nowrap;
  }

  .status-badge.connected {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
  }

  .status-badge.error {
    background: rgba(244, 63, 94, 0.1);
    color: #f43f5e;
  }

  .status-badge.unknown {
    background: var(--bg-surface-hover);
    color: var(--text-muted);
  }

  .mcp-card-actions {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }

  .mcp-action-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: transparent;
    color: var(--text-secondary);
    font-size: 11px;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .mcp-action-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .mcp-action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .mcp-action-btn.danger:hover {
    border-color: rgba(244, 63, 94, 0.3);
    color: #f43f5e;
    background: rgba(244, 63, 94, 0.05);
  }

  .setting-hint {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 10px;
    line-height: 1.5;
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    transition: all var(--transition-fast);
  }

  .toggle-btn:hover {
    background: var(--bg-surface-hover);
  }

  .toggle-btn.active {
    border-color: rgba(16, 185, 129, 0.3);
    color: #10b981;
  }

  .memory-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
  }

  .memory-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    padding: 8px 12px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
  }

  .memory-content {
    font-size: 12px;
    color: var(--text-secondary);
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .memory-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .memory-importance {
    font-size: 10px;
    color: #f59e0b;
    letter-spacing: 1px;
  }

  .memory-delete {
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    padding: 2px;
    display: flex;
    transition: color var(--transition-fast);
  }

  .memory-delete:hover {
    color: #f43f5e;
  }

  .clear-memory-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(244, 63, 94, 0.3);
    background: transparent;
    color: #f43f5e;
    font-size: 12px;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .clear-memory-btn:hover {
    background: rgba(244, 63, 94, 0.1);
  }

  .select-wrapper {
    display: inline-block;
  }

  .settings-select {
    padding: 8px 32px 8px 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    outline: none;
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2371717a' d='M3 4.5L6 7.5L9 4.5'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    transition: border-color var(--transition-fast);
  }

  .settings-select:focus {
    border-color: var(--accent);
  }

  .settings-select option {
    background: var(--bg-base);
    color: var(--text-primary);
  }

  .model-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
  }

  .model-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    transition: all var(--transition-fast);
  }

  .model-card.configured {
    border-color: rgba(16, 185, 129, 0.2);
  }

  .model-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .model-card-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .model-card-model {
    font-size: 12px;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
  }

  .model-card-id {
    font-size: 11px;
    color: var(--text-muted);
  }

  .apikey-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .apikey-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    flex-wrap: wrap;
  }

  .apikey-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 140px;
  }

  .apikey-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .apikey-model {
    font-size: 11px;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
  }

  .apikey-display {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .apikey-edit {
    display: flex;
    align-items: center;
    gap: 6px;
    flex: 1;
    min-width: 0;
  }

  .apikey-input {
    flex: 1;
    min-width: 180px;
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
    font-size: 12px;
  }

  .apikey-masked {
    font-size: 12px;
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
  }

  .apikey-masked.not-set {
    color: var(--text-muted);
    font-family: inherit;
    font-style: italic;
    letter-spacing: normal;
  }

  code {
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
    font-size: 12px;
    padding: 1px 5px;
    background: var(--bg-surface);
    border-radius: 4px;
    color: var(--accent-glow);
  }
</style>
