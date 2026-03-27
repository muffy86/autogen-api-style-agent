<script lang="ts">
  import { Search, Clock, Zap, ArrowRight, MessageSquare, Folder, Terminal, Settings, LayoutDashboard, AppWindow } from 'lucide-svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { chatStore } from '$lib/stores/chat.svelte';
  import { appRegistry } from '$lib/stores/apps.svelte';

  let query = $state('');
  let selectedIndex = $state(0);

  const iconMap: Record<string, any> = {
    'message-square': MessageSquare,
    folder: Folder,
    terminal: Terminal,
    settings: Settings,
    search: Search,
    'layout-dashboard': LayoutDashboard
  };

  interface SearchResult {
    id: string;
    label: string;
    category: string;
    icon: any;
    action: () => void;
  }

  let results = $derived.by((): SearchResult[] => {
    const q = query.toLowerCase().trim();
    if (!q) return [];

    const items: SearchResult[] = [];

    for (const app of appRegistry.apps) {
      if (app.name.toLowerCase().includes(q) || app.description.toLowerCase().includes(q)) {
        items.push({
          id: `app-${app.id}`,
          label: app.name,
          category: 'Apps',
          icon: iconMap[app.icon] ?? Search,
          action: () => windowStore.open(app.id),
        });
      }
    }

    for (const win of windowStore.windows) {
      if (win.title.toLowerCase().includes(q) || win.appId.toLowerCase().includes(q)) {
        items.push({
          id: `win-${win.id}`,
          label: `${win.title} (Window)`,
          category: 'Open Windows',
          icon: AppWindow,
          action: () => {
            if (win.isMinimized) {
              win.isMinimized = false;
            }
            windowStore.focus(win.id);
          },
        });
      }
    }

    for (const conv of chatStore.conversations) {
      if (conv.title.toLowerCase().includes(q)) {
        items.push({
          id: `conv-${conv.id}`,
          label: conv.title,
          category: 'Conversations',
          icon: MessageSquare,
          action: () => {
            chatStore.setActive(conv.id);
            windowStore.open('chat');
          },
        });
      }
    }

    return items;
  });

  let grouped = $derived.by(() => {
    const groups: Record<string, SearchResult[]> = {};
    for (const r of results) {
      if (!groups[r.category]) groups[r.category] = [];
      groups[r.category].push(r);
    }
    return Object.entries(groups);
  });

  let flatResults = $derived(results);

  $effect(() => {
    query;
    selectedIndex = 0;
  });

  const quickActions = [
    { name: 'New Chat', icon: MessageSquare, shortcut: '⌘ N', appId: 'chat', action: () => { chatStore.createConversation(); windowStore.open('chat'); } },
    { name: 'Open Files', icon: Folder, shortcut: '⌘ O', appId: 'files', action: () => windowStore.open('files') },
    { name: 'Terminal', icon: Terminal, shortcut: '⌘ T', appId: 'terminal', action: () => windowStore.open('terminal') },
    { name: 'Settings', icon: Settings, shortcut: '⌘ ,', appId: 'settings', action: () => windowStore.open('settings') },
    { name: 'Dashboard', icon: LayoutDashboard, shortcut: '⌘ D', appId: 'dashboard', action: () => windowStore.open('dashboard') }
  ];

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = Math.min(selectedIndex + 1, flatResults.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = Math.max(selectedIndex - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (flatResults[selectedIndex]) {
        flatResults[selectedIndex].action();
      }
    }
  }

  function getFlatIndex(catIdx: number, itemIdx: number): number {
    let idx = 0;
    for (let i = 0; i < catIdx; i++) {
      idx += grouped[i][1].length;
    }
    return idx + itemIdx;
  }
</script>

<div class="search-app">
  <div class="dev-banner">
    <span>🔍 Search is under development</span>
  </div>
  <div class="search-header">
    <div class="search-input-wrapper">
      <Search size={18} />
      <!-- svelte-ignore a11y_autofocus -->
      <input
        class="search-input"
        type="text"
        placeholder="Search apps, windows, conversations..."
        bind:value={query}
        onkeydown={handleKeydown}
        autofocus={true}
      />
    </div>
  </div>

  <div class="search-body scrollbar-thin">
    {#if !query}
      <div class="search-section">
        <div class="section-header">
          <Zap size={13} />
          <span>Quick Actions</span>
        </div>
        {#each quickActions as action}
          <button class="search-result" onclick={() => action.action()}>
            <action.icon size={14} />
            <span>{action.name}</span>
            <kbd class="shortcut">{action.shortcut}</kbd>
          </button>
        {/each}
      </div>

      {#if chatStore.conversations.length > 0}
        <div class="search-section">
          <div class="section-header">
            <Clock size={13} />
            <span>Recent Conversations</span>
          </div>
          {#each chatStore.conversations.slice(0, 5) as conv}
            <button class="search-result" onclick={() => { chatStore.setActive(conv.id); windowStore.open('chat'); }}>
              <MessageSquare size={14} />
              <span>{conv.title}</span>
              <ArrowRight size={12} class="arrow" />
            </button>
          {/each}
        </div>
      {/if}
    {:else if results.length === 0}
      <div class="search-section">
        <div class="section-header">
          <Search size={13} />
          <span>Results for "{query}"</span>
        </div>
        <div class="no-results">
          <p>No results found. Try different keywords.</p>
        </div>
      </div>
    {:else}
      {#each grouped as [category, items], catIdx}
        <div class="search-section">
          <div class="section-header">
            <Search size={13} />
            <span>{category}</span>
          </div>
          {#each items as item, itemIdx}
            {@const flatIdx = getFlatIndex(catIdx, itemIdx)}
            <button
              class="search-result"
              class:selected={flatIdx === selectedIndex}
              onmouseenter={() => (selectedIndex = flatIdx)}
              onclick={() => item.action()}
            >
              <item.icon size={14} />
              <span>{item.label}</span>
              <ArrowRight size={12} class="arrow" />
            </button>
          {/each}
        </div>
      {/each}
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
    font-family: inherit;
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
    font-family: inherit;
  }

  .search-result:hover,
  .search-result.selected {
    background: var(--accent-subtle);
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
