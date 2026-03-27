<script lang="ts">
  import { Search, MessageSquare, Folder, Terminal, Settings, LayoutDashboard, Moon, Sun, X as XIcon, Maximize, Command } from 'lucide-svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { themeStore } from '$lib/stores/theme.svelte';
  import { chatStore } from '$lib/stores/chat.svelte';

  interface Props {
    visible: boolean;
    onclose: () => void;
  }

  let { visible, onclose }: Props = $props();

  let query = $state('');
  let selectedIndex = $state(0);
  let inputEl: HTMLInputElement | undefined = $state(undefined);

  interface PaletteAction {
    id: string;
    label: string;
    category: string;
    icon: any;
    shortcut?: string;
    action: () => void;
  }

  const appActions: PaletteAction[] = [
    { id: 'open-chat', label: 'Open Chat', category: 'Apps', icon: MessageSquare, action: () => { windowStore.open('chat'); onclose(); } },
    { id: 'open-files', label: 'Open Files', category: 'Apps', icon: Folder, action: () => { windowStore.open('files'); onclose(); } },
    { id: 'open-terminal', label: 'Open Terminal', category: 'Apps', icon: Terminal, action: () => { windowStore.open('terminal'); onclose(); } },
    { id: 'open-settings', label: 'Open Settings', category: 'Apps', icon: Settings, action: () => { windowStore.open('settings'); onclose(); } },
    { id: 'open-search', label: 'Open Search', category: 'Apps', icon: Search, action: () => { windowStore.open('search'); onclose(); } },
    { id: 'open-dashboard', label: 'Open Dashboard', category: 'Apps', icon: LayoutDashboard, action: () => { windowStore.open('dashboard'); onclose(); } },
  ];

  const themeActions: PaletteAction[] = [
    { id: 'theme-dark', label: 'Switch to Dark Theme', category: 'Theme', icon: Moon, action: () => { themeStore.setTheme('dark'); onclose(); } },
    { id: 'theme-light', label: 'Switch to Light Theme', category: 'Theme', icon: Sun, action: () => { themeStore.setTheme('light'); onclose(); } },
  ];

  const quickActions: PaletteAction[] = [
    { id: 'new-chat', label: 'New Chat', category: 'Actions', icon: MessageSquare, shortcut: '⌘N', action: () => { chatStore.createConversation(); windowStore.open('chat'); onclose(); } },
    { id: 'close-window', label: 'Close Active Window', category: 'Actions', icon: XIcon, action: () => { const aw = windowStore.activeWindow; if (aw) windowStore.close(aw.id); onclose(); } },
    { id: 'maximize-window', label: 'Maximize Active Window', category: 'Actions', icon: Maximize, action: () => { const aw = windowStore.activeWindow; if (aw) windowStore.maximize(aw.id); onclose(); } },
  ];

  const allActions = [...appActions, ...themeActions, ...quickActions];

  let filtered = $derived.by(() => {
    if (!query.trim()) return allActions;
    const q = query.toLowerCase();
    return allActions.filter(
      (a) => a.label.toLowerCase().includes(q) || a.category.toLowerCase().includes(q)
    );
  });

  let grouped = $derived.by(() => {
    const groups: Record<string, PaletteAction[]> = {};
    for (const item of filtered) {
      if (!groups[item.category]) groups[item.category] = [];
      groups[item.category].push(item);
    }
    return Object.entries(groups);
  });

  $effect(() => {
    if (visible && inputEl) {
      query = '';
      selectedIndex = 0;
      requestAnimationFrame(() => inputEl?.focus());
    }
  });

  $effect(() => {
    query;
    selectedIndex = 0;
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      onclose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = Math.min(selectedIndex + 1, filtered.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = Math.max(selectedIndex - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        filtered[selectedIndex].action();
      }
    }
  }

  function handleBackdropClick(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('palette-overlay')) {
      onclose();
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

{#if visible}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="palette-overlay" onclick={handleBackdropClick}>
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="palette-container glass" onkeydown={handleKeydown}>
      <div class="palette-input-row">
        <Command size={16} strokeWidth={2} />
        <input
          bind:this={inputEl}
          class="palette-input"
          type="text"
          placeholder="Type a command..."
          bind:value={query}
        />
        <kbd class="palette-esc">ESC</kbd>
      </div>
      <div class="palette-results scrollbar-thin">
        {#if filtered.length === 0}
          <div class="palette-empty">No results found</div>
        {:else}
          {#each grouped as [category, items], catIdx}
            <div class="palette-category">
              <span class="palette-category-label">{category}</span>
              {#each items as item, itemIdx}
                {@const flatIdx = getFlatIndex(catIdx, itemIdx)}
                <button
                  class="palette-item"
                  class:selected={flatIdx === selectedIndex}
                  onmouseenter={() => (selectedIndex = flatIdx)}
                  onclick={() => item.action()}
                >
                  <item.icon size={16} strokeWidth={1.5} />
                  <span class="palette-item-label">{item.label}</span>
                  {#if item.shortcut}
                    <kbd class="palette-shortcut">{item.shortcut}</kbd>
                  {/if}
                </button>
              {/each}
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .palette-overlay {
    position: fixed;
    inset: 0;
    z-index: 8600;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    padding-top: 20vh;
    animation: fadeIn 120ms ease-out;
  }

  .palette-container {
    width: 520px;
    max-height: 420px;
    border-radius: var(--radius-lg);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: paletteIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    box-shadow: 0 16px 64px rgba(0, 0, 0, 0.5), 0 0 1px rgba(255, 255, 255, 0.1);
    align-self: flex-start;
  }

  .palette-input-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-muted);
  }

  .palette-input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 16px;
    color: var(--text-primary);
    outline: none;
    font-weight: 400;
    font-family: inherit;
  }

  .palette-input::placeholder {
    color: var(--text-muted);
  }

  .palette-esc {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    font-family: inherit;
  }

  .palette-results {
    flex: 1;
    overflow-y: auto;
    padding: 6px;
  }

  .palette-category {
    margin-bottom: 4px;
  }

  .palette-category-label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    padding: 6px 10px 4px;
  }

  .palette-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 10px 10px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 14px;
    color: var(--text-secondary);
    transition: all 80ms ease;
    text-align: left;
    font-family: inherit;
  }

  .palette-item:hover,
  .palette-item.selected {
    background: var(--accent-subtle);
    color: var(--text-primary);
  }

  .palette-item-label {
    flex: 1;
  }

  .palette-shortcut {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    font-family: inherit;
  }

  .palette-empty {
    padding: 24px;
    text-align: center;
    font-size: 13px;
    color: var(--text-muted);
  }
</style>
