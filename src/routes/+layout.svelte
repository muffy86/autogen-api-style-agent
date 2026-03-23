<script lang="ts">
  import '../app.css';
  import { themeStore } from '$lib/stores/theme.svelte';

  let { children } = $props();

  $effect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', themeStore.resolved);
    }
  });

  $effect(() => {
    themeStore.initAccent();
  });
</script>

<svelte:head>
  <title>Elysium AI OS</title>
  <meta name="description" content="Elysium AI OS — Next-generation AI operating system" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
</svelte:head>

<div class="app-root">
  {@render children()}
</div>

<style>
  .app-root {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  @media (max-width: 767px) {
    .app-root {
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-base);
    }
  }
</style>
