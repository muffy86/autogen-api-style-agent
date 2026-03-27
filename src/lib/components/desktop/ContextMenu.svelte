<script lang="ts">
  interface MenuItem {
    label: string;
    icon?: any;
    action?: () => void;
    separator?: boolean;
  }

  interface Props {
    x: number;
    y: number;
    items: MenuItem[];
    onclose: () => void;
  }

  let { x, y, items, onclose }: Props = $props();

  let menuEl: HTMLDivElement | undefined = $state(undefined);

  let adjustedX = $derived.by(() => {
    if (typeof window === 'undefined') return x;
    const menuW = 200;
    return x + menuW > window.innerWidth ? window.innerWidth - menuW - 8 : x;
  });

  let adjustedY = $derived.by(() => {
    if (typeof window === 'undefined') return y;
    const menuH = items.length * 36;
    return y + menuH > window.innerHeight ? window.innerHeight - menuH - 8 : y;
  });

  $effect(() => {
    function handleClick(e: MouseEvent) {
      if (menuEl && !menuEl.contains(e.target as Node)) {
        onclose();
      }
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onclose();
    }
    document.addEventListener('mousedown', handleClick, true);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handleClick, true);
      document.removeEventListener('keydown', handleKey);
    };
  });
</script>

<div
  bind:this={menuEl}
  class="context-menu glass"
  style="left: {adjustedX}px; top: {adjustedY}px"
>
  {#each items as item}
    {#if item.separator}
      <div class="menu-separator"></div>
    {:else}
      <button
        class="menu-item"
        onclick={() => {
          if (item.action) item.action();
          onclose();
        }}
      >
        {#if item.icon}
          {@const Icon = item.icon}
          <Icon size={14} strokeWidth={1.5} />
        {/if}
        <span>{item.label}</span>
      </button>
    {/if}
  {/each}
</div>

<style>
  .context-menu {
    position: fixed;
    z-index: 8800;
    min-width: 180px;
    padding: 4px;
    border-radius: var(--radius-md);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 1px rgba(255, 255, 255, 0.1);
    animation: fadeIn 100ms ease-out;
  }

  .menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
    transition: all 80ms ease;
    text-align: left;
    font-family: inherit;
  }

  .menu-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .menu-separator {
    height: 1px;
    margin: 4px 8px;
    background: var(--border-subtle);
  }
</style>
