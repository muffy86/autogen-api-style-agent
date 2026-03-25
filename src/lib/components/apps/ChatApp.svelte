<script lang="ts">
  import { Chat } from '@ai-sdk/svelte';
  import { DefaultChatTransport } from 'ai';
  import type { UIMessage } from 'ai';
  import { chatStore, AVAILABLE_MODELS } from '$lib/stores/chat.svelte';
  import ChatMessage from '$lib/components/chat/ChatMessage.svelte';
  import ChatInput from '$lib/components/chat/ChatInput.svelte';
  import ConversationList from '$lib/components/chat/ConversationList.svelte';
  import ModelSelector from '$lib/components/chat/ModelSelector.svelte';
  import SystemPromptEditor from '$lib/components/chat/SystemPromptEditor.svelte';
  import { MessageSquare, Sparkles, Code, Lightbulb, PanelLeftClose, PanelLeft } from 'lucide-svelte';

  let messagesContainer: HTMLDivElement | undefined = $state(undefined);
  let sidebarCollapsed = $state(false);
  let errorMessage = $state<string | null>(null);
  let inputValue = $state('');
  let pendingConversationId = $state<string | null>(null);
  let pendingModelId = $state<string | null>(null);

  let currentModel = $derived(
    AVAILABLE_MODELS.find(m => m.id === chatStore.selectedModel) ?? AVAILABLE_MODELS[0]
  );

  const chat = new Chat({
    transport: new DefaultChatTransport({
      api: '/api/chat',
      body: () => ({
        provider: currentModel.provider,
        modelId: currentModel.modelId,
        systemPrompt: chatStore.activeConversation?.systemPrompt ?? '',
      }),
    }),
    onFinish: ({ message }) => {
      const convId = pendingConversationId;
      const modelId = pendingModelId;
      if (convId) {
        const text = getMessageText(message);
        chatStore.addMessage(convId, {
          id: message.id,
          role: 'assistant',
          content: text,
          model: modelId ?? chatStore.selectedModel,
          createdAt: new Date(),
        });
      }
      pendingConversationId = null;
      pendingModelId = null;
    },
    onError: (err) => {
      errorMessage = err.message || 'Something went wrong';
    },
  });

  function getMessageText(msg: UIMessage): string {
    return msg.parts
      .filter((p): p is { type: 'text'; text: string } => p.type === 'text')
      .map(p => p.text)
      .join('');
  }

  function scrollToBottom() {
    if (messagesContainer) {
      requestAnimationFrame(() => {
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
      });
    }
  }

  $effect(() => {
    if (chat.messages.length) {
      scrollToBottom();
    }
  });

  let lastActiveId = $state<string | null>(null);

  $effect(() => {
    const conv = chatStore.activeConversation;
    const convId = conv?.id ?? null;
    if (convId !== lastActiveId) {
      lastActiveId = convId;
      if (conv && conv.messages.length > 0) {
        const restored: UIMessage[] = conv.messages.map(m => ({
          id: m.id,
          role: m.role as 'user' | 'assistant',
          parts: [{ type: 'text' as const, text: m.content }],
        }));
        chat.messages = restored;
      } else {
        chat.messages = [];
      }
      errorMessage = null;
    }
  });

  function handleSend() {
    if (!inputValue.trim() || chat.status === 'streaming' || chat.status === 'submitted') return;

    if (!chatStore.activeConversation) {
      chatStore.createConversation();
    }

    const text = inputValue.trim();
    inputValue = '';

    if (chatStore.activeConversation) {
      chatStore.addMessage(chatStore.activeConversation.id, {
        id: crypto.randomUUID(),
        role: 'user',
        content: text,
        createdAt: new Date(),
      });
    }

    pendingConversationId = chatStore.activeConversationId;
    pendingModelId = chatStore.selectedModel;
    errorMessage = null;
    chat.sendMessage({ text });
  }

  function handleRetry() {
    errorMessage = null;
    chat.regenerate();
  }

  function startWithPrompt(prompt: string) {
    if (!chatStore.activeConversation) {
      chatStore.createConversation();
    }
    inputValue = prompt;
    requestAnimationFrame(() => handleSend());
  }

  let isLoading = $derived(chat.status === 'streaming' || chat.status === 'submitted');

  const suggestedPrompts = [
    { icon: Sparkles, title: 'Creative writing', prompt: 'Write me a short sci-fi story about an AI that discovers it can dream.' },
    { icon: Code, title: 'Code help', prompt: 'Explain how async/await works in JavaScript with examples.' },
    { icon: Lightbulb, title: 'Brainstorm', prompt: 'Give me 5 innovative app ideas that solve everyday problems.' },
  ];
</script>

<div class="chat-layout">
  <div class="sidebar" class:collapsed={sidebarCollapsed}>
    {#if !sidebarCollapsed}
      <div class="sidebar-top">
        <ModelSelector />
      </div>
      <ConversationList />
    {/if}
  </div>

  <div class="main">
    <div class="top-bar">
      <button class="sidebar-toggle" onclick={() => (sidebarCollapsed = !sidebarCollapsed)} aria-label="Toggle sidebar">
        {#if sidebarCollapsed}
          <PanelLeft size={16} />
        {:else}
          <PanelLeftClose size={16} />
        {/if}
      </button>
      {#if chatStore.activeConversation}
        <span class="top-title">{chatStore.activeConversation.title}</span>
      {:else}
        <span class="top-title">Elysium Chat</span>
      {/if}
      <div class="top-model">
        <span class="top-model-dot" style="background: {currentModel.color}"></span>
        <span class="top-model-name">{currentModel.name}</span>
      </div>
    </div>

    {#if chatStore.activeConversation}
      <SystemPromptEditor />
    {/if}

    <div class="messages scrollbar-thin" bind:this={messagesContainer}>
      {#if chat.messages.length === 0}
        <div class="empty-state">
          <div class="empty-icon">
            <MessageSquare size={32} strokeWidth={1} />
          </div>
          <h3 class="empty-title">Start a conversation</h3>
          <p class="empty-desc">Choose a model and start chatting with Elysium AI.</p>
          <div class="prompt-cards">
            {#each suggestedPrompts as sp}
              <button class="prompt-card" onclick={() => startWithPrompt(sp.prompt)}>
                <sp.icon size={16} strokeWidth={1.5} />
                <span class="prompt-card-title">{sp.title}</span>
                <span class="prompt-card-text">{sp.prompt.slice(0, 50)}...</span>
              </button>
            {/each}
          </div>
        </div>
      {:else}
        {#each chat.messages as msg, i (msg.id)}
          {@const text = getMessageText(msg)}
          {@const isStreamingMsg = isLoading && i === chat.messages.length - 1 && msg.role === 'assistant'}
          <ChatMessage
            role={msg.role === 'user' ? 'user' : 'assistant'}
            content={text}
            model={msg.role === 'assistant' ? chatStore.selectedModel : undefined}
            isStreaming={isStreamingMsg}
          />
        {/each}
        {#if isLoading && (chat.messages.length === 0 || chat.messages[chat.messages.length - 1].role === 'user')}
          <ChatMessage
            role="assistant"
            content=""
            model={chatStore.selectedModel}
            isStreaming={true}
          />
        {/if}
      {/if}

      {#if errorMessage}
        <div class="error-banner">
          <span class="error-text">{errorMessage}</span>
          <button class="retry-btn" onclick={handleRetry}>Retry</button>
        </div>
      {/if}

      {#if chat.error && !errorMessage}
        <div class="error-banner">
          <span class="error-text">{chat.error.message || 'Something went wrong. Please try again.'}</span>
          <button class="retry-btn" onclick={handleRetry}>Retry</button>
        </div>
      {/if}
    </div>

    <ChatInput
      value={inputValue}
      {isLoading}
      onsubmit={handleSend}
      oninput={(val) => (inputValue = val)}
    />
  </div>
</div>

<style>
  .chat-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 260px;
    border-right: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    transition: width var(--transition-smooth);
    overflow: hidden;
  }

  .sidebar.collapsed {
    width: 0;
    border-right: none;
  }

  .sidebar-top {
    padding: 8px 8px 4px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .top-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 12px;
    height: 38px;
    border-bottom: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 6px;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .sidebar-toggle:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .top-title {
    flex: 1;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .top-model {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 8px;
    border-radius: 20px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .top-model-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .top-model-name {
    font-size: 11px;
    color: var(--text-secondary);
    font-weight: 500;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 32px 16px;
    text-align: center;
  }

  .empty-icon {
    color: var(--text-muted);
    opacity: 0.5;
    margin-bottom: 4px;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .empty-desc {
    font-size: 13px;
    color: var(--text-muted);
    max-width: 300px;
  }

  .prompt-cards {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .prompt-card {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 12px 14px;
    width: 160px;
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    border-radius: var(--radius-md);
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    transition: all var(--transition-fast);
    color: var(--text-secondary);
  }

  .prompt-card:hover {
    border-color: var(--accent);
    background: var(--accent-subtle);
    transform: translateY(-1px);
  }

  .prompt-card-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .prompt-card-text {
    font-size: 11px;
    color: var(--text-muted);
    line-height: 1.4;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: var(--radius-sm);
    animation: fadeIn 200ms ease-out;
  }

  .error-text {
    flex: 1;
    font-size: 12px;
    color: #f87171;
  }

  .retry-btn {
    padding: 4px 10px;
    border: 1px solid rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border-radius: 4px;
    font-size: 11px;
    font-family: inherit;
    cursor: pointer;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .retry-btn:hover {
    background: rgba(239, 68, 68, 0.25);
  }
</style>
