<script lang="ts">
  import type { WindowState } from '$lib/types';
  import { windowStore, detectSnapZone } from '$lib/stores/windows.svelte';
  import { contextMenuStore } from '$lib/stores/contextmenu.svelte';
  import type { Component } from 'svelte';
  import { Minus, Square, X, Maximize2, ArrowLeftToLine, ArrowRightToLine } from 'lucide-svelte';
  import { appRegistry } from '$lib/stores/apps.svelte';

  interface Props {
    win: WindowState;
    appComponent: Component;
  }

  let { win, appComponent }: Props = $props();

  let isDragging = $state(false);
  let isResizing = $state(false);
  let resizeDir = $state('');
  let dragStartX = $state(0);
  let dragStartY = $state(0);
  let dragStartWinX = $state(0);
  let dragStartWinY = $state(0);
  let resizeStartW = $state(0);
  let resizeStartH = $state(0);
  let resizeStartX = $state(0);
  let resizeStartY = $state(0);
  let windowEl: HTMLDivElement | undefined = $state(undefined);
  let isClosing = $state(false);
  let controlsHovered = $state(false);

  let appDef = $derived(appRegistry.getApp(win.appId));

  function handleTitleMousedown(e: MouseEvent) {
    if ((e.target as HTMLElement).closest('.window-controls')) return;
    if (win.isMaximized) return;
    e.preventDefault();
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    dragStartWinX = win.x;
    dragStartWinY = win.y;
    windowStore.focus(win.id);
    document.addEventListener('mousemove', handleDragMove);
    document.addEventListener('mouseup', handleDragEnd);
  }

  function handleDragMove(e: MouseEvent) {
    if (!isDragging) return;
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    windowStore.move(win.id, dragStartWinX + dx, dragStartWinY + dy);

    const zone = detectSnapZone(e.clientX, e.clientY);
    windowStore.setSnapZone(zone);
  }

  function handleDragEnd(e: MouseEvent) {
    if (isDragging && windowStore.currentSnapZone) {
      windowStore.snap(win.id, windowStore.currentSnapZone);
    }
    isDragging = false;
    windowStore.clearSnapZone();
    document.removeEventListener('mousemove', handleDragMove);
    document.removeEventListener('mouseup', handleDragEnd);
  }

  function handleResizeMousedown(e: MouseEvent, direction: string) {
    e.preventDefault();
    e.stopPropagation();
    isResizing = true;
    resizeDir = direction;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    resizeStartW = win.width;
    resizeStartH = win.height;
    resizeStartX = win.x;
    resizeStartY = win.y;
    windowStore.focus(win.id);
    document.addEventListener('mousemove', handleResizeMove);
    document.addEventListener('mouseup', handleResizeEnd);
  }

  function handleResizeMove(e: MouseEvent) {
    if (!isResizing) return;
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;

    let newW = resizeStartW;
    let newH = resizeStartH;
    let newX = resizeStartX;
    let newY = resizeStartY;

    if (resizeDir.includes('e')) newW = resizeStartW + dx;
    if (resizeDir.includes('w')) {
      newW = resizeStartW - dx;
      if (newW >= win.minWidth) newX = resizeStartX + dx;
      else newW = win.minWidth;
    }
    if (resizeDir.includes('s')) newH = resizeStartH + dy;
    if (resizeDir.includes('n')) {
      newH = resizeStartH - dy;
      if (newH >= win.minHeight) newY = resizeStartY + dy;
      else newH = win.minHeight;
    }

    windowStore.resize(win.id, newW, newH, newX, newY);
  }

  function handleResizeEnd() {
    isResizing = false;
    resizeDir = '';
    document.removeEventListener('mousemove', handleResizeMove);
    document.removeEventListener('mouseup', handleResizeEnd);
  }

  function handleTitleDblClick() {
    windowStore.maximize(win.id);
  }

  function handleClose() {
    isClosing = true;
    setTimeout(() => {
      windowStore.close(win.id);
    }, 150);
  }

  function handleFocus() {
    windowStore.focus(win.id);
  }

  function handleTitleContextMenu(e: MouseEvent) {
    e.preventDefault();
    contextMenuStore.open(e.clientX, e.clientY, [
      { id: 'min', label: 'Minimize', shortcut: '', action: () => windowStore.minimize(win.id) },
      { id: 'max', label: win.isMaximized ? 'Restore' : 'Maximize', action: () => windowStore.maximize(win.id) },
      { id: 'sep1', label: '', separator: true, action: () => {} },
      { id: 'snap-l', label: 'Snap Left', icon: ArrowLeftToLine, action: () => windowStore.snap(win.id, 'left') },
      { id: 'snap-r', label: 'Snap Right', icon: ArrowRightToLine, action: () => windowStore.snap(win.id, 'right') },
      { id: 'sep2', label: '', separator: true, action: () => {} },
      { id: 'close', label: 'Close Window', shortcut: '⌘W', danger: true, icon: X, action: handleClose }
    ]);
  }
</script>

{#if !win.isMinimized}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    bind:this={windowEl}
    class="window"
    class:focused={win.isFocused}
    class:maximized={win.isMaximized}
    class:closing={isClosing}
    class:dragging={isDragging || isResizing}
    style="
      left: {win.x}px;
      top: {win.y}px;
      width: {win.width}px;
      height: {win.height}px;
      z-index: {win.zIndex};
    "
    onmousedown={handleFocus}
  >
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="title-bar"
      onmousedown={handleTitleMousedown}
      ondblclick={handleTitleDblClick}
      oncontextmenu={handleTitleContextMenu}
    >
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div
        class="window-controls"
        onmouseenter={() => (controlsHovered = true)}
        onmouseleave={() => (controlsHovered = false)}
      >
        <button
          class="traffic-light close"
          class:show-icon={controlsHovered}
          class:unfocused={!win.isFocused}
          aria-label="Close"
          onclick={handleClose}
        >
          {#if controlsHovered}
            <X size={8} strokeWidth={3} />
          {/if}
        </button>
        <button
          class="traffic-light minimize"
          class:show-icon={controlsHovered}
          class:unfocused={!win.isFocused}
          aria-label="Minimize"
          onclick={() => windowStore.minimize(win.id)}
        >
          {#if controlsHovered}
            <Minus size={8} strokeWidth={3} />
          {/if}
        </button>
        <button
          class="traffic-light maximize"
          class:show-icon={controlsHovered}
          class:unfocused={!win.isFocused}
          aria-label="Maximize"
          onclick={() => windowStore.maximize(win.id)}
        >
          {#if controlsHovered}
            <Maximize2 size={7} strokeWidth={2.5} />
          {/if}
        </button>
      </div>
      <div class="title-center">
        <span class="title-text">{win.title}</span>
      </div>
      <div class="title-spacer"></div>
    </div>

    <div class="window-body">
      {@render appSlot()}
    </div>

    {#if !win.isMaximized}
      <div class="resize-handle n" onmousedown={(e) => handleResizeMousedown(e, 'n')}></div>
      <div class="resize-handle s" onmousedown={(e) => handleResizeMousedown(e, 's')}></div>
      <div class="resize-handle e" onmousedown={(e) => handleResizeMousedown(e, 'e')}></div>
      <div class="resize-handle w" onmousedown={(e) => handleResizeMousedown(e, 'w')}></div>
      <div class="resize-handle ne" onmousedown={(e) => handleResizeMousedown(e, 'ne')}></div>
      <div class="resize-handle nw" onmousedown={(e) => handleResizeMousedown(e, 'nw')}></div>
      <div class="resize-handle se" onmousedown={(e) => handleResizeMousedown(e, 'se')}></div>
      <div class="resize-handle sw" onmousedown={(e) => handleResizeMousedown(e, 'sw')}></div>
    {/if}
  </div>
{/if}

{#snippet appSlot()}
  {@const AppComp = appComponent}
  <AppComp />
{/snippet}

<style>
  .window {
    position: fixed;
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: var(--window-bg);
    border: 1px solid var(--glass-border);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.5),
      0 0 1px rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    animation: windowIn 250ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    will-change: transform;
    transition: box-shadow var(--transition-smooth);
  }

  .window.closing {
    animation: windowOut 150ms ease-in forwards;
    pointer-events: none;
  }

  .window.dragging {
    transition: none !important;
  }

  .window.focused {
    box-shadow:
      0 12px 48px rgba(0, 0, 0, 0.6),
      0 0 1px rgba(255, 255, 255, 0.15),
      var(--shadow-glow);
  }

  .window.maximized {
    border-radius: 0;
    border: none;
  }

  .title-bar {
    height: 40px;
    display: flex;
    align-items: center;
    padding: 0 12px;
    background: var(--titlebar-bg);
    border-bottom: 1px solid var(--border-subtle);
    cursor: grab;
    flex-shrink: 0;
  }

  .title-bar:active {
    cursor: grabbing;
  }

  .window-controls {
    display: flex;
    align-items: center;
    gap: 7px;
    flex-shrink: 0;
    padding-right: 8px;
  }

  .traffic-light {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 150ms ease;
    padding: 0;
    color: rgba(0, 0, 0, 0.6);
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15);
  }

  .traffic-light.close {
    background: #ff5f57;
  }

  .traffic-light.minimize {
    background: #febc2e;
  }

  .traffic-light.maximize {
    background: #28c840;
  }

  .traffic-light.unfocused {
    background: #4a4a4a;
  }

  .traffic-light:hover {
    filter: brightness(1.1);
  }

  .title-center {
    flex: 1;
    display: flex;
    justify-content: center;
    min-width: 0;
  }

  .title-text {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .window:not(.focused) .title-text {
    color: var(--text-muted);
  }

  .title-spacer {
    width: 64px;
    flex-shrink: 0;
  }

  .window-body {
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  .resize-handle {
    position: absolute;
    z-index: 10;
  }

  .resize-handle.n {
    top: -3px; left: 6px; right: 6px; height: 6px;
    cursor: n-resize;
  }
  .resize-handle.s {
    bottom: -3px; left: 6px; right: 6px; height: 6px;
    cursor: s-resize;
  }
  .resize-handle.e {
    top: 6px; right: -3px; bottom: 6px; width: 6px;
    cursor: e-resize;
  }
  .resize-handle.w {
    top: 6px; left: -3px; bottom: 6px; width: 6px;
    cursor: w-resize;
  }
  .resize-handle.ne {
    top: -3px; right: -3px; width: 12px; height: 12px;
    cursor: ne-resize;
  }
  .resize-handle.nw {
    top: -3px; left: -3px; width: 12px; height: 12px;
    cursor: nw-resize;
  }
  .resize-handle.se {
    bottom: -3px; right: -3px; width: 12px; height: 12px;
    cursor: se-resize;
  }
  .resize-handle.sw {
    bottom: -3px; left: -3px; width: 12px; height: 12px;
    cursor: sw-resize;
  }
</style>
