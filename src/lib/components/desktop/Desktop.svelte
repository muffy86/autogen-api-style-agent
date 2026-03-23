<script lang="ts">
  import Wallpaper from './Wallpaper.svelte';
  import TopBar from './TopBar.svelte';
  import Dock from './Dock.svelte';
  import AppLauncher from './AppLauncher.svelte';
  import WindowManager from '$lib/components/window/WindowManager.svelte';
  import NotificationCenter from './NotificationCenter.svelte';
  import CommandPalette from './CommandPalette.svelte';
  import ContextMenu from './ContextMenu.svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';
  import { chatStore } from '$lib/stores/chat.svelte';
  import { MessageSquare, Terminal, Settings, Image } from 'lucide-svelte';

  let showCommandPalette = $state(false);
  let contextMenu = $state<{ x: number; y: number; items: any[] } | null>(null);

  function handleDesktopClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (target.classList.contains('desktop-area')) {
      windowStore.unfocusAll();
      desktopState.closeLauncher();
    }
  }

  function handleDesktopContextMenu(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.classList.contains('desktop-area')) return;
    e.preventDefault();
    contextMenu = {
      x: e.clientX,
      y: e.clientY,
      items: [
        {
          label: 'New Chat',
          icon: MessageSquare,
          action: () => {
            chatStore.createConversation();
            windowStore.open('chat');
          },
        },
        {
          label: 'Open Terminal',
          icon: Terminal,
          action: () => windowStore.open('terminal'),
        },
        { separator: true },
        {
          label: 'Settings',
          icon: Settings,
          action: () => windowStore.open('settings'),
        },
      ],
    };
  }

  $effect(() => {
    function handleKeydown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        showCommandPalette = !showCommandPalette;
      }
    }
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="desktop" onclick={handleDesktopClick} oncontextmenu={handleDesktopContextMenu}>
  <Wallpaper />
  <div class="desktop-area"></div>
  <WindowManager />

  {#if windowStore.snapPreview}
    <div
      class="snap-preview"
      style="
        left: {windowStore.snapPreview.x}px;
        top: {windowStore.snapPreview.y}px;
        width: {windowStore.snapPreview.w}px;
        height: {windowStore.snapPreview.h}px;
      "
    ></div>
  {/if}

  <NotificationCenter />
  <TopBar />
  <Dock />
  <AppLauncher />

  <CommandPalette
    visible={showCommandPalette}
    onclose={() => (showCommandPalette = false)}
  />

  {#if contextMenu}
    <ContextMenu
      x={contextMenu.x}
      y={contextMenu.y}
      items={contextMenu.items}
      onclose={() => (contextMenu = null)}
    />
  {/if}
</div>

<style>
  .desktop {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    position: relative;
  }

  .desktop-area {
    position: fixed;
    inset: 0;
    z-index: 1;
  }

  .snap-preview {
    position: fixed;
    z-index: 99;
    background: var(--accent-subtle);
    border: 2px dashed var(--accent);
    border-radius: var(--radius-lg);
    animation: snapPreviewIn 150ms ease-out forwards;
    pointer-events: none;
  }
</style>
