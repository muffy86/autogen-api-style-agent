<script lang="ts">
  import { windowStore } from '$lib/stores/windows.svelte';
  import Window from './Window.svelte';
  import ChatApp from '$lib/components/apps/ChatApp.svelte';
  import FilesApp from '$lib/components/apps/FilesApp.svelte';
  import TerminalApp from '$lib/components/apps/TerminalApp.svelte';
  import SettingsApp from '$lib/components/apps/SettingsApp.svelte';
  import SearchApp from '$lib/components/apps/SearchApp.svelte';
  import DashboardApp from '$lib/components/apps/DashboardApp.svelte';
  import KnowledgeApp from '$lib/components/apps/KnowledgeApp.svelte';
  import type { Component } from 'svelte';

  const appComponents: Record<string, any> = {
    chat: ChatApp,
    files: FilesApp,
    terminal: TerminalApp,
    settings: SettingsApp,
    search: SearchApp,
    dashboard: DashboardApp,
    knowledge: KnowledgeApp
  };

  function getComponent(appId: string): any {
    return appComponents[appId] ?? ChatApp;
  }
</script>

<div class="window-manager">
  {#each windowStore.windows as win (win.id)}
    <Window {win} appComponent={getComponent(win.appId)} />
  {/each}
</div>

<style>
  .window-manager {
    position: fixed;
    inset: 0;
    z-index: 100;
    pointer-events: none;
  }

  .window-manager :global(> *) {
    pointer-events: auto;
  }
</style>
