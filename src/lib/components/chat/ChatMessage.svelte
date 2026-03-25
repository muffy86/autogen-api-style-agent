<script lang="ts">
  import MarkdownRenderer from './MarkdownRenderer.svelte';
  import { AVAILABLE_MODELS } from '$lib/stores/chat.svelte';

  interface Props {
    role: 'user' | 'assistant' | 'system';
    content: string;
    parts?: Array<{ type: string; text?: string; toolInvocation?: any }>;
    model?: string;
    isStreaming?: boolean;
  }

  let { role, content, parts, model, isStreaming = false }: Props = $props();

  let modelInfo = $derived(model ? AVAILABLE_MODELS.find(m => m.id === model) : null);

  const toolIcons: Record<string, string> = {
    webSearch: '\u{1F50D}',
    calculator: '\u{1F9EE}',
    urlFetch: '\u{1F310}',
  };

  const toolLabels: Record<string, string> = {
    webSearch: 'Web Search',
    calculator: 'Calculator',
    urlFetch: 'URL Fetch',
  };

  function formatToolResult(result: any): string {
    if (!result) return '';
    if (typeof result === 'string') return result;
    if (result.error) return `Error: ${result.error}`;
    if (result.result !== undefined) return `= ${result.result}`;
    if (result.content) return result.content.slice(0, 300) + (result.content.length > 300 ? '...' : '');
    if (result.results && Array.isArray(result.results)) {
      return result.results.map((r: any) => `${r.title}: ${r.snippet?.slice(0, 120) || ''}`).join('\n');
    }
    if (result.message) return result.message;
    return JSON.stringify(result, null, 2).slice(0, 400);
  }

  let toolParts = $derived(
    (parts ?? []).filter(p => p.type === 'tool-invocation' && p.toolInvocation)
  );
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

    {#each toolParts as part}
      {@const inv = part.toolInvocation}
      {@const icon = toolIcons[inv.toolName] ?? '\u{1F527}'}
      {@const label = toolLabels[inv.toolName] ?? inv.toolName}
      {@const isDone = inv.state === 'result'}
      <div class="tool-card" class:done={isDone}>
        <div class="tool-header">
          <span class="tool-icon">{icon}</span>
          <span class="tool-name">{label}</span>
          {#if isDone}
            <span class="tool-status done-check">&#10003;</span>
          {:else}
            <span class="tool-status spinner"></span>
          {/if}
        </div>
        <div class="tool-args">
          {#if inv.toolName === 'calculator' && inv.args?.expression}
            <code>{inv.args.expression}</code>
          {:else if inv.toolName === 'webSearch' && inv.args?.query}
            <span class="tool-arg-text">"{inv.args.query}"</span>
          {:else if inv.toolName === 'urlFetch' && inv.args?.url}
            <span class="tool-arg-text tool-url">{inv.args.url}</span>
          {/if}
        </div>
        {#if isDone && inv.result}
          <div class="tool-result">
            <pre class="tool-result-text">{formatToolResult(inv.result)}</pre>
          </div>
        {/if}
      </div>
    {/each}

    {#if isStreaming && !content && toolParts.length === 0}
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

  .tool-card {
    margin: 8px 0 4px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    overflow: hidden;
    font-size: 12px;
  }

  .tool-card.done {
    border-color: rgba(74, 222, 128, 0.2);
  }

  .tool-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid var(--border-subtle);
  }

  .tool-icon {
    font-size: 13px;
    line-height: 1;
  }

  .tool-name {
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 11px;
    letter-spacing: 0.02em;
    flex: 1;
  }

  .tool-status {
    font-size: 12px;
    line-height: 1;
  }

  .done-check {
    color: #4ade80;
    font-weight: 700;
  }

  .spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid var(--border-subtle);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .tool-args {
    padding: 6px 10px;
  }

  .tool-args code {
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #e2b3ff;
    background: rgba(255, 255, 255, 0.05);
    padding: 1px 5px;
    border-radius: 3px;
  }

  .tool-arg-text {
    color: var(--text-secondary);
    font-size: 12px;
  }

  .tool-url {
    word-break: break-all;
    color: var(--accent-glow);
  }

  .tool-code {
    margin: 0;
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-all;
    background: rgba(0, 0, 0, 0.2);
    padding: 4px 6px;
    border-radius: 3px;
  }

  .tool-result {
    padding: 6px 10px;
    border-top: 1px solid var(--border-subtle);
    background: rgba(74, 222, 128, 0.03);
  }

  .tool-result-text {
    margin: 0;
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 150px;
    overflow-y: auto;
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
