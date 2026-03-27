<script lang="ts">
  import { desktopState } from '$lib/stores/desktop.svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { appRegistry } from '$lib/stores/apps.svelte';
  import { MessageSquare, Folder, Terminal, Settings, Search, LayoutDashboard } from 'lucide-svelte';

  const iconMap: Record<string, any> = {
    'message-square': MessageSquare,
    folder: Folder,
    terminal: Terminal,
    settings: Settings,
    search: Search,
    'layout-dashboard': LayoutDashboard
  };

  function launchApp(appId: string) {
    windowStore.open(appId);
    desktopState.closeLauncher();
  }

  function handleBackdropClick(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('launcher-overlay')) {
      desktopState.closeLauncher();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      desktopState.closeLauncher();
    }
  }

  $effect(() => {
    if (desktopState.launcherOpen) {
      window.addEventListener('keydown', handleKeydown);
      return () => window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

{#if desktopState.launcherOpen}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="launcher-overlay" onclick={handleBackdropClick}>
    <div class="launcher-content">
      <h2 class="launcher-title">Applications</h2>
      <div class="launcher-grid">
        {#each appRegistry.apps as app}
          {@const IconComp = iconMap[app.icon]}
          <button class="app-card" onclick={() => launchApp(app.id)}>
            <div class="app-card-icon">
              {#if IconComp}
                <IconComp size={28} strokeWidth={1.5} />
              {/if}
            </div>
            <div class="app-card-info">
              <span class="app-card-name">{app.name}</span>
              <span class="app-card-desc">{app.description}</span>
            </div>
          </button>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .launcher-overlay {
    position: fixed;
    inset: 0;
    z-index: 8500;
    background: rgba(6, 6, 10, 0.7);
    backdrop-filter: blur(30px);
    -webkit-backdrop-filter: blur(30px);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: launcherIn 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  .launcher-content {
    max-width: 700px;
    width: 90%;
  }

  .launcher-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 28px;
    text-align: center;
    letter-spacing: -0.02em;
  }

  .launcher-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  .app-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px 16px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    cursor: pointer;
    transition: all var(--transition-smooth);
    text-align: center;
  }

  .app-card:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-default);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }

  .app-card:active {
    transform: translateY(0);
  }

  .app-card-icon {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-md);
    background: var(--accent-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-glow);
    transition: all var(--transition-smooth);
  }

  .app-card:hover .app-card-icon {
    background: rgba(139, 92, 246, 0.25);
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.2);
  }

  .app-card-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .app-card-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .app-card-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
</style>
