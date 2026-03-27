<script lang="ts">
  import { chatStore } from '$lib/stores/chat.svelte';
  import { ChevronDown, ChevronRight } from 'lucide-svelte';

  let expanded = $state(false);
  let localPrompt = $state('');

  let currentPrompt = $derived(chatStore.activeConversation?.systemPrompt ?? '');

  $effect(() => {
    localPrompt = currentPrompt;
  });

  function save() {
    if (chatStore.activeConversation) {
      chatStore.updateSystemPrompt(chatStore.activeConversation.id, localPrompt);
    }
  }
</script>

<div class="system-prompt-editor">
  <button class="toggle-btn" onclick={() => (expanded = !expanded)}>
    {#if expanded}
      <ChevronDown size={12} />
    {:else}
      <ChevronRight size={12} />
    {/if}
    <span>System Prompt</span>
    {#if currentPrompt}
      <span class="has-prompt-dot"></span>
    {/if}
  </button>

  {#if expanded}
    <div class="editor-area">
      <textarea
        class="prompt-textarea scrollbar-thin"
        placeholder="You are Elysium, a helpful AI assistant..."
        bind:value={localPrompt}
        onblur={save}
        rows={3}
      ></textarea>
    </div>
  {/if}
</div>

<style>
  .system-prompt-editor {
    border-bottom: 1px solid var(--border-subtle);
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding: 6px 16px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 11px;
    font-family: inherit;
    transition: color var(--transition-fast);
  }

  .toggle-btn:hover {
    color: var(--text-secondary);
  }

  .has-prompt-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
  }

  .editor-area {
    padding: 0 12px 8px;
    animation: slideDown 150ms ease-out;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .prompt-textarea {
    width: 100%;
    min-height: 60px;
    max-height: 120px;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    font-size: 12px;
    font-family: inherit;
    line-height: 1.5;
    resize: vertical;
    outline: none;
    transition: border-color var(--transition-fast);
  }

  .prompt-textarea::placeholder {
    color: var(--text-muted);
  }

  .prompt-textarea:focus {
    border-color: var(--accent);
    color: var(--text-primary);
  }
</style>
