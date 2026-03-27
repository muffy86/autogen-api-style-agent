<script lang="ts">
  import { Monitor, Palette, Shield, Info, Cpu, Key } from 'lucide-svelte';
  import { themeStore } from '$lib/stores/theme.svelte';
  import { notificationStore } from '$lib/stores/notifications.svelte';

  let selectedSection = $state('appearance');

  const sections = [
    { id: 'general', name: 'General', icon: Monitor },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'models', name: 'AI Models', icon: Cpu },
    { id: 'apikeys', name: 'API Keys', icon: Key },
    { id: 'privacy', name: 'Privacy', icon: Shield },
    { id: 'about', name: 'About', icon: Info }
  ];

  let selectedTheme = $derived(themeStore.theme);
  let selectedAccent = $derived(themeStore.accentColor);

  const accentColors = [
    { name: 'Violet', value: '#8b5cf6' },
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Emerald', value: '#10b981' },
    { name: 'Rose', value: '#f43f5e' },
    { name: 'Amber', value: '#f59e0b' }
  ];

  const wallpapers = [
    { name: 'Nebula', color: 'linear-gradient(135deg, #1a0533, #0a0a1a)' },
    { name: 'Ocean', color: 'linear-gradient(135deg, #0a1628, #0a0a1a)' },
    { name: 'Aurora', color: 'linear-gradient(135deg, #0a1a0f, #0a0a1a)' },
    { name: 'Sunset', color: 'linear-gradient(135deg, #1a0f0a, #0a0a1a)' }
  ];

  function handleThemeChange(theme: string) {
    themeStore.setTheme(theme as 'dark' | 'light' | 'system');
    notificationStore.add('Theme Changed', `Switched to ${theme} theme`, 'success', 3000);
  }

  function handleAccentChange(value: string) {
    themeStore.setAccent(value);
  }
</script>

<div class="settings-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Settings</span>
    </div>
    <div class="nav-list">
      {#each sections as section}
        <button
          class="nav-item"
          class:active={selectedSection === section.id}
          onclick={() => (selectedSection = section.id)}
        >
          <section.icon size={15} strokeWidth={1.5} />
          <span>{section.name}</span>
        </button>
      {/each}
    </div>
  </div>
  <div class="main scrollbar-thin">
    {#if selectedSection === 'appearance'}
      <div class="section">
        <h3 class="section-title">Appearance</h3>
        <p class="section-desc">Customize the look and feel of Elysium</p>

        <div class="setting-group">
          <span class="setting-label">Theme</span>
          <div class="theme-options">
            {#each ['dark', 'light', 'system'] as theme}
              <button
                class="theme-btn"
                class:active={selectedTheme === theme}
                onclick={() => handleThemeChange(theme)}
              >
                {theme.charAt(0).toUpperCase() + theme.slice(1)}
              </button>
            {/each}
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Accent Color</span>
          <div class="color-options">
            {#each accentColors as color}
              <button
                class="color-swatch"
                class:active={selectedAccent === color.value}
                style="background: {color.value}"
                onclick={() => handleAccentChange(color.value)}
                aria-label={color.name}
              >
                {#if selectedAccent === color.value}
                  <svg viewBox="0 0 16 16" fill="none" class="check">
                    <path d="M3 8l4 4 6-7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                {/if}
              </button>
            {/each}
          </div>
        </div>

        <div class="setting-group">
          <span class="setting-label">Wallpaper</span>
          <div class="wallpaper-grid">
            {#each wallpapers as wp}
              <button class="wallpaper-thumb" style="background: {wp.color}">
                <span class="wp-name">{wp.name}</span>
              </button>
            {/each}
          </div>
        </div>
      </div>
    {:else if selectedSection === 'about'}
      <div class="section">
        <h3 class="section-title">About Elysium</h3>
        <div class="about-card">
          <div class="about-logo">✦</div>
          <h4>Elysium AI OS</h4>
          <p class="version">Version 0.1.0-alpha</p>
          <p class="about-desc">A next-generation AI-powered operating system interface. Built with SvelteKit, designed for the future.</p>
        </div>
      </div>
    {:else}
      <div class="section">
        <h3 class="section-title">{sections.find((s) => s.id === selectedSection)?.name}</h3>
        <p class="section-desc">This section is coming soon.</p>
        <div class="placeholder-content">
          <div class="placeholder-row"></div>
          <div class="placeholder-row short"></div>
          <div class="placeholder-row"></div>
          <div class="placeholder-row shorter"></div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .settings-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 200px;
    border-right: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .nav-list {
    padding: 4px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    text-align: left;
  }

  .nav-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .nav-item.active {
    background: var(--accent-subtle);
    color: var(--accent-glow);
  }

  .main {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .section-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 24px;
  }

  .setting-group {
    margin-bottom: 24px;
  }

  .setting-label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 10px;
    font-style: normal;
  }

  .theme-options {
    display: flex;
    gap: 8px;
  }

  .theme-btn {
    position: relative;
    padding: 10px 20px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    transition: all var(--transition-fast);
    font-family: inherit;
  }

  .theme-btn:hover {
    border-color: var(--border-default);
    color: var(--text-primary);
  }

  .theme-btn.active {
    border-color: var(--accent);
    color: var(--accent-glow);
    background: var(--accent-subtle);
  }

  .color-options {
    display: flex;
    gap: 10px;
  }

  .color-swatch {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .color-swatch:hover {
    transform: scale(1.1);
  }

  .color-swatch.active {
    border-color: white;
    box-shadow: 0 0 12px currentColor;
  }

  .check {
    width: 14px;
    height: 14px;
  }

  .wallpaper-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .wallpaper-thumb {
    aspect-ratio: 16/10;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    cursor: pointer;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 6px;
    transition: all var(--transition-fast);
  }

  .wallpaper-thumb:hover {
    border-color: var(--accent);
    transform: scale(1.02);
  }

  .wp-name {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.6);
  }

  .about-card {
    text-align: center;
    padding: 32px;
  }

  .about-logo {
    font-size: 48px;
    color: var(--accent-glow);
    margin-bottom: 12px;
  }

  .about-card h4 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .version {
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }

  .about-desc {
    font-size: 13px;
    color: var(--text-secondary);
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
  }

  .placeholder-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
  }

  .placeholder-row {
    height: 12px;
    background: var(--bg-surface);
    border-radius: 6px;
    width: 100%;
  }

  .placeholder-row.short {
    width: 75%;
  }

  .placeholder-row.shorter {
    width: 50%;
  }
</style>
