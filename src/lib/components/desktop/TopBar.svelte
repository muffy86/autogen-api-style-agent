<script lang="ts">
  import { Wifi, Volume2, Battery, Sparkles, Bell, LogOut } from 'lucide-svelte';
  import { contextMenuStore } from '$lib/stores/contextmenu.svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';
  import { commandPaletteStore } from '$lib/stores/commandpalette.svelte';
  import { notificationStore } from '$lib/stores/notifications.svelte';
  import { createSupabaseBrowserClient } from '$lib/supabase/client';
  import { goto } from '$app/navigation';

  const supabase = createSupabaseBrowserClient();

  let hours = $state('');
  let minutes = $state('');
  let dayStr = $state('');
  let activeMenu = $state<string | null>(null);

  function updateTime() {
    const now = new Date();
    hours = now.getHours().toString().padStart(2, '0');
    minutes = now.getMinutes().toString().padStart(2, '0');
    dayStr = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  }

  $effect(() => {
    updateTime();
    const interval = setInterval(updateTime, 10000);
    return () => clearInterval(interval);
  });

  function openMenuBelow(el: HTMLElement, menuId: string, items: any[]) {
    const rect = el.getBoundingClientRect();
    activeMenu = menuId;
    contextMenuStore.open(rect.left, rect.bottom + 4, items);
    const unsub = $effect.root(() => {
      $effect(() => {
        if (!contextMenuStore.visible) {
          activeMenu = null;
          unsub();
        }
      });
    });
  }

  function handleMenuClick(e: MouseEvent, menuId: string) {
    const el = e.currentTarget as HTMLElement;
    if (activeMenu === menuId && contextMenuStore.visible) {
      contextMenuStore.close();
      activeMenu = null;
      return;
    }
    const items = getMenuItems(menuId);
    openMenuBelow(el, menuId, items);
  }

  function handleMenuEnter(e: MouseEvent, menuId: string) {
    if (activeMenu && activeMenu !== menuId && contextMenuStore.visible) {
      const el = e.currentTarget as HTMLElement;
      contextMenuStore.close();
      setTimeout(() => {
        const items = getMenuItems(menuId);
        openMenuBelow(el, menuId, items);
      }, 10);
    }
  }

  function getMenuItems(menuId: string): any[] {
    const aw = windowStore.activeWindow;
    switch (menuId) {
      case 'file':
        return [
          { id: 'new-win', label: 'New Window', shortcut: '⌘N', action: () => windowStore.open('chat') },
          { id: 'new-chat', label: 'New Chat', action: () => windowStore.open('chat') },
          { id: 'sep1', label: '', separator: true, action: () => {} },
          { id: 'close', label: 'Close Window', shortcut: '⌘W', disabled: !aw, action: () => aw && windowStore.close(aw.id) },
          { id: 'sep2', label: '', separator: true, action: () => {} },
          { id: 'quit', label: 'Quit Elysium', shortcut: '⌘Q', danger: true, action: () => windowStore.closeAll() }
        ];
      case 'edit':
        return [
          { id: 'undo', label: 'Undo', shortcut: '⌘Z', disabled: true, action: () => {} },
          { id: 'redo', label: 'Redo', shortcut: '⇧⌘Z', disabled: true, action: () => {} },
          { id: 'sep1', label: '', separator: true, action: () => {} },
          { id: 'cut', label: 'Cut', shortcut: '⌘X', disabled: true, action: () => {} },
          { id: 'copy', label: 'Copy', shortcut: '⌘C', disabled: true, action: () => {} },
          { id: 'paste', label: 'Paste', shortcut: '⌘V', disabled: true, action: () => {} },
          { id: 'sep2', label: '', separator: true, action: () => {} },
          { id: 'selall', label: 'Select All', shortcut: '⌘A', disabled: true, action: () => {} }
        ];
      case 'view':
        return [
          { id: 'launcher', label: 'Toggle App Launcher', action: () => desktopState.toggleLauncher() },
          { id: 'sep1', label: '', separator: true, action: () => {} },
          { id: 'zoom-in', label: 'Zoom In', shortcut: '⌘+', disabled: true, action: () => {} },
          { id: 'zoom-out', label: 'Zoom Out', shortcut: '⌘-', disabled: true, action: () => {} },
          { id: 'sep2', label: '', separator: true, action: () => {} },
          { id: 'fullscreen', label: 'Full Screen', shortcut: '⌃⌘F', disabled: true, action: () => {} }
        ];
      case 'window':
        return [
          { id: 'min', label: 'Minimize', shortcut: '⌘M', disabled: !aw, action: () => aw && windowStore.minimize(aw.id) },
          { id: 'max', label: 'Maximize', disabled: !aw, action: () => aw && windowStore.maximize(aw.id) },
          { id: 'sep1', label: '', separator: true, action: () => {} },
          { id: 'tile-l', label: 'Tile Left', disabled: !aw, action: () => { if (aw) windowStore.snap(aw.id, 'left'); } },
          { id: 'tile-r', label: 'Tile Right', disabled: !aw, action: () => { if (aw) windowStore.snap(aw.id, 'right'); } },
          { id: 'sep2', label: '', separator: true, action: () => {} },
          { id: 'close-all', label: 'Close All', danger: true, action: () => windowStore.closeAll() }
        ];
      case 'help':
        return [
          { id: 'about', label: 'About Elysium', action: () => notificationStore.push({ type: 'info', title: 'Elysium AI OS', message: 'Version 1.0 — A futuristic desktop experience' }) },
          { id: 'shortcuts', label: 'Keyboard Shortcuts', shortcut: '⌘K', action: () => commandPaletteStore.open() },
          { id: 'sep1', label: '', separator: true, action: () => {} },
          { id: 'issue', label: 'Report Issue', action: () => notificationStore.push({ type: 'info', title: 'Feedback', message: 'Thank you for using Elysium!' }) }
        ];
      default:
        return [];
    }
  }

  let notifCount = $derived(notificationStore.notifications.length);

  async function handleLogout() {
    await supabase.auth.signOut();
    goto('/login');
  }
</script>

<div class="topbar glass">
  <div class="topbar-left">
    <button class="topbar-brand" aria-label="Elysium">
      <Sparkles size={14} strokeWidth={2} />
      <span class="brand-text">Elysium</span>
    </button>
    <div class="topbar-menus">
      {#each ['file', 'edit', 'view', 'window', 'help'] as menu}
        <button
          class="menu-item"
          class:menu-active={activeMenu === menu}
          onclick={(e) => handleMenuClick(e, menu)}
          onmouseenter={(e) => handleMenuEnter(e, menu)}
        >
          {menu.charAt(0).toUpperCase() + menu.slice(1)}
        </button>
      {/each}
    </div>
  </div>
  <div class="topbar-right">
    <div class="status-icons">
      <button class="status-btn" aria-label="Notifications">
        <Bell size={14} />
        {#if notifCount > 0}
          <span class="notif-badge">{notifCount}</span>
        {/if}
      </button>
      <Wifi size={14} />
      <Volume2 size={14} />
      <Battery size={14} />
    </div>
    <button class="logout-btn" onclick={handleLogout} aria-label="Sign out">
      <LogOut size={13} strokeWidth={2} />
    </button>
    <div class="clock">
      <span class="clock-date">{dayStr}</span>
      <span class="clock-time">{hours}:{minutes}</span>
    </div>
  </div>
</div>

<style>
  .topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 36px;
    z-index: 9000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    font-size: 13px;
    border-top: none;
    border-left: none;
    border-right: none;
  }

  .topbar-left {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .topbar-brand {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--accent-glow);
    cursor: pointer;
    font-weight: 600;
    font-size: 13px;
    transition: background var(--transition-fast);
  }

  .topbar-brand:hover {
    background: var(--bg-surface-hover);
  }

  .brand-text {
    background: linear-gradient(135deg, var(--accent-glow), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .topbar-menus {
    display: flex;
    align-items: center;
  }

  .menu-item {
    padding: 4px 10px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    transition: all var(--transition-fast);
  }

  .menu-item:hover,
  .menu-item.menu-active {
    background: var(--bg-surface-active);
    color: var(--text-primary);
  }

  .menu-item:disabled {
    opacity: 0.4;
    cursor: default;
  }

  .topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .status-icons {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--text-secondary);
  }

  .status-btn {
    position: relative;
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: color var(--transition-fast);
  }

  .status-btn:hover {
    color: var(--text-primary);
  }

  .notif-badge {
    position: absolute;
    top: -4px;
    right: -6px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--accent);
    color: white;
    font-size: 9px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }

  .logout-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    transition: all var(--transition-fast);
  }

  .logout-btn:hover {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
  }

  .clock {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 13px;
  }

  .clock-time {
    font-variant-numeric: tabular-nums;
    color: var(--text-primary);
    font-weight: 500;
  }
</style>
