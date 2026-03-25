<script lang="ts">
  import { Wifi, Volume2, Battery, Sparkles } from 'lucide-svelte';

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
</script>

<div class="topbar glass">
  <div class="topbar-left">
    <button class="topbar-brand" aria-label="Elysium">
      <Sparkles size={14} strokeWidth={2} />
      <span class="brand-text">Elysium</span>
    </button>
    <div class="topbar-menus">
      <button class="menu-item" disabled title="Coming soon">File</button>
      <button class="menu-item" disabled title="Coming soon">Edit</button>
      <button class="menu-item" disabled title="Coming soon">View</button>
      <button class="menu-item" disabled title="Coming soon">Window</button>
      <button class="menu-item" disabled title="Coming soon">Help</button>
    </div>
  </div>
  <div class="topbar-right">
    <div class="status-icons">
      <Wifi size={14} />
      <Volume2 size={14} />
      <Battery size={14} />
    </div>
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

  .menu-item:hover:not(:disabled) {
    background: var(--bg-surface-hover);
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
