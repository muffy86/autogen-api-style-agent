<script lang="ts">
  import { Sparkles, MessageSquare, Folder, Terminal, Settings, Search } from 'lucide-svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';
  import { contextMenuStore } from '$lib/stores/contextmenu.svelte';

  const dockApps = [
    { id: 'launcher', name: 'Elysium', icon: Sparkles, isLauncher: true, group: 0 },
    { id: 'chat', name: 'Chat', icon: MessageSquare, isLauncher: false, group: 1 },
    { id: 'files', name: 'Files', icon: Folder, isLauncher: false, group: 1 },
    { id: 'terminal', name: 'Terminal', icon: Terminal, isLauncher: false, group: 1 },
    { id: 'settings', name: 'Settings', icon: Settings, isLauncher: false, group: 2 },
    { id: 'search', name: 'Search', icon: Search, isLauncher: false, group: 2 }
  ];

  let mouseX = $state(-1000);
  let isHovering = $state(false);
  let tooltipApp = $state<string | null>(null);
  let dockEl: HTMLDivElement | undefined = $state(undefined);

  const BASE_ITEM_WIDTH = 52;
  const SEPARATOR_WIDTH = 9;
  const DOCK_PADDING = 12;

  function getDockItemBaseCenter(index: number): number {
    if (!dockEl) return 0;
    const dockRect = dockEl.getBoundingClientRect();
    let offset = DOCK_PADDING;
    for (let i = 0; i < index; i++) {
      offset += BASE_ITEM_WIDTH;
      if (i + 1 < dockApps.length && dockApps[i + 1].group !== dockApps[i].group) {
        offset += SEPARATOR_WIDTH;
      }
    }
    return dockRect.left + offset + BASE_ITEM_WIDTH / 2;
  }

  function getScale(mx: number, centerX: number): number {
    if (!isHovering || centerX === 0) return 1;
    const distance = Math.abs(mx - centerX);
    const maxDistance = 120;
    const maxScale = 1.6;
    const minScale = 1.0;
    if (distance > maxDistance) return minScale;
    const ratio = 1 - distance / maxDistance;
    const factor = (1 + Math.cos(Math.PI * (1 - ratio))) / 2;
    return minScale + (maxScale - minScale) * factor;
  }

  function handleDockMousemove(e: MouseEvent) {
    mouseX = e.clientX;
    isHovering = true;
  }

  function handleDockMouseleave() {
    isHovering = false;
    mouseX = -1000;
    tooltipApp = null;
  }

  function handleClick(app: (typeof dockApps)[number]) {
    if (app.isLauncher) {
      desktopState.toggleLauncher();
    } else {
      desktopState.closeLauncher();
      windowStore.open(app.id);
    }
  }

  function handleContextMenu(e: MouseEvent, app: (typeof dockApps)[number]) {
    e.preventDefault();
    if (app.isLauncher) return;
    const hasWindow = windowStore.hasOpenWindow(app.id);
    contextMenuStore.open(e.clientX, e.clientY, [
      { id: 'open', label: 'Open', action: () => windowStore.open(app.id) },
      { id: 'new', label: 'New Instance', action: () => windowStore.open(app.id) },
      ...(hasWindow
        ? [
            { id: 'sep1', label: '', separator: true, action: () => {} },
            {
              id: 'close-all',
              label: 'Close All Windows',
              danger: true,
              action: () => windowStore.closeAll(app.id)
            }
          ]
        : [])
    ]);
  }
</script>

<div class="dock-container">
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="dock-wrap"
    onmousemove={handleDockMousemove}
    onmouseleave={handleDockMouseleave}
  >
    <div bind:this={dockEl} class="dock glass" class:dock-hover={isHovering}>
      {#each dockApps as app, i}
        {@const center = getDockItemBaseCenter(i)}
        {@const scale = getScale(mouseX, center)}
        {@const iconSize = Math.round(42 * scale)}
        {@const lift = (scale - 1) * 32}
        {@const isActive = !app.isLauncher && windowStore.hasOpenWindow(app.id)}
        {@const showSep = i > 0 && app.group !== dockApps[i - 1].group}
        {#if showSep}
          <div class="dock-separator"></div>
        {/if}
        <button
          class="dock-item"
          class:active={isActive}
          aria-label={app.name}
          onclick={() => handleClick(app)}
          oncontextmenu={(e) => handleContextMenu(e, app)}
          onmouseenter={() => (tooltipApp = app.id)}
          onmouseleave={() => (tooltipApp = null)}
          style="transform: perspective(800px) rotateX(-5deg) translateY(-{lift}px) scale({scale}); transition: transform {isHovering ? '150ms' : '400ms'} cubic-bezier(0.34, 1.56, 0.64, 1);"
        >
          <div class="dock-icon" style="width: {iconSize}px; height: {iconSize}px;">
            <app.icon size={Math.round(24 * scale)} strokeWidth={1.5} />
          </div>
          {#if tooltipApp === app.id}
            <div class="dock-tooltip">{app.name}</div>
          {/if}
          {#if isActive}
            <div class="dock-indicator"></div>
          {/if}
        </button>
      {/each}
    </div>
    <div class="dock-reflection"></div>
  </div>
</div>

<style>
  .dock-container {
    position: fixed;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 8000;
  }

  .dock-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .dock {
    display: flex;
    align-items: flex-end;
    gap: 2px;
    padding: 6px 12px 8px;
    border-radius: var(--radius-xl);
    transition: padding 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .dock.dock-hover {
    padding-bottom: 10px;
  }

  .dock-separator {
    width: 1px;
    height: 28px;
    background: rgba(255, 255, 255, 0.1);
    margin: 0 4px;
    align-self: center;
    flex-shrink: 0;
  }

  .dock-item {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 4px 6px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: var(--radius-md);
    transform-origin: bottom center;
    will-change: transform;
  }

  .dock-item:hover {
    color: var(--text-primary);
  }

  .dock-item:hover .dock-icon {
    filter: drop-shadow(0 0 10px rgba(139, 92, 246, 0.5));
  }

  .dock-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    transition: filter 200ms ease;
  }

  .dock-tooltip {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 10px;
    border-radius: 6px;
    background: rgba(16, 16, 28, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
    font-size: 12px;
    white-space: nowrap;
    pointer-events: none;
    animation: tooltipIn 120ms ease forwards;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .dock-indicator {
    position: absolute;
    bottom: -2px;
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 6px var(--accent);
    animation: pulseGlow 2s ease-in-out infinite;
  }

  .dock-reflection {
    width: 80%;
    height: 24px;
    margin-top: -1px;
    background: linear-gradient(
      to bottom,
      rgba(255, 255, 255, 0.03),
      transparent
    );
    border-radius: 0 0 16px 16px;
    transform: scaleY(-1);
    opacity: 0.15;
    mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), transparent);
    -webkit-mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.3), transparent);
    pointer-events: none;
  }
</style>
