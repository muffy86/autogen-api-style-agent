<script lang="ts">
  import { commandPaletteStore } from '$lib/stores/commandpalette.svelte';
  import { Search } from 'lucide-svelte';

  let selectedIndex = $state(0);
  let inputEl: HTMLInputElement | undefined = $state(undefined);

  const categoryLabels: Record<string, string> = {
    app: 'Apps',
    action: 'Actions',
    setting: 'Settings',
    recent: 'Recent'
  };

  let flatList = $derived(commandPaletteStore.filtered);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      e.preventDefault();
      commandPaletteStore.close();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = (selectedIndex + 1) % Math.max(1, flatList.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = (selectedIndex - 1 + Math.max(1, flatList.length)) % Math.max(1, flatList.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const cmd = flatList[selectedIndex];
      if (cmd) commandPaletteStore.execute(cmd);
    }
  }

  function handleInput(e: Event) {
    commandPaletteStore.query = (e.target as HTMLInputElement).value;
    selectedIndex = 0;
  }

  function handleBackdropClick(e: MouseEvent) {
    if ((e.target as HTMLElement).classList.contains('palette-overlay')) {
      commandPaletteStore.close();
    }
  }

  $effect(() => {
    if (commandPaletteStore.visible) {
      requestAnimationFrame(() => inputEl?.focus());
    }
  });
</script>

{#if commandPaletteStore.visible}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <div class="palette-overlay" onclick={handleBackdropClick}>
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="palette" onkeydown={handleKeydown}>
      <div class="palette-input-wrap">
        <Search size={18} strokeWidth={1.8} />
        <input
          bind:this={inputEl}
          class="palette-input"
          type="text"
          placeholder="Search apps, actions, settings..."
          value={commandPaletteStore.query}
          oninput={handleInput}
        />
        <kbd class="palette-kbd">ESC</kbd>
      </div>
      <div class="palette-results scrollbar-thin">
        {#each Object.entries(commandPaletteStore.grouped) as [cat, cmds]}
          <div class="palette-group">
            <div class="palette-group-label">{categoryLabels[cat] ?? cat}</div>
            {#each cmds as cmd}
              {@const idx = flatList.indexOf(cmd)}
              <!-- svelte-ignore a11y_click_events_have_key_events -->
              <div
                class="palette-item"
                class:selected={idx === selectedIndex}
                role="option"
                aria-selected={idx === selectedIndex}
                onclick={() => commandPaletteStore.execute(cmd)}
                onmouseenter={() => (selectedIndex = idx)}
              >
                {#if cmd.icon}
                  {@const Icon = cmd.icon}
                  <span class="palette-icon">
                    <Icon size={18} strokeWidth={1.6} />
                  </span>
                {/if}
                <div class="palette-item-text">
                  <span class="palette-item-title">{cmd.title}</span>
                  {#if cmd.description}
                    <span class="palette-item-desc">{cmd.description}</span>
                  {/if}
                </div>
                {#if cmd.shortcut}
                  <kbd class="palette-shortcut">{cmd.shortcut}</kbd>
                {/if}
              </div>
            {/each}
          </div>
        {/each}
        {#if flatList.length === 0}
          <div class="palette-empty">No results found</div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .palette-overlay {
    position: fixed;
    inset: 0;
    z-index: 9800;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    padding-top: 20vh;
    animation: fadeIn 120ms ease-out;
  }

  .palette {
    width: 100%;
    max-width: 640px;
    max-height: 460px;
    background: rgba(16, 16, 28, 0.95);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7), 0 0 1px rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: paletteIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    align-self: flex-start;
  }

  .palette-input-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--text-muted);
  }

  .palette-input {
    flex: 1;
    border: none;
    background: none;
    outline: none;
    font-size: 17px;
    color: var(--text-primary);
    font-family: inherit;
  }

  .palette-input::placeholder {
    color: var(--text-muted);
  }

  .palette-kbd {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted);
    font-family: inherit;
  }

  .palette-results {
    overflow-y: auto;
    padding: 6px;
    max-height: 380px;
  }

  .palette-group {
    margin-bottom: 4px;
  }

  .palette-group-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    padding: 8px 10px 4px;
  }

  .palette-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 80ms ease;
  }

  .palette-item.selected {
    background: var(--accent-subtle);
  }

  .palette-icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-secondary);
    flex-shrink: 0;
  }

  .palette-item.selected .palette-icon {
    background: rgba(139, 92, 246, 0.2);
    color: var(--accent-glow);
  }

  .palette-item-text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  .palette-item-title {
    font-size: 14px;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .palette-item-desc {
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .palette-shortcut {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--text-muted);
    flex-shrink: 0;
    font-family: inherit;
  }

  .palette-empty {
    padding: 24px;
    text-align: center;
    color: var(--text-muted);
    font-size: 14px;
  }
</style>
