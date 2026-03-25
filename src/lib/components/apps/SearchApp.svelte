<script lang="ts">
  import { Search, Clock, Zap, ArrowRight, MessageSquare, Folder, Terminal, Settings } from 'lucide-svelte';

  let query = $state('');

  const recentSearches = [
    'Project architecture docs',
    'API integration guide',
    'Meeting notes March 2026'
  ];

  const quickActions = [
    { name: 'New Chat', icon: MessageSquare, shortcut: '⌘ N' },
    { name: 'Open Files', icon: Folder, shortcut: '⌘ O' },
    { name: 'Terminal', icon: Terminal, shortcut: '⌘ T' },
    { name: 'Settings', icon: Settings, shortcut: '⌘ ,' }
  ];
</script>

<div class="search-app">
  <div class="dev-banner">
    <span>🔍 Search is under development</span>
  </div>
  <div class="search-header">
    <div class="search-input-wrapper">
      <Search size={18} />
      <input
        class="search-input"
        type="text"
        placeholder="Search anything..."
        bind:value={query}
        autofocus={true}
      />
    </div>
  </div>

  <div class="search-body scrollbar-thin">
    {#if !query}
      <div class="search-section">
        <div class="section-header">
          <Clock size={13} />
          <span>Recent Searches</span>
        </div>
        {#each recentSearches as item}
          <button class="search-result">
            <Clock size={14} />
            <span>{item}</span>
            <ArrowRight size={12} class="arrow" />
          </button>
        {/each}
      </div>

      <div class="search-section">
        <div class="section-header">
          <Zap size={13} />
          <span>Quick Actions</span>
        </div>
        {#each quickActions as action}
          <button class="search-result">
            <action.icon size={14} />
            <span>{action.name}</span>
            <kbd class="shortcut">{action.shortcut}</kbd>
          </button>
        {/each}
      </div>
    {:else}
      <div class="search-section">
        <div class="section-header">
          <Search size={13} />
          <span>Results for "{query}"</span>
        </div>
        <div class="no-results">
          <p>Start typing to search across all your files, chats, and settings.</p>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .search-app {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .dev-banner {
    padding: 6px 16px;
    background: rgba(245, 158, 11, 0.1);
    border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    font-size: 11px;
    color: #f59e0b;
    text-align: center;
    flex-shrink: 0;
  }

  .search-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .search-input-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-muted);
  }

  .search-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 16px;
    color: var(--text-primary);
    outline: none;
    font-weight: 300;
  }

  .search-input::placeholder {
    color: var(--text-muted);
  }

  .search-body {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .search-section {
    margin-bottom: 8px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .search-result {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    text-align: left;
  }

  .search-result:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .search-result span {
    flex: 1;
  }

  .shortcut {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    font-family: inherit;
  }

  .search-result :global(.arrow) {
    opacity: 0;
    transition: opacity var(--transition-fast);
    color: var(--text-muted);
  }

  .search-result:hover :global(.arrow) {
    opacity: 1;
  }

  .no-results {
    padding: 24px;
    text-align: center;
  }

  .no-results p {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.5;
  }
</style>
