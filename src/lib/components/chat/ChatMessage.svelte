<script lang="ts">
  import MarkdownRenderer from './MarkdownRenderer.svelte';
  import { AVAILABLE_MODELS } from '$lib/stores/chat.svelte';
  import {
    Copy,
    RefreshCw,
    Pin,
    MoreHorizontal,
    Search,
    ExternalLink,
    ChevronDown,
    ChevronRight,
    Check,
    AlertCircle,
    Loader2,
    ArrowRight,
    Code,
    Eye,
    Maximize2,
    FileText,
    Image as ImageIcon,
  } from 'lucide-svelte';
  import type {
    MessageAttachment,
    WebSearchResult,
    ToolCallResult,
    MessageArtifact,
  } from '$lib/types';

  interface Props {
    role: 'user' | 'assistant' | 'system';
    content: string;
    parts?: Array<{ type: string; text?: string; toolInvocation?: any }>;
    model?: string;
    isStreaming?: boolean;
    isLastMessage?: boolean;
    attachments?: MessageAttachment[];
    webSearchResults?: WebSearchResult[];
    toolCalls?: ToolCallResult[];
    artifacts?: MessageArtifact[];
    suggestions?: string[];
    onSuggest?: (text: string) => void;
    onRegenerate?: () => void;
  }

  let {
    role,
    content,
    parts,
    model,
    isStreaming = false,
    isLastMessage = false,
    attachments,
    webSearchResults,
    toolCalls,
    artifacts,
    suggestions,
    onSuggest,
    onRegenerate,
  }: Props = $props();

  let modelInfo = $derived(model ? AVAILABLE_MODELS.find(m => m.id === model) : null);
  let showActions = $state(false);
  let copied = $state(false);
  let searchExpanded = $state(false);
  let expandedToolCalls = $state<Set<string>>(new Set());
  let artifactViews = $state<Record<string, 'code' | 'preview'>>({});
  let expandedImage = $state<string | null>(null);

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

  function copyContent() {
    navigator.clipboard.writeText(content);
    copied = true;
    setTimeout(() => (copied = false), 2000);
  }

  function toggleToolCall(id: string) {
    const next = new Set(expandedToolCalls);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    expandedToolCalls = next;
  }

  function toggleArtifactView(id: string) {
    const current = artifactViews[id] ?? 'code';
    artifactViews = { ...artifactViews, [id]: current === 'code' ? 'preview' : 'code' };
  }

  function copyArtifact(text: string) {
    navigator.clipboard.writeText(text);
  }

  let visibleSearchResults = $derived.by(() => {
    if (!webSearchResults) return [];
    return searchExpanded ? webSearchResults : webSearchResults.slice(0, 3);
  });

  let hasMoreResults = $derived((webSearchResults?.length ?? 0) > 3);
</script>

{#if expandedImage}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="image-overlay" onclick={() => (expandedImage = null)} onkeydown={(e) => e.key === 'Escape' && (expandedImage = null)}>
    <img src={expandedImage} alt="Full size" class="image-overlay-img" />
  </div>
{/if}

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="message"
  class:user={role === 'user'}
  class:assistant={role === 'assistant'}
  onmouseenter={() => (showActions = true)}
  onmouseleave={() => (showActions = false)}
>
  {#if role === 'assistant' && modelInfo}
    <div class="model-badge">
      <span class="model-dot" style="background: {modelInfo.color}"></span>
      <span class="model-name">{modelInfo.name}</span>
    </div>
  {/if}

  {#if role === 'user' && attachments && attachments.length > 0}
    <div class="msg-attachments">
      {#each attachments as att (att.id)}
        {#if att.type === 'image'}
          <button class="msg-img-thumb" onclick={() => (expandedImage = att.url)}>
            <img src={att.url} alt={att.name} />
          </button>
        {:else}
          <div class="msg-file-chip">
            {#if att.type === 'document'}
              <FileText size={13} />
            {:else if att.type === 'code'}
              <Code size={13} />
            {:else}
              <FileText size={13} />
            {/if}
            <span>{att.name}</span>
          </div>
        {/if}
      {/each}
    </div>
  {/if}

  {#if toolCalls && toolCalls.length > 0}
    <div class="tool-calls">
      {#each toolCalls as tc (tc.id)}
        <div class="tool-call" class:running={tc.status === 'running'} class:error={tc.status === 'error'} class:completed={tc.status === 'completed'}>
          <button class="tool-call-header" onclick={() => toggleToolCall(tc.id)}>
            <div class="tool-call-status">
              {#if tc.status === 'running'}
                <Loader2 size={13} class="spin" />
              {:else if tc.status === 'completed'}
                <Check size={13} />
              {:else}
                <AlertCircle size={13} />
              {/if}
            </div>
            <span class="tool-call-label">
              {tc.status === 'running' ? 'Running' : tc.status === 'completed' ? 'Completed' : 'Error'}:
              <strong>{tc.name}</strong>
            </span>
            {#if tc.duration}
              <span class="tool-call-time">{(tc.duration / 1000).toFixed(1)}s</span>
            {/if}
            <span class="tool-call-chevron">
              {#if expandedToolCalls.has(tc.id)}
                <ChevronDown size={12} />
              {:else}
                <ChevronRight size={12} />
              {/if}
            </span>
          </button>
          {#if expandedToolCalls.has(tc.id)}
            <div class="tool-call-body">
              {#if tc.input}
                <div class="tool-call-section">
                  <span class="tool-call-section-label">Input</span>
                  <pre class="tool-call-json">{JSON.stringify(tc.input, null, 2)}</pre>
                </div>
              {/if}
              {#if tc.output}
                <div class="tool-call-section">
                  <span class="tool-call-section-label">Output</span>
                  <pre class="tool-call-json">{tc.output}</pre>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  {#if webSearchResults && webSearchResults.length > 0}
    <div class="search-results-card glass">
      <div class="search-results-header">
        <Search size={13} />
        <span>Web Search Results</span>
        <span class="search-count">{webSearchResults.length}</span>
      </div>
      <div class="search-results-list">
        {#each visibleSearchResults as result, i}
          <a href={result.url} target="_blank" rel="noopener noreferrer" class="search-result-item">
            <div class="search-result-rank">[{i + 1}]</div>
            <div class="search-result-content">
              <div class="search-result-title">
                {#if result.favicon}
                  <img src={result.favicon} alt="" class="search-favicon" />
                {/if}
                {result.title}
                <ExternalLink size={10} />
              </div>
              <div class="search-result-snippet">{result.snippet}</div>
              <div class="search-result-url">{result.url.replace(/^https?:\/\//, '').split('/')[0]}</div>
            </div>
          </a>
        {/each}
      </div>
      {#if hasMoreResults}
        <button class="search-show-more" onclick={() => (searchExpanded = !searchExpanded)}>
          {#if searchExpanded}
            <ChevronDown size={12} /> Show less
          {:else}
            <ChevronRight size={12} /> Show {(webSearchResults?.length ?? 0) - 3} more results
          {/if}
        </button>
      {/if}
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
      <div class="thinking-indicator">
        <div class="thinking-dots">
          <span></span><span></span><span></span>
        </div>
        <div class="thinking-text">
          {#if modelInfo}
            <span class="thinking-model-dot" style="background: {modelInfo.color}"></span>
          {/if}
          <span class="thinking-label">Elysium is thinking</span>
          <span class="thinking-shimmer"></span>
        </div>
      </div>
    {/if}
  </div>

  {#if artifacts && artifacts.length > 0}
    <div class="artifacts">
      {#each artifacts as art (art.id)}
        <div class="artifact-block">
          <div class="artifact-header">
            <div class="artifact-type-badge">
              {#if art.type === 'code'}
                <Code size={12} />
              {:else if art.type === 'html' || art.type === 'svg'}
                <Eye size={12} />
              {:else}
                <FileText size={12} />
              {/if}
              <span>{art.type.toUpperCase()}</span>
            </div>
            <span class="artifact-title">{art.title}</span>
            <div class="artifact-actions">
              {#if art.type === 'html' || art.type === 'svg'}
                <button
                  class="artifact-action-btn"
                  class:active={(artifactViews[art.id] ?? 'code') === 'preview'}
                  onclick={() => toggleArtifactView(art.id)}
                >
                  {#if (artifactViews[art.id] ?? 'code') === 'code'}
                    <Eye size={12} />
                  {:else}
                    <Code size={12} />
                  {/if}
                </button>
              {/if}
              <button class="artifact-action-btn" onclick={() => copyArtifact(art.content)}>
                <Copy size={12} />
              </button>
              <button class="artifact-action-btn" onclick={() => {}}>
                <Maximize2 size={12} />
              </button>
            </div>
          </div>
          <div class="artifact-body">
            {#if (art.type === 'html' || art.type === 'svg') && (artifactViews[art.id] ?? 'code') === 'preview'}
              <iframe
                class="artifact-iframe"
                sandbox="allow-scripts"
                srcdoc={art.content}
                title={art.title}
              ></iframe>
            {:else if art.type === 'markdown'}
              <div class="artifact-md">
                <MarkdownRenderer content={art.content} />
              </div>
            {:else}
              <div class="artifact-code">
                <MarkdownRenderer content={'```' + (art.language ?? art.type) + '\n' + art.content + '\n```'} />
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}

  {#if showActions && role === 'assistant' && content && !isStreaming}
    <div class="message-actions">
      <button class="action-btn" onclick={copyContent}>
        {#if copied}
          <Check size={12} />
          <span>Copied</span>
        {:else}
          <Copy size={12} />
          <span>Copy</span>
        {/if}
      </button>
      {#if isLastMessage && onRegenerate}
        <button class="action-btn" onclick={onRegenerate}>
          <RefreshCw size={12} />
          <span>Regenerate</span>
        </button>
      {/if}
      <button class="action-btn" onclick={() => {}}>
        <Pin size={12} />
        <span>Pin</span>
      </button>
    </div>
  {/if}

  {#if isLastMessage && !isStreaming && role === 'assistant' && suggestions && suggestions.length > 0}
    <div class="suggestions">
      {#each suggestions as sug}
        <button class="suggestion-chip" onclick={() => onSuggest?.(sug)}>
          <ArrowRight size={11} />
          <span>{sug}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .message {
    display: flex;
    flex-direction: column;
    max-width: 82%;
    animation: msgIn 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
    position: relative;
  }

  @keyframes msgIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
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

  .msg-attachments {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 6px;
  }

  .msg-img-thumb {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    cursor: pointer;
    border: 1px solid var(--border-subtle);
    padding: 0;
    background: none;
    transition: all var(--transition-fast);
  }

  .msg-img-thumb:hover {
    border-color: var(--accent);
    transform: scale(1.05);
  }

  .msg-img-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .msg-file-chip {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 4px 8px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    font-size: 11px;
    color: var(--text-secondary);
  }

  .tool-calls {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 8px;
    width: 100%;
  }

  .tool-call {
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    overflow: hidden;
    background: var(--bg-surface);
  }

  .tool-call.running {
    border-color: rgba(139, 92, 246, 0.4);
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.05), rgba(59, 130, 246, 0.05));
    animation: pulseGlow 2s ease-in-out infinite;
  }

  .tool-call.completed {
    border-left: 3px solid #22c55e;
  }

  .tool-call.error {
    border-left: 3px solid #ef4444;
  }

  .tool-call-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 6px 10px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-family: inherit;
    color: var(--text-secondary);
    font-size: 12px;
  }

  .tool-call-status {
    display: flex;
    align-items: center;
    color: var(--text-muted);
  }

  .tool-call.running .tool-call-status {
    color: var(--accent-glow);
  }

  .tool-call.completed .tool-call-status {
    color: #22c55e;
  }

  .tool-call.error .tool-call-status {
    color: #ef4444;
  }

  .tool-call-status :global(.spin) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .tool-call-label strong {
    color: var(--text-primary);
  }

  .tool-call-time {
    margin-left: auto;
    font-size: 10px;
    color: var(--text-muted);
    font-family: 'SF Mono', monospace;
  }

  .tool-call-chevron {
    color: var(--text-muted);
  }

  .tool-call-body {
    padding: 0 10px 8px;
    animation: fadeIn 150ms ease-out;
  }

  .tool-call-section {
    margin-top: 6px;
  }

  .tool-call-section-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    display: block;
    margin-bottom: 2px;
  }

  .tool-call-json {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-secondary);
    background: rgba(0, 0, 0, 0.2);
    padding: 6px 8px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .search-results-card {
    width: 100%;
    border-radius: var(--radius-md);
    margin-bottom: 8px;
    overflow: hidden;
    animation: fadeIn 200ms ease-out;
  }

  .search-results-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .search-count {
    margin-left: auto;
    font-size: 10px;
    font-weight: 500;
    color: var(--text-muted);
    background: var(--bg-surface-hover);
    padding: 1px 6px;
    border-radius: 10px;
  }

  .search-results-list {
    padding: 4px;
  }

  .search-result-item {
    display: flex;
    gap: 8px;
    padding: 8px;
    border-radius: 6px;
    text-decoration: none;
    transition: background var(--transition-fast);
  }

  .search-result-item:hover {
    background: var(--bg-surface-hover);
  }

  .search-result-rank {
    font-size: 10px;
    font-weight: 700;
    color: var(--accent-glow);
    min-width: 20px;
    padding-top: 2px;
    font-family: 'SF Mono', monospace;
  }

  .search-result-content {
    flex: 1;
    min-width: 0;
  }

  .search-result-title {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 2px;
  }

  .search-favicon {
    width: 14px;
    height: 14px;
    border-radius: 2px;
  }

  .search-result-snippet {
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .search-result-url {
    font-size: 10px;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .search-show-more {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100%;
    padding: 6px 12px;
    border: none;
    border-top: 1px solid var(--border-subtle);
    background: transparent;
    color: var(--accent-glow);
    font-size: 11px;
    font-family: inherit;
    cursor: pointer;
    transition: background var(--transition-fast);
  }

  .search-show-more:hover {
    background: var(--bg-surface-hover);
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

  .thinking-indicator {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 2px 0;
  }

  .thinking-dots {
    display: flex;
    gap: 5px;
    padding: 2px 0;
  }

  .thinking-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--accent-glow);
    animation: dotBounce 1.4s ease-in-out infinite;
  }

  .thinking-dots span:nth-child(2) {
    animation-delay: 0.16s;
  }

  .thinking-dots span:nth-child(3) {
    animation-delay: 0.32s;
  }

  @keyframes dotBounce {
    0%, 80%, 100% { opacity: 0.3; transform: translateY(0) scale(0.85); }
    40% { opacity: 1; transform: translateY(-4px) scale(1); }
  }

  .thinking-text {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--text-muted);
    position: relative;
    overflow: hidden;
  }

  .thinking-model-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .thinking-label {
    position: relative;
  }

  .thinking-shimmer {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.15), transparent);
    animation: shimmer 2s ease-in-out infinite;
  }

  @keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
  }

  .artifacts {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 6px;
    width: 100%;
  }

  .artifact-block {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--bg-surface);
  }

  .artifact-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid var(--border-subtle);
  }

  .artifact-type-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent-glow);
    padding: 2px 6px;
    background: rgba(139, 92, 246, 0.1);
    border-radius: 4px;
  }

  .artifact-title {
    font-size: 12px;
    color: var(--text-primary);
    font-weight: 500;
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .artifact-actions {
    display: flex;
    gap: 2px;
  }

  .artifact-action-btn {
    width: 24px;
    height: 24px;
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

  .artifact-action-btn:hover,
  .artifact-action-btn.active {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .artifact-body {
    max-height: 400px;
    overflow: auto;
  }

  .artifact-iframe {
    width: 100%;
    min-height: 200px;
    height: 300px;
    border: none;
    background: white;
  }

  .artifact-md {
    padding: 10px 14px;
  }

  .artifact-code {
    padding: 0;
  }

  .artifact-code :global(.code-block-wrapper) {
    margin: 0;
    border: none;
    border-radius: 0;
  }

  .message-actions {
    display: flex;
    gap: 2px;
    margin-top: 4px;
    animation: fadeIn 150ms ease-out;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border: none;
    background: var(--bg-surface);
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    font-size: 11px;
    font-family: inherit;
    transition: all var(--transition-fast);
  }

  .action-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
    animation: fadeIn 300ms ease-out;
  }

  .suggestion-chip {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px 5px 8px;
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    border-radius: 20px;
    cursor: pointer;
    font-size: 12px;
    font-family: inherit;
    transition: all var(--transition-fast);
    max-width: 300px;
  }

  .suggestion-chip span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .suggestion-chip:hover {
    border-color: var(--accent);
    background: var(--accent-subtle);
    color: var(--text-primary);
  }

  .image-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    animation: fadeIn 200ms ease-out;
  }

  .image-overlay-img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    border-radius: var(--radius-md);
  }
</style>
