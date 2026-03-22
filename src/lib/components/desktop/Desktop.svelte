<script lang="ts">
  import Wallpaper from './Wallpaper.svelte';
  import TopBar from './TopBar.svelte';
  import Dock from './Dock.svelte';
  import AppLauncher from './AppLauncher.svelte';
  import WindowManager from '$lib/components/window/WindowManager.svelte';
  import { windowStore } from '$lib/stores/windows.svelte';
  import { desktopState } from '$lib/stores/desktop.svelte';

  function handleDesktopClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (target.classList.contains('desktop-area')) {
      windowStore.unfocusAll();
      desktopState.closeLauncher();
    }
  }
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="desktop" onclick={handleDesktopClick}>
  <Wallpaper />
  <div class="desktop-area"></div>
  <WindowManager />
  <TopBar />
  <Dock />
  <AppLauncher />
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
