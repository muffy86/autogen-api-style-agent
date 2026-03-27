<script lang="ts">
  import { Sparkles, MessageSquare, Folder, Terminal, Settings, Search, LayoutDashboard, BookOpen } from 'lucide-svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';

  const dockApps = [
    { id: 'launcher', name: 'Elysium', icon: Sparkles, isLauncher: true },
    { id: 'chat', name: 'Chat', icon: MessageSquare, isLauncher: false },
    { id: 'files', name: 'Files', icon: Folder, isLauncher: false },
    { id: 'terminal', name: 'Terminal', icon: Terminal, isLauncher: false },
    { id: 'settings', name: 'Settings', icon: Settings, isLauncher: false },
    { id: 'search', name: 'Search', icon: Search, isLauncher: false },
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard, isLauncher: false },
    { id: 'knowledge', name: 'Knowledge', icon: BookOpen, isLauncher: false }
  ];

  let bouncingApp = $state<string | null>(null);
  let hoveredApp = $state<string | null>(null);

  function handleClick(app: (typeof dockApps)[number]) {
    if (app.isLauncher) {
      desktopState.toggleLauncher();
    } else {
      desktopState.closeLauncher();

      const wasOpen = windowStore.hasOpenWindow(app.id);
      windowStore.open(app.id);

      if (!wasOpen) {
        bouncingApp = app.id;
        setTimeout(() => (bouncingApp = null), 600);
      }
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
        onmouseenter={() => (hoveredApp = app.id)}
        onmouseleave={() => (hoveredApp = null)}
      >
        <div class="dock-icon" class:bouncing={bouncingApp === app.id}>
          <app.icon size={24} strokeWidth={1.5} />
        </div>
        {#if hoveredApp === app.id}
          <div class="dock-tooltip">{app.name}</div>
        {/if}
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

  .dock-item:hover .dock-icon:not(.bouncing) {
    transform: scale(1.2) translateY(-2px);
    filter: drop-shadow(0 0 8px var(--accent-subtle));
  }

  .dock-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-smooth);
  }

  .dock-icon.bouncing {
    animation: dockBounce 600ms cubic-bezier(0.36, 0, 0.66, -0.56) forwards;
  }

  .dock-tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-bottom: 8px;
    padding: 4px 10px;
    border-radius: 6px;
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    pointer-events: none;
    animation: fadeIn 120ms ease-out;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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
