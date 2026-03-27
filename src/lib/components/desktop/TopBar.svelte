<script lang="ts">
  import { Wifi, Volume2, Battery, Sparkles, LogOut } from 'lucide-svelte';
  import { createSupabaseBrowserClient } from '$lib/supabase/client';
  import { goto } from '$app/navigation';

  const supabase = createSupabaseBrowserClient();

  let hours = $state('');
  let minutes = $state('');
  let dayStr = $state('');

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
      <button class="menu-item">File</button>
      <button class="menu-item">Edit</button>
      <button class="menu-item">View</button>
      <button class="menu-item">Window</button>
      <button class="menu-item">Help</button>
    </div>
  </div>
  <div class="topbar-right">
    <div class="status-icons">
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

  .menu-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
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
