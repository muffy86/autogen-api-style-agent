<script lang="ts">
  import Wallpaper from './Wallpaper.svelte';
  import TopBar from './TopBar.svelte';
  import Dock from './Dock.svelte';
  import AppLauncher from './AppLauncher.svelte';
  import ContextMenu from './ContextMenu.svelte';
  import CommandPalette from './CommandPalette.svelte';
  import NotificationToast from './NotificationToast.svelte';
  import SnapZone from './SnapZone.svelte';
  import WindowManager from '$lib/components/window/WindowManager.svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';
  import { contextMenuStore } from '$lib/stores/contextmenu.svelte';
  import { commandPaletteStore } from '$lib/stores/commandpalette.svelte';
  import { notificationStore } from '$lib/stores/notifications.svelte';
  import {
    MessageSquare, Folder, Terminal, Settings, Search,
    RefreshCw, Monitor, Info, Layout, Moon, Sparkles
  } from 'lucide-svelte';
  import type { PaletteCommand } from '$lib/types';

  $effect(() => {
    const commands: PaletteCommand[] = [
      { id: 'open-chat', title: 'Open Chat', description: 'AI-powered conversations', icon: MessageSquare, category: 'app', action: () => windowStore.open('chat') },
      { id: 'open-files', title: 'Open Files', description: 'Browse and manage files', icon: Folder, category: 'app', action: () => windowStore.open('files') },
      { id: 'open-terminal', title: 'Open Terminal', description: 'Command line interface', icon: Terminal, category: 'app', action: () => windowStore.open('terminal') },
      { id: 'open-settings', title: 'Open Settings', description: 'System preferences', icon: Settings, category: 'app', action: () => windowStore.open('settings') },
      { id: 'open-search', title: 'Open Search', description: 'Spotlight search', icon: Search, category: 'app', action: () => windowStore.open('search') },
      { id: 'close-win', title: 'Close Window', description: 'Close the active window', category: 'action', shortcut: '⌘W', action: () => { const aw = windowStore.activeWindow; if (aw) windowStore.close(aw.id); } },
      { id: 'min-win', title: 'Minimize Window', description: 'Minimize the active window', category: 'action', action: () => { const aw = windowStore.activeWindow; if (aw) windowStore.minimize(aw.id); } },
      { id: 'max-win', title: 'Maximize Window', description: 'Maximize the active window', category: 'action', action: () => { const aw = windowStore.activeWindow; if (aw) windowStore.maximize(aw.id); } },
      { id: 'tile-left', title: 'Tile Left', description: 'Snap window to left half', icon: Layout, category: 'action', action: () => { const aw = windowStore.activeWindow; if (aw) { windowStore.snapPreview = { region: 'left', bounds: { x: 0, y: 36, width: window.innerWidth / 2, height: window.innerHeight - 116 } }; windowStore.applySnap(aw.id); } } },
      { id: 'tile-right', title: 'Tile Right', description: 'Snap window to right half', icon: Layout, category: 'action', action: () => { const aw = windowStore.activeWindow; if (aw) { windowStore.snapPreview = { region: 'right', bounds: { x: window.innerWidth / 2, y: 36, width: window.innerWidth / 2, height: window.innerHeight - 116 } }; windowStore.applySnap(aw.id); } } },
      { id: 'toggle-launcher', title: 'Toggle App Launcher', description: 'Show or hide the app grid', icon: Sparkles, category: 'action', action: () => desktopState.toggleLauncher() },
      { id: 'about', title: 'About Elysium', description: 'System information', icon: Info, category: 'setting', action: () => notificationStore.push({ type: 'info', title: 'Elysium AI OS', message: 'Version 1.0 — A futuristic desktop experience' }) }
    ];
    commandPaletteStore.register(commands);
  });

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
    contextMenuStore.open(e.clientX, e.clientY, [
      { id: 'new-win', label: 'New Window', icon: MessageSquare, action: () => windowStore.open('chat') },
      { id: 'sep1', label: '', separator: true, action: () => {} },
      { id: 'refresh', label: 'Refresh Desktop', icon: RefreshCw, action: () => notificationStore.push({ type: 'success', title: 'Desktop Refreshed', duration: 2000 }) },
      { id: 'sep2', label: '', separator: true, action: () => {} },
      { id: 'display', label: 'Display Settings', icon: Monitor, action: () => windowStore.open('settings') },
      { id: 'about', label: 'About Elysium', icon: Info, action: () => notificationStore.push({ type: 'info', title: 'Elysium AI OS', message: 'Version 1.0 — A futuristic desktop experience' }) }
    ]);
  }

  $effect(() => {
    function handleKeydown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        commandPaletteStore.toggle();
      }
    }
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });

  let welcomeShown = false;
  $effect(() => {
    if (welcomeShown) return;
    welcomeShown = true;
    setTimeout(() => {
      notificationStore.push({
        type: 'info',
        title: 'Welcome to Elysium',
        message: 'Press ⌘K to open the command palette',
        duration: 6000
      });
    }, 500);
  });
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="desktop" onclick={handleDesktopClick} oncontextmenu={handleDesktopContextMenu}>
  <Wallpaper />
  <div class="desktop-area"></div>
  <SnapZone />
  <WindowManager />
  <TopBar />
  <Dock />
  <AppLauncher />
  <ContextMenu />
  <CommandPalette />
  <NotificationToast />
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
</style>
