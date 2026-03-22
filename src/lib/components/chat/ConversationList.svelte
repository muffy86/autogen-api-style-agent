<script lang="ts">
  import { chatStore } from '$lib/stores/chat.svelte';
  import { Plus, Trash2 } from 'lucide-svelte';

  function formatTime(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  function getPreview(conv: typeof chatStore.conversations[0]): string {
    const last = [...conv.messages].reverse().find(m => m.role === 'assistant' || m.role === 'user');
    if (!last) return 'No messages yet';
    return last.content.slice(0, 60) + (last.content.length > 60 ? '...' : '');
  }

  let hoveredId = $state<string | null>(null);
</script>

<div class="conversation-list">
  <button class="new-chat-btn" onclick={() => chatStore.createConversation()}>
    <Plus size={14} strokeWidth={2} />
    <span>New Chat</span>
  </button>

  <div class="list scrollbar-thin">
    {#if chatStore.conversations.length === 0}
      <div class="empty-state">No conversations yet</div>
    {:else}
      {#each chatStore.conversations as conv (conv.id)}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="conv-wrapper"
          onmouseenter={() => (hoveredId = conv.id)}
          onmouseleave={() => (hoveredId = null)}
        >
          <button
            class="conv-item"
            class:active={conv.id === chatStore.activeConversationId}
            onclick={() => chatStore.setActive(conv.id)}
          >
            <div class="conv-title">{conv.title}</div>
            <div class="conv-meta">
              <span class="conv-preview">{getPreview(conv)}</span>
              <span class="conv-time">{formatTime(conv.updatedAt)}</span>
            </div>
          </button>
          {#if hoveredId === conv.id}
            <button
              class="delete-btn"
              onclick={() => chatStore.deleteConversation(conv.id)}
              aria-label="Delete conversation"
            >
              <Trash2 size={12} />
            </button>
          {/if}
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .conversation-list {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .new-chat-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin: 8px 8px 4px;
    padding: 8px 12px;
    border: none;
    background: var(--accent);
    color: white;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    transition: all var(--transition-fast);
  }

  .new-chat-btn:hover {
    background: var(--accent-glow);
    box-shadow: 0 0 12px rgba(139, 92, 246, 0.3);
  }

  .list {
    flex: 1;
    overflow-y: auto;
    padding: 4px;
  }

  .empty-state {
    padding: 24px 16px;
    text-align: center;
    font-size: 12px;
    color: var(--text-muted);
  }

  .conv-wrapper {
    position: relative;
  }

  .conv-item {
    position: relative;
    display: block;
    width: 100%;
    text-align: left;
    padding: 10px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-family: inherit;
    transition: background var(--transition-fast);
  }

  .conv-item:hover {
    background: var(--bg-surface-hover);
  }

  .conv-item.active {
    background: var(--accent-subtle);
  }

  .conv-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 20px;
  }

  .conv-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .conv-preview {
    font-size: 11px;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 140px;
  }

  .conv-time {
    font-size: 10px;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .delete-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 22px;
    height: 22px;
    border: none;
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
  }

  .delete-btn:hover {
    background: rgba(239, 68, 68, 0.3);
  }
</style>
