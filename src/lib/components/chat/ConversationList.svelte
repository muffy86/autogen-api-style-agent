<script lang="ts">
  import { chatStore, AVAILABLE_MODELS } from '$lib/stores/chat.svelte';
  import { Plus, Trash2, Search, Pin, PinOff, Pencil, Check, X, MessageSquare } from 'lucide-svelte';

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

  function getTimeGroup(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = diff / (1000 * 60 * 60);
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const startOfYesterday = startOfToday - 86400000;

    if (date.getTime() >= startOfToday) return 'Today';
    if (date.getTime() >= startOfYesterday) return 'Yesterday';
    if (hours < 168) return 'This Week';
    if (hours < 720) return 'This Month';
    return 'Older';
  }

  let hoveredId = $state<string | null>(null);
  let searchQuery = $state('');
  let editingId = $state<string | null>(null);
  let editingTitle = $state('');

  let filteredConversations = $derived.by(() => {
    let list = chatStore.conversations;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        c =>
          c.title.toLowerCase().includes(q) ||
          c.messages.some(m => m.content.toLowerCase().includes(q))
      );
    }
    return list;
  });

  let pinnedConversations = $derived(
    filteredConversations.filter(c => c.pinned)
  );

  let unpinnedConversations = $derived(
    filteredConversations.filter(c => !c.pinned)
  );

  let groupedConversations = $derived.by(() => {
    const groups: { label: string; items: typeof chatStore.conversations }[] = [];
    const order = ['Today', 'Yesterday', 'This Week', 'This Month', 'Older'];
    const grouped: Record<string, typeof chatStore.conversations> = {};

    for (const conv of unpinnedConversations) {
      const group = getTimeGroup(conv.updatedAt);
      if (!grouped[group]) grouped[group] = [];
      grouped[group].push(conv);
    }

    for (const label of order) {
      if (grouped[label]?.length) {
        groups.push({ label, items: grouped[label] });
      }
    }

    return groups;
  });

  function getModelColor(conv: typeof chatStore.conversations[0]): string {
    const m = AVAILABLE_MODELS.find(m => m.id === conv.model);
    return m?.color ?? '#71717a';
  }

  function startRename(conv: typeof chatStore.conversations[0]) {
    editingId = conv.id;
    editingTitle = conv.title;
  }

  function saveRename() {
    if (editingId && editingTitle.trim()) {
      chatStore.updateConversationTitle(editingId, editingTitle.trim());
    }
    editingId = null;
  }

  function cancelRename() {
    editingId = null;
  }

  function togglePin(conv: typeof chatStore.conversations[0]) {
    if (chatStore.activeConversation) {
      const c = chatStore.conversations.find(c => c.id === conv.id);
      if (c) {
        (c as any).pinned = !(c as any).pinned;
        chatStore.save();
      }
    }
  }

  function handleConvKeydown(e: KeyboardEvent) {
    if (editingId) {
      if (e.key === 'Enter') saveRename();
      if (e.key === 'Escape') cancelRename();
    }
  }
</script>

<div class="conversation-list">
  <button class="new-chat-btn" onclick={() => chatStore.createConversation()}>
    <Plus size={14} strokeWidth={2} />
    <span>New Chat</span>
  </button>

  <div class="search-bar">
    <Search size={13} />
    <input
      class="search-input"
      type="text"
      placeholder="Search conversations..."
      bind:value={searchQuery}
    />
    {#if searchQuery}
      <button class="search-clear" onclick={() => (searchQuery = '')}>
        <X size={12} />
      </button>
    {/if}
  </div>

  <div class="list scrollbar-thin">
    {#if filteredConversations.length === 0}
      <div class="empty-state">
        {#if searchQuery}
          No matching conversations
        {:else}
          No conversations yet
        {/if}
      </div>
    {:else}
      {#if pinnedConversations.length > 0}
        <div class="group-label">
          <Pin size={10} />
          <span>Pinned</span>
        </div>
        {#each pinnedConversations as conv (conv.id)}
          {@render conversationItem(conv)}
        {/each}
      {/if}

      {#each groupedConversations as group}
        <div class="group-label">
          <span>{group.label}</span>
        </div>
        {#each group.items as conv (conv.id)}
          {@render conversationItem(conv)}
        {/each}
      {/each}
    {/if}
  </div>
</div>

{#snippet conversationItem(conv: typeof chatStore.conversations[0])}
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
      ondblclick={() => startRename(conv)}
    >
      <div class="conv-title-row">
        <span class="conv-model-dot" style="background: {getModelColor(conv)}"></span>
        {#if editingId === conv.id}
          <!-- svelte-ignore a11y_autofocus -->
          <input
            class="conv-rename-input"
            bind:value={editingTitle}
            onblur={saveRename}
            onkeydown={handleConvKeydown}
            autofocus
            onclick={(e) => e.stopPropagation()}
          />
        {:else}
          <span class="conv-title">{conv.title}</span>
        {/if}
      </div>
      <div class="conv-meta">
        <span class="conv-preview">{getPreview(conv)}</span>
        <div class="conv-meta-right">
          <span class="conv-msg-count">{conv.messages.length}</span>
          <span class="conv-time">{formatTime(conv.updatedAt)}</span>
        </div>
      </div>
    </button>
    {#if hoveredId === conv.id && editingId !== conv.id}
      <div class="conv-actions">
        <button
          class="conv-action-btn"
          onclick={(e) => { e.stopPropagation(); togglePin(conv); }}
          aria-label={conv.pinned ? 'Unpin' : 'Pin'}
        >
          {#if conv.pinned}
            <PinOff size={11} />
          {:else}
            <Pin size={11} />
          {/if}
        </button>
        <button
          class="conv-action-btn"
          onclick={(e) => { e.stopPropagation(); startRename(conv); }}
          aria-label="Rename"
        >
          <Pencil size={11} />
        </button>
        <button
          class="conv-action-btn danger"
          onclick={(e) => { e.stopPropagation(); chatStore.deleteConversation(conv.id); }}
          aria-label="Delete conversation"
        >
          <Trash2 size={11} />
        </button>
      </div>
    {/if}
  </div>
{/snippet}

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

  .search-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 4px 8px;
    padding: 5px 8px;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    background: var(--bg-surface);
    color: var(--text-muted);
    transition: border-color var(--transition-fast);
  }

  .search-bar:focus-within {
    border-color: var(--accent);
  }

  .search-input {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 12px;
    font-family: inherit;
    outline: none;
  }

  .search-input::placeholder {
    color: var(--text-muted);
  }

  .search-clear {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border: none;
    background: var(--bg-surface-hover);
    color: var(--text-muted);
    border-radius: 50%;
    cursor: pointer;
    padding: 0;
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

  .group-label {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px 3px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
    padding: 8px 12px;
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

  .conv-title-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 2px;
  }

  .conv-model-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .conv-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
  }

  .conv-rename-input {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    background: var(--bg-surface);
    border: 1px solid var(--accent);
    border-radius: 4px;
    padding: 1px 6px;
    font-family: inherit;
    outline: none;
    flex: 1;
    min-width: 0;
  }

  .conv-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-left: 12px;
  }

  .conv-preview {
    font-size: 11px;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 120px;
  }

  .conv-meta-right {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }

  .conv-msg-count {
    font-size: 9px;
    color: var(--text-muted);
    background: var(--bg-surface-hover);
    padding: 0 5px;
    border-radius: 8px;
    line-height: 16px;
  }

  .conv-time {
    font-size: 10px;
    color: var(--text-muted);
  }

  .conv-actions {
    position: absolute;
    top: 6px;
    right: 6px;
    display: flex;
    gap: 2px;
    animation: fadeIn 100ms ease-out;
  }

  .conv-action-btn {
    width: 22px;
    height: 22px;
    border: none;
    background: var(--bg-surface-hover);
    color: var(--text-muted);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
  }

  .conv-action-btn:hover {
    background: var(--bg-surface-active);
    color: var(--text-primary);
  }

  .conv-action-btn.danger:hover {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
</style>
