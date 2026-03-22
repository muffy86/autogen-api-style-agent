<script lang="ts">
  import MarkdownRenderer from './MarkdownRenderer.svelte';
  import { AVAILABLE_MODELS } from '$lib/stores/chat.svelte';

  interface Props {
    role: 'user' | 'assistant' | 'system';
    content: string;
    model?: string;
    isStreaming?: boolean;
  }

  let { role, content, model, isStreaming = false }: Props = $props();

  let modelInfo = $derived(model ? AVAILABLE_MODELS.find(m => m.id === model) : null);
</script>

<div class="message" class:user={role === 'user'} class:assistant={role === 'assistant'}>
  {#if role === 'assistant' && modelInfo}
    <div class="model-badge">
      <span class="model-dot" style="background: {modelInfo.color}"></span>
      <span class="model-name">{modelInfo.name}</span>
    </div>
  {/if}
  <div class="message-bubble">
    {#if role === 'user'}
      <span class="user-text">{content}</span>
    {:else if content}
      <MarkdownRenderer {content} />
    {/if}
    {#if isStreaming && !content}
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    {/if}
  </div>
</div>

<style>
  .message {
    display: flex;
    flex-direction: column;
    max-width: 82%;
    animation: msgIn 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
  }

  @keyframes msgIn {
    from {
      opacity: 0;
      transform: translateY(6px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message.user {
    align-self: flex-end;
    align-items: flex-end;
  }

  .message.assistant {
    align-self: flex-start;
    align-items: flex-start;
  }

  .model-badge {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 4px;
    padding-left: 2px;
  }

  .model-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .model-name {
    font-size: 10px;
    color: var(--text-muted);
    font-weight: 500;
    letter-spacing: 0.02em;
  }

  .message-bubble {
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 13px;
    line-height: 1.5;
    min-width: 20px;
  }

  .message.user .message-bubble {
    background: var(--accent);
    color: white;
    border-bottom-right-radius: 4px;
  }

  .user-text {
    white-space: pre-wrap;
    word-break: break-word;
  }

  .message.assistant .message-bubble {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  .typing-dots {
    display: flex;
    gap: 4px;
    padding: 2px 0;
  }

  .typing-dots span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: dotPulse 1.4s ease-in-out infinite;
  }

  .typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes dotPulse {
    0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
    30% { opacity: 1; transform: scale(1); }
  }
</style>
