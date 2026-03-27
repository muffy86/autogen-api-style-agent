<script lang="ts">
  import Desktop from '$lib/components/desktop/Desktop.svelte';
  import { createSupabaseBrowserClient } from '$lib/supabase/client';
  import { chatStore } from '$lib/stores/chat.svelte';

  const supabase = createSupabaseBrowserClient();

  let isMobile = $state(false);

  $effect(() => {
    chatStore.init(supabase);
  });

  $effect(() => {
    function checkWidth() {
      isMobile = window.innerWidth < 768;
    }
    checkWidth();
    window.addEventListener('resize', checkWidth);
    return () => window.removeEventListener('resize', checkWidth);
  });
</script>

{#if isMobile}
  <div class="mobile-notice">
    <div class="mobile-icon">✦</div>
    <h2>Elysium AI OS</h2>
    <p>Desktop experience requires a larger screen.</p>
    <p class="sub">Please use a device with at least 768px viewport width.</p>
  </div>
{:else}
  <Desktop />
{/if}

<style>
  .mobile-notice {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    padding: 32px;
    text-align: center;
    background: var(--bg-base);
    color: var(--text-primary);
  }

  .mobile-icon {
    font-size: 48px;
    color: var(--accent-glow);
    margin-bottom: 16px;
  }

  .mobile-notice h2 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 12px;
    background: linear-gradient(135deg, var(--accent-glow), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .mobile-notice p {
    font-size: 15px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .mobile-notice .sub {
    font-size: 13px;
    color: var(--text-muted);
  }
</style>
