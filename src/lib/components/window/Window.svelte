<script lang="ts">
  import type { WindowState } from '$lib/types';
  import { windowStore } from '$lib/stores/windows.svelte';
  import type { Component } from 'svelte';
  import { Minus, Square, X } from 'lucide-svelte';
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

  let appDef = $derived(appRegistry.getApp(win.appId));
  let appIcon = $derived(appDef?.icon ?? 'app');

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
  }

  function handleDragEnd() {
    isDragging = false;
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
    <!-- Title bar -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
      class="title-bar"
      onmousedown={handleTitleMousedown}
      ondblclick={handleTitleDblClick}
    >
      <div class="title-info">
        <span class="title-text">{win.title}</span>
      </div>
      <div class="window-controls">
        <button
          class="control-btn minimize"
          aria-label="Minimize"
          onclick={() => windowStore.minimize(win.id)}
        >
          <Minus size={10} strokeWidth={2.5} />
        </button>
        <button
          class="control-btn maximize"
          aria-label="Maximize"
          onclick={() => windowStore.maximize(win.id)}
        >
          <Square size={9} strokeWidth={2.5} />
        </button>
        <button class="control-btn close" aria-label="Close" onclick={handleClose}>
          <X size={11} strokeWidth={2.5} />
        </button>
      </div>
    </div>

    <!-- Window body -->
    <div class="window-body">
      {@render appSlot()}
    </div>

    <!-- Resize handles -->
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
    background: rgba(12, 12, 20, 0.92);
    border: 1px solid var(--glass-border);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.5),
      0 0 1px rgba(255, 255, 255, 0.1);
    display: flex;
    flex-direction: column;
    animation: windowIn 200ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    will-change: transform;
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
      0 0 24px rgba(139, 92, 246, 0.08);
  }

  .window.maximized {
    border-radius: 0;
    border: none;
  }

  .title-bar {
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    background: rgba(20, 20, 30, 0.9);
    border-bottom: 1px solid var(--border-subtle);
    cursor: grab;
    flex-shrink: 0;
  }

  .title-bar:active {
    cursor: grabbing;
  }

  .title-info {
    display: flex;
    align-items: center;
    gap: 8px;
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

  .window-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .control-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: var(--text-muted);
    background: var(--bg-surface);
    transition: all var(--transition-fast);
  }

  .control-btn:hover {
    color: var(--text-primary);
  }

  .control-btn.close:hover {
    background: rgba(239, 68, 68, 0.8);
    color: white;
  }

  .control-btn.minimize:hover {
    background: rgba(234, 179, 8, 0.6);
    color: white;
  }

  .control-btn.maximize:hover {
    background: rgba(34, 197, 94, 0.6);
    color: white;
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
