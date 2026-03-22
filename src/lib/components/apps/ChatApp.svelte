<script lang="ts">
  import { Send } from 'lucide-svelte';

  let inputValue = $state('');

  const conversations = [
    { id: 1, name: 'Project Planning', preview: 'Let me help you outline...', time: '2m ago', active: true },
    { id: 2, name: 'Code Review', preview: 'The function looks good but...', time: '1h ago', active: false },
    { id: 3, name: 'Research Notes', preview: 'Here are the key findings...', time: '3h ago', active: false }
  ];

  const messages = [
    { id: 1, role: 'user' as const, text: 'Can you help me design the architecture for a new web application?' },
    { id: 2, role: 'assistant' as const, text: "I'd be happy to help! Let me outline a clean architecture for you. I'd recommend a modular approach with these key layers:\n\n• Presentation Layer — Components & Views\n• Business Logic — Services & Stores\n• Data Layer — API clients & Models\n\nShall I go deeper into any of these?" },
    { id: 3, role: 'user' as const, text: 'Yes, tell me more about the data layer.' },
    { id: 4, role: 'assistant' as const, text: 'The data layer should abstract all external communication. Use a repository pattern: each entity gets a repository class that encapsulates API calls, caching, and data transformation. This keeps your business logic clean and testable.' }
  ];

  function handleSend() {
    if (inputValue.trim()) {
      inputValue = '';
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }
</script>

<div class="chat-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Conversations</span>
    </div>
    <div class="conv-list scrollbar-thin">
      {#each conversations as conv}
        <button class="conv-item" class:active={conv.active}>
          <div class="conv-name">{conv.name}</div>
          <div class="conv-meta">
            <span class="conv-preview">{conv.preview}</span>
            <span class="conv-time">{conv.time}</span>
          </div>
        </button>
      {/each}
    </div>
  </div>
  <div class="main">
    <div class="messages scrollbar-thin">
      {#each messages as msg}
        <div class="message" class:user={msg.role === 'user'} class:assistant={msg.role === 'assistant'}>
          <div class="message-bubble">
            {msg.text}
          </div>
        </div>
      {/each}
    </div>
    <div class="input-bar">
      <input
        type="text"
        placeholder="Type a message..."
        bind:value={inputValue}
        onkeydown={handleKeydown}
      />
      <button class="send-btn" onclick={handleSend} aria-label="Send">
        <Send size={16} />
      </button>
    </div>
  </div>
</div>

<style>
  .chat-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 240px;
    border-right: 1px solid var(--border-subtle);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .conv-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px;
  }

  .conv-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 10px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background var(--transition-fast);
  }

  .conv-item:hover {
    background: var(--bg-surface-hover);
  }

  .conv-item.active {
    background: var(--accent-subtle);
  }

  .conv-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 2px;
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

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .message {
    display: flex;
    max-width: 80%;
  }

  .message.user {
    align-self: flex-end;
  }

  .message.assistant {
    align-self: flex-start;
  }

  .message-bubble {
    padding: 10px 14px;
    border-radius: var(--radius-md);
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
  }

  .message.user .message-bubble {
    background: var(--accent);
    color: white;
    border-bottom-right-radius: 4px;
  }

  .message.assistant .message-bubble {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
  }

  .input-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid var(--border-subtle);
  }

  .input-bar input {
    flex: 1;
    height: 36px;
    padding: 0 12px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 13px;
    outline: none;
    transition: border-color var(--transition-fast);
  }

  .input-bar input::placeholder {
    color: var(--text-muted);
  }

  .input-bar input:focus {
    border-color: var(--accent);
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

  .send-btn:hover {
    background: var(--accent-glow);
  }
</style>
