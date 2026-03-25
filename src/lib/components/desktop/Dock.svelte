<script lang="ts">
  import { Sparkles, MessageSquare, Folder, Terminal, Settings, Search, LayoutDashboard, Github } from 'lucide-svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';

  const dockApps = [
    { id: 'launcher', name: 'Elysium', icon: Sparkles, isLauncher: true },
    { id: 'chat', name: 'Chat', icon: MessageSquare, isLauncher: false },
    { id: 'github', name: 'GitHub', icon: Github, isLauncher: false },
    { id: 'files', name: 'Files', icon: Folder, isLauncher: false },
    { id: 'terminal', name: 'Terminal', icon: Terminal, isLauncher: false },
    { id: 'settings', name: 'Settings', icon: Settings, isLauncher: false },
    { id: 'search', name: 'Search', icon: Search, isLauncher: false },
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, isLauncher: false }
  ];

  function handleClick(app: (typeof dockApps)[number]) {
    if (app.isLauncher) {
      desktopState.toggleLauncher();
    } else {
      desktopState.closeLauncher();
      windowStore.open(app.id);
    }
  }
</script>

<div class="dock-container">
  <div class="dock glass">
    {#each dockApps as app}
      {@const isActive = !app.isLauncher && windowStore.hasOpenWindow(app.id)}
      <button
        class="dock-item"
        class:active={isActive}
        aria-label={app.name}
        onclick={() => handleClick(app)}
      >
        <div class="dock-icon">
          <app.icon size={24} strokeWidth={1.5} />
        </div>
        <span class="dock-label">{app.name}</span>
        {#if isActive}
          <div class="dock-indicator"></div>
        {/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .dock-container {
    position: fixed;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 8000;
  }

  .dock {
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 6px 10px;
    border-radius: var(--radius-xl);
  }

  .dock-item {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 8px 12px 6px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: all var(--transition-smooth);
  }

  .dock-item:hover {
    color: var(--text-primary);
    background: var(--bg-surface-hover);
  }

  .dock-item:hover .dock-icon {
    transform: scale(1.2) translateY(-2px);
    filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.4));
  }

  .dock-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-smooth);
  }

  .dock-label {
    font-size: 10px;
    opacity: 0.7;
    transition: opacity var(--transition-fast);
    white-space: nowrap;
  }

  .dock-item:hover .dock-label {
    opacity: 1;
  }

  .dock-indicator {
    position: absolute;
    bottom: 2px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
  }
</style>
