<script lang="ts">
  import { contextMenuStore } from '$lib/stores/contextmenu.svelte';
  import type { ContextMenuItem } from '$lib/types';

  let focusIndex = $state(-1);
  let menuEl: HTMLDivElement | undefined = $state(undefined);

  let nonSepItems = $derived(contextMenuStore.items.filter((i) => !i.separator));

  function handleKeydown(e: KeyboardEvent) {
    if (!contextMenuStore.visible) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      contextMenuStore.close();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      focusIndex = (focusIndex + 1) % nonSepItems.length;
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      focusIndex = (focusIndex - 1 + nonSepItems.length) % nonSepItems.length;
    } else if (e.key === 'Enter' && focusIndex >= 0) {
      e.preventDefault();
      const item = nonSepItems[focusIndex];
      if (item && !item.disabled) {
        item.action();
        contextMenuStore.close();
      }
    }
  }

  function handleItemClick(item: ContextMenuItem) {
    if (item.disabled) return;
    item.action();
    contextMenuStore.close();
  }

  function handleBackdropClick() {
    contextMenuStore.close();
  }

  $effect(() => {
    if (contextMenuStore.visible) {
      focusIndex = -1;
      window.addEventListener('keydown', handleKeydown);
      return () => window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

{#if contextMenuStore.visible}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="ctx-backdrop" onclick={handleBackdropClick}></div>
  <div
    bind:this={menuEl}
    class="ctx-menu"
    style="left: {contextMenuStore.x}px; top: {contextMenuStore.y}px;"
    role="menu"
  >
    {#each contextMenuStore.items as item, i}
      {#if item.separator}
        <div class="ctx-separator"></div>
      {:else}
        {@const itemIdx = nonSepItems.indexOf(item)}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <div
          class="ctx-item"
          class:focused={itemIdx === focusIndex}
          class:disabled={item.disabled}
          class:danger={item.danger}
          role="menuitem"
          onclick={() => handleItemClick(item)}
          onmouseenter={() => (focusIndex = itemIdx)}
        >
          {#if item.icon}
            {@const Icon = item.icon}
            <span class="ctx-icon">
              <Icon size={15} strokeWidth={1.8} />
            </span>
          {:else}
            <span class="ctx-icon-spacer"></span>
          {/if}
          <span class="ctx-label">{item.label}</span>
          {#if item.shortcut}
            <span class="ctx-shortcut">{item.shortcut}</span>
          {/if}
        </div>
      {/if}
    {/each}
  </div>
{/if}

<style>
  .ctx-backdrop {
    position: fixed;
    inset: 0;
    z-index: 9499;
  }

  .ctx-menu {
    position: fixed;
    z-index: 9500;
    min-width: 200px;
    max-width: 280px;
    padding: 5px;
    background: rgba(18, 18, 30, 0.92);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 255, 255, 0.1);
    animation: contextMenuIn 120ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  .ctx-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-primary);
    transition: background 80ms ease;
    user-select: none;
  }

  .ctx-item.focused {
    background: var(--accent-subtle);
  }

  .ctx-item.disabled {
    opacity: 0.4;
    pointer-events: none;
  }

  .ctx-item.danger.focused {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
  }

  .ctx-icon {
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    flex-shrink: 0;
  }

  .ctx-item.focused .ctx-icon {
    color: var(--accent-glow);
  }

  .ctx-item.danger.focused .ctx-icon {
    color: #f87171;
  }

  .ctx-icon-spacer {
    width: 18px;
    flex-shrink: 0;
  }

  .ctx-label {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .ctx-shortcut {
    font-size: 11px;
    color: var(--text-muted);
    margin-left: auto;
    padding-left: 16px;
    flex-shrink: 0;
  }

  .ctx-separator {
    height: 1px;
    margin: 4px 8px;
    background: rgba(255, 255, 255, 0.08);
  }
</style>
