<script lang="ts">
  import { windowStore } from '$lib/stores/windows.svelte';

  let snap = $derived(windowStore.snapPreview);
</script>

{#if snap}
  <div
    class="snap-zone"
    style="
      left: {snap.x}px;
      top: {snap.y}px;
      width: {snap.w}px;
      height: {snap.h}px;
    "
  ></div>
{/if}

<style>
  .snap-zone {
    position: fixed;
    z-index: 7500;
    background: rgba(139, 92, 246, 0.08);
    border: 2px dashed rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    pointer-events: none;
    animation: snapFadeIn 150ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
</style>
