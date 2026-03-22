<script lang="ts">
  import { notificationStore } from '$lib/stores/notifications.svelte';
  import { X, Info, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-svelte';

  const typeConfig: Record<string, { color: string; icon: any }> = {
    info: { color: '#3b82f6', icon: Info },
    success: { color: '#22c55e', icon: CheckCircle },
    warning: { color: '#f59e0b', icon: AlertTriangle },
    error: { color: '#ef4444', icon: AlertCircle }
  };
</script>

<div class="notif-stack">
  {#each notificationStore.notifications as notif (notif.id)}
    {@const cfg = typeConfig[notif.type] ?? typeConfig.info}
    {@const Icon = notif.icon ?? cfg.icon}
    <div
      class="notif-toast"
      style="border-left-color: {cfg.color};"
    >
      <div class="notif-content">
        <span class="notif-icon" style="color: {cfg.color};">
          <Icon size={18} strokeWidth={2} />
        </span>
        <div class="notif-text">
          <div class="notif-title">{notif.title}</div>
          {#if notif.message}
            <div class="notif-message">{notif.message}</div>
          {/if}
          {#if notif.action}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <span
              class="notif-action"
              onclick={() => { notif.action?.onClick(); notificationStore.dismiss(notif.id); }}
            >{notif.action.label}</span>
          {/if}
        </div>
        <button
          class="notif-close"
          aria-label="Dismiss"
          onclick={() => notificationStore.dismiss(notif.id)}
        >
          <X size={14} strokeWidth={2} />
        </button>
      </div>
      {#if notif.duration && notif.duration > 0}
        <div class="notif-progress">
          <div
            class="notif-progress-bar"
            style="background: {cfg.color}; animation-duration: {notif.duration}ms;"
          ></div>
        </div>
      {/if}
    </div>
  {/each}
</div>

<style>
  .notif-stack {
    position: fixed;
    top: 48px;
    right: 16px;
    z-index: 9900;
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 340px;
    pointer-events: none;
  }

  .notif-toast {
    pointer-events: auto;
    background: rgba(16, 16, 28, 0.94);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    animation: notifIn 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  .notif-content {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 12px 10px;
  }

  .notif-icon {
    flex-shrink: 0;
    margin-top: 1px;
  }

  .notif-text {
    flex: 1;
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
    margin-top: 2px;
    line-height: 1.4;
  }

  .notif-action {
    display: inline-block;
    margin-top: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-glow);
    cursor: pointer;
    transition: color 100ms ease;
  }

  .notif-action:hover {
    color: var(--accent);
  }

  .notif-close {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    transition: all 100ms ease;
  }

  .notif-close:hover {
    background: rgba(255, 255, 255, 0.06);
    color: var(--text-primary);
  }

  .notif-progress {
    height: 2px;
    background: rgba(255, 255, 255, 0.04);
  }

  .notif-progress-bar {
    height: 100%;
    animation: progressShrink linear forwards;
  }
</style>
