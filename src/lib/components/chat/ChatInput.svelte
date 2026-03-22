<script lang="ts">
  import { ArrowUp, Loader2 } from 'lucide-svelte';

  interface Props {
    value: string;
    isLoading: boolean;
    onsubmit: () => void;
    oninput: (val: string) => void;
  }

  let { value, isLoading, onsubmit, oninput }: Props = $props();

  let textareaEl: HTMLTextAreaElement | undefined = $state(undefined);

  function autoResize() {
    if (!textareaEl) return;
    textareaEl.style.height = 'auto';
    textareaEl.style.height = Math.min(textareaEl.scrollHeight, 200) + 'px';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onsubmit();
      }
    }
  }

  function handleInput(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    oninput(target.value);
    autoResize();
  }

  $effect(() => {
    if (!value && textareaEl) {
      textareaEl.style.height = 'auto';
    }
  });
</script>

<div class="chat-input-bar">
  {#if isLoading}
    <div class="streaming-indicator">
      <Loader2 size={12} class="spin" />
      <span>Streaming...</span>
    </div>
  {/if}
  <div class="input-row">
    <textarea
      bind:this={textareaEl}
      class="input-textarea"
      placeholder="Message Elysium..."
      rows={1}
      value={value}
      oninput={handleInput}
      onkeydown={handleKeydown}
      disabled={isLoading}
    ></textarea>
    <button
      class="send-btn"
      onclick={onsubmit}
      disabled={!value.trim() || isLoading}
      aria-label="Send message"
    >
      {#if isLoading}
        <Loader2 size={16} />
      {:else}
        <ArrowUp size={16} strokeWidth={2.5} />
      {/if}
    </button>
  </div>
</div>

<style>
  .chat-input-bar {
    padding: 8px 16px 12px;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .streaming-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 4px 2px;
    font-size: 11px;
    color: var(--accent-glow);
  }

  .streaming-indicator :global(.spin) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .input-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }

  .input-textarea {
    flex: 1;
    min-height: 36px;
    max-height: 200px;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    line-height: 1.5;
    resize: none;
    outline: none;
    transition: border-color var(--transition-fast);
  }

  .input-textarea::placeholder {
    color: var(--text-muted);
  }

  .input-textarea:focus {
    border-color: var(--accent);
  }

  .input-textarea:disabled {
    opacity: 0.5;
  }

  .send-btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    border: none;
    background: var(--accent);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .send-btn:hover:not(:disabled) {
    background: var(--accent-glow);
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
  }

  .send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
</style>
