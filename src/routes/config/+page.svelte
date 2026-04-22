<script lang="ts">
  import SettingsApp from '$lib/components/apps/SettingsApp.svelte';
</script>

<div class="config-page">
  <div class="config-header">
    <a href="/" class="back-link">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M10 12L6 8l4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      Back to Elysium
    </a>
    <span class="config-title">Settings</span>
  </div>
  <div class="config-body">
    <SettingsApp />
  </div>
</div>

<style>
  .config-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--bg-base);
    color: var(--text-primary);
  }

  .config-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 24px;
    border-bottom: 1px solid var(--border-subtle);
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    flex-shrink: 0;
  }

  .back-link {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 13px;
    transition: color 150ms;
  }

  .back-link:hover {
    color: var(--accent-glow);
  }

  .config-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .config-body {
    flex: 1;
    overflow: hidden;
  }
</style>
