<script lang="ts">
  import { notificationStore } from '$lib/stores/notifications.svelte';
  import { X, Info, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-svelte';

  const typeIcons = { info: Info, success: CheckCircle, warning: AlertTriangle, error: AlertCircle };
  const typeBorderColors: Record<string, string> = {
    info: 'var(--accent)',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
  };
</script>

{#if notificationStore.notifications.length > 0}
  <div class="notification-center">
    {#each notificationStore.notifications as notif (notif.id)}
      {@const IconComp = typeIcons[notif.type]}
      <div
        class="notification-card glass"
        style="border-left: 3px solid {typeBorderColors[notif.type]}"
      >
        <div class="notif-icon" style="color: {typeBorderColors[notif.type]}">
          <IconComp size={16} strokeWidth={2} />
        </div>
        <div class="notif-content">
          <span class="notif-title">{notif.title}</span>
          <span class="notif-message">{notif.message}</span>
        </div>
        <button class="notif-dismiss" onclick={() => notificationStore.dismiss(notif.id)}>
          <X size={14} strokeWidth={2} />
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .notification-center {
    position: fixed;
    top: 44px;
    right: 12px;
    z-index: 8200;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: 340px;
    pointer-events: none;
  }

  .notification-card {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    border-radius: var(--radius-md);
    pointer-events: auto;
    animation: slideInRight 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    min-width: 280px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }

  .notif-icon {
    flex-shrink: 0;
    margin-top: 1px;
  }

  .notif-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .notif-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .notif-message {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .notif-dismiss {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
  }

  .notif-dismiss:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }
</style>
