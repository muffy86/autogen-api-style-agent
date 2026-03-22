<script lang="ts">
  import {
    ArrowUp,
    Square,
    Paperclip,
    Globe,
    X,
    FileText,
    FileCode,
    File as FileIcon,
    Search,
    Image as ImageIcon,
    Terminal,
    MessageSquare,
    Eraser,
    Cpu,
  } from 'lucide-svelte';
  import { AVAILABLE_MODELS, chatStore } from '$lib/stores/chat.svelte';
  import type { FileAttachment } from '$lib/types';

  interface Props {
    value: string;
    isLoading: boolean;
    attachments: FileAttachment[];
    searchMode: boolean;
    onsubmit: () => void;
    oninput: (val: string) => void;
    onattach: (files: FileAttachment[]) => void;
    onremoveattachment: (id: string) => void;
    onstop: () => void;
    onsearchtoggle: () => void;
    onslashcommand?: (cmd: string, arg: string) => void;
  }

  let {
    value,
    isLoading,
    attachments,
    searchMode,
    onsubmit,
    oninput,
    onattach,
    onremoveattachment,
    onstop,
    onsearchtoggle,
    onslashcommand,
  }: Props = $props();

  let textareaEl: HTMLTextAreaElement | undefined = $state(undefined);
  let fileInputEl: HTMLInputElement | undefined = $state(undefined);
  let isFocused = $state(false);
  let showSlashMenu = $state(false);
  let slashFilter = $state('');
  let selectedSlashIndex = $state(0);

  const slashCommands = [
    { cmd: '/search', arg: '[query]', desc: 'Web search', icon: Search },
    { cmd: '/image', arg: '[prompt]', desc: 'Generate image', icon: ImageIcon },
    { cmd: '/system', arg: '[prompt]', desc: 'Set system prompt', icon: Terminal },
    { cmd: '/clear', arg: '', desc: 'Clear conversation', icon: Eraser },
    { cmd: '/model', arg: '[name]', desc: 'Switch model', icon: Cpu },
  ];

  let filteredCommands = $derived.by(() => {
    if (!slashFilter) return slashCommands;
    return slashCommands.filter(c => c.cmd.startsWith('/' + slashFilter));
  });

  let currentModel = $derived(
    AVAILABLE_MODELS.find(m => m.id === chatStore.selectedModel) ?? AVAILABLE_MODELS[0]
  );

  let tokenEstimate = $derived(Math.ceil((value.length || 0) / 4));
  let hasContent = $derived(value.trim().length > 0 || attachments.length > 0);

  function autoResize() {
    if (!textareaEl) return;
    textareaEl.style.height = 'auto';
    textareaEl.style.height = Math.min(textareaEl.scrollHeight, 200) + 'px';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (showSlashMenu) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedSlashIndex = Math.min(selectedSlashIndex + 1, filteredCommands.length - 1);
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedSlashIndex = Math.max(selectedSlashIndex - 1, 0);
        return;
      }
      if (e.key === 'Tab' || e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedSlashIndex]) {
          const cmd = filteredCommands[selectedSlashIndex];
          oninput(cmd.cmd + ' ');
          showSlashMenu = false;
          textareaEl?.focus();
        }
        return;
      }
      if (e.key === 'Escape') {
        showSlashMenu = false;
        return;
      }
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (isLoading) {
        onstop();
      } else if (hasContent) {
        handleSubmit();
      }
    }
  }

  function handleSubmit() {
    if (value.startsWith('/') && onslashcommand) {
      const parts = value.match(/^\/(\S+)\s*(.*)/);
      if (parts) {
        onslashcommand(parts[1], parts[2]);
        return;
      }
    }
    onsubmit();
  }

  function handleInput(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    oninput(target.value);
    autoResize();

    if (target.value === '/') {
      showSlashMenu = true;
      slashFilter = '';
      selectedSlashIndex = 0;
    } else if (target.value.startsWith('/') && !target.value.includes(' ')) {
      showSlashMenu = true;
      slashFilter = target.value.slice(1);
      selectedSlashIndex = 0;
    } else {
      showSlashMenu = false;
    }
  }

  function handleFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    if (!input.files) return;
    const newFiles: FileAttachment[] = [];

    const maxFiles = 5 - attachments.length;
    const filesToProcess = Array.from(input.files).slice(0, maxFiles);

    for (const file of filesToProcess) {
      const type = getFileType(file);
      const attachment: FileAttachment = {
        id: `file-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        name: file.name,
        type,
        mimeType: file.type,
        size: file.size,
        file,
      };

      if (type === 'image') {
        const reader = new FileReader();
        reader.onload = () => {
          attachment.dataUrl = reader.result as string;
          onattach([...attachments, attachment]);
        };
        reader.readAsDataURL(file);
      } else {
        newFiles.push(attachment);
      }
    }

    if (newFiles.length > 0) {
      onattach([...attachments, ...newFiles]);
    }

    input.value = '';
  }

  function getFileType(file: File): FileAttachment['type'] {
    if (file.type.startsWith('image/')) return 'image';
    if (file.type === 'application/pdf' || file.type.includes('document')) return 'document';
    const codeExts = ['.js', '.ts', '.py', '.json', '.md', '.css', '.html', '.svelte', '.jsx', '.tsx'];
    if (codeExts.some(ext => file.name.endsWith(ext))) return 'code';
    return 'other';
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return bytes + 'B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
  }

  $effect(() => {
    if (!value && textareaEl) {
      textareaEl.style.height = 'auto';
    }
  });
</script>

<div class="chat-input-container" class:focused={isFocused}>
  {#if attachments.length > 0}
    <div class="attachment-row">
      {#each attachments as att (att.id)}
        <div class="attachment-thumb" class:image={att.type === 'image'}>
          {#if att.type === 'image' && att.dataUrl}
            <img src={att.dataUrl} alt={att.name} class="thumb-img" />
          {:else if att.type === 'document'}
            <FileText size={18} />
          {:else if att.type === 'code'}
            <FileCode size={18} />
          {:else}
            <FileIcon size={18} />
          {/if}
          {#if att.type !== 'image'}
            <span class="thumb-name">{att.name}</span>
            <span class="thumb-size">{formatSize(att.size)}</span>
          {/if}
          <button class="thumb-remove" onclick={() => onremoveattachment(att.id)}>
            <X size={10} />
          </button>
        </div>
      {/each}
    </div>
  {/if}

  {#if showSlashMenu && filteredCommands.length > 0}
    <div class="slash-menu glass">
      {#each filteredCommands as cmd, i (cmd.cmd)}
        <button
          class="slash-item"
          class:active={i === selectedSlashIndex}
          onclick={() => {
            oninput(cmd.cmd + ' ');
            showSlashMenu = false;
            textareaEl?.focus();
          }}
          onmouseenter={() => (selectedSlashIndex = i)}
        >
          <cmd.icon size={14} />
          <span class="slash-cmd">{cmd.cmd}</span>
          <span class="slash-arg">{cmd.arg}</span>
          <span class="slash-desc">{cmd.desc}</span>
        </button>
      {/each}
    </div>
  {/if}

  {#if searchMode}
    <div class="search-badge">
      <Search size={11} />
      <span>Web Search</span>
      <button class="search-badge-close" onclick={onsearchtoggle}>
        <X size={10} />
      </button>
    </div>
  {/if}

  <div class="input-row">
    <button
      class="input-action-btn"
      onclick={() => fileInputEl?.click()}
      aria-label="Attach files"
      disabled={attachments.length >= 5}
    >
      <Paperclip size={16} />
    </button>
    <input
      bind:this={fileInputEl}
      type="file"
      multiple
      accept="image/*,.pdf,.txt,.md,.json,.csv,.py,.js,.ts,.jsx,.tsx,.html,.css,.svelte"
      onchange={handleFileSelect}
      hidden
    />
    <button
      class="input-action-btn"
      class:active={searchMode}
      onclick={onsearchtoggle}
      aria-label="Toggle web search"
    >
      <Globe size={16} />
    </button>

    <textarea
      bind:this={textareaEl}
      class="input-textarea"
      placeholder={searchMode ? 'Search the web...' : 'Message Elysium...'}
      rows={1}
      value={value}
      oninput={handleInput}
      onkeydown={handleKeydown}
      onfocus={() => (isFocused = true)}
      onblur={() => (isFocused = false)}
    ></textarea>

    {#if isLoading}
      <button class="send-btn stop" onclick={onstop} aria-label="Stop streaming">
        <Square size={14} />
      </button>
    {:else}
      <button
        class="send-btn"
        class:ready={hasContent}
        onclick={handleSubmit}
        disabled={!hasContent}
        aria-label="Send message"
      >
        <ArrowUp size={16} strokeWidth={2.5} />
      </button>
    {/if}
  </div>

  <div class="status-line">
    <span class="status-hint">
      <span class="slash-hint">/</span> for commands
    </span>
    <div class="status-model">
      <span class="status-model-dot" style="background: {currentModel.color}"></span>
      <span>{currentModel.name}</span>
    </div>
    {#if value.length > 0}
      <span class="status-tokens">~{tokenEstimate} tokens</span>
    {/if}
  </div>
</div>

<style>
  .chat-input-container {
    padding: 8px 12px 6px;
    border-top: 1px solid var(--border-subtle);
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    display: flex;
    flex-direction: column;
    gap: 4px;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    transition: border-color var(--transition-fast);
    position: relative;
  }

  .chat-input-container.focused {
    border-top-color: var(--accent);
    box-shadow: 0 -1px 12px rgba(139, 92, 246, 0.08);
  }

  .attachment-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    padding: 4px 0 2px;
  }

  .attachment-thumb {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    font-size: 11px;
    color: var(--text-secondary);
    position: relative;
    animation: fadeIn 150ms ease-out;
  }

  .attachment-thumb.image {
    padding: 2px;
    width: 52px;
    height: 52px;
    overflow: hidden;
    border-radius: var(--radius-sm);
  }

  .thumb-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 6px;
  }

  .thumb-name {
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .thumb-size {
    color: var(--text-muted);
    font-size: 10px;
  }

  .thumb-remove {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: rgba(239, 68, 68, 0.9);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity var(--transition-fast);
  }

  .attachment-thumb:hover .thumb-remove {
    opacity: 1;
  }

  .slash-menu {
    position: absolute;
    bottom: calc(100% + 4px);
    left: 12px;
    width: 280px;
    border-radius: var(--radius-md);
    padding: 4px;
    z-index: 50;
    animation: slideUp 150ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  .slash-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 7px 10px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    font-family: inherit;
    color: var(--text-secondary);
    transition: background var(--transition-fast);
  }

  .slash-item:hover,
  .slash-item.active {
    background: var(--bg-surface-hover);
  }

  .slash-cmd {
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-glow);
    font-family: 'SF Mono', 'Fira Code', monospace;
  }

  .slash-arg {
    font-size: 11px;
    color: var(--text-muted);
    font-family: 'SF Mono', 'Fira Code', monospace;
  }

  .slash-desc {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-muted);
  }

  .search-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px 3px 6px;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px;
    font-size: 11px;
    color: var(--accent-glow);
    font-weight: 500;
    width: fit-content;
    animation: fadeIn 150ms ease-out;
  }

  .search-badge-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    border: none;
    background: rgba(255, 255, 255, 0.1);
    color: var(--accent-glow);
    border-radius: 50%;
    cursor: pointer;
    padding: 0;
    margin-left: 2px;
  }

  .input-row {
    display: flex;
    align-items: flex-end;
    gap: 4px;
  }

  .input-action-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .input-action-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .input-action-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .input-action-btn.active {
    background: rgba(139, 92, 246, 0.2);
    color: var(--accent-glow);
    box-shadow: 0 0 8px rgba(139, 92, 246, 0.2);
  }

  .input-textarea {
    flex: 1;
    min-height: 36px;
    max-height: 200px;
    padding: 7px 12px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    line-height: 1.5;
    resize: none;
    outline: none;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  }

  .input-textarea::placeholder {
    color: var(--text-muted);
  }

  .input-textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1);
  }

  .send-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: var(--bg-surface-hover);
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .send-btn.ready {
    background: var(--accent);
    color: white;
  }

  .send-btn.ready:hover {
    background: var(--accent-glow);
    box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
  }

  .send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .send-btn.stop {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    cursor: pointer;
  }

  .send-btn.stop:hover {
    background: rgba(239, 68, 68, 0.35);
  }

  .status-line {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 4px;
    min-height: 18px;
  }

  .status-hint {
    font-size: 10px;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 3px;
  }

  .slash-hint {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 3px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    font-size: 10px;
    color: var(--text-muted);
    font-family: 'SF Mono', monospace;
  }

  .status-model {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    color: var(--text-muted);
    margin-left: auto;
  }

  .status-model-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
  }

  .status-tokens {
    font-size: 10px;
    color: var(--text-muted);
    font-family: 'SF Mono', monospace;
    padding-left: 8px;
    border-left: 1px solid var(--border-subtle);
  }
</style>
