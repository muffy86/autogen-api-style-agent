<script lang="ts">
  import { AVAILABLE_MODELS } from '$lib/stores/chat.svelte';
  import { chatStore } from '$lib/stores/chat.svelte';
  import { ChevronDown } from 'lucide-svelte';

  let open = $state(false);

  let currentModel = $derived(
    AVAILABLE_MODELS.find(m => m.id === chatStore.selectedModel) ?? AVAILABLE_MODELS[0]
  );

  const providerOrder = ['openrouter', 'groq', 'openai', 'anthropic', 'google', 'xai'] as const;
  const providerLabels: Record<string, string> = {
    openrouter: 'OpenRouter',
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    google: 'Google',
    xai: 'xAI',
    groq: 'Groq',
  };

  let grouped = $derived.by(() => {
    const groups: Record<string, typeof AVAILABLE_MODELS> = {};
    const allowPaid = chatStore.allowPaid;
    for (const m of AVAILABLE_MODELS) {
      if (!allowPaid && m.tier === 'paid') continue;
      if (!groups[m.provider]) groups[m.provider] = [];
      groups[m.provider].push(m);
    }
    return providerOrder
      .filter(p => groups[p])
      .map(p => ({ provider: p, label: providerLabels[p], models: groups[p] }));
  });

  function select(modelId: string) {
    chatStore.setModel(modelId);
    open = false;
  }

  function handleClickOutside(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (!target.closest('.model-selector')) {
      open = false;
    }
  }

  $effect(() => {
    if (open) {
      document.addEventListener('click', handleClickOutside, true);
      return () => document.removeEventListener('click', handleClickOutside, true);
    }
  });
</script>

<div class="model-selector">
  <button class="selector-trigger" onclick={() => (open = !open)}>
    <span class="trigger-dot" style="background: {currentModel.color}"></span>
    <span class="trigger-name">{currentModel.name}</span>
    <ChevronDown size={12} />
  </button>

  {#if open}
    <div class="selector-dropdown glass">
      {#each grouped as group}
        <div class="provider-group">
          <div class="provider-label">{group.label}</div>
          {#each group.models as model}
            <button
              class="model-option"
              class:active={model.id === chatStore.selectedModel}
              onclick={() => select(model.id)}
            >
              <span class="option-dot" style="background: {model.color}"></span>
              <div class="option-info">
                <span class="option-name">{model.name}</span>
                <span class="option-desc">{model.description}</span>
              </div>
              {#if model.tier === 'paid'}
                <span class="tier-badge paid">Paid</span>
              {:else}
                <span class="tier-badge free">Free</span>
              {/if}
            </button>
          {/each}
        </div>
      {/each}
      <div class="footer">
        <label class="toggle">
          <input type="checkbox" checked={chatStore.allowPaid} onchange={(e) => chatStore.setAllowPaid((e.target as HTMLInputElement).checked)} />
          <span>Allow paid models</span>
        </label>
      </div>
    </div>
  {/if}
</div>

<style>
  .model-selector {
    position: relative;
  }

  .selector-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-primary);
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 12px;
    font-family: inherit;
    transition: all var(--transition-fast);
    width: 100%;
  }

  .selector-trigger:hover {
    border-color: var(--border-default);
    background: var(--bg-surface-hover);
  }

  .trigger-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .trigger-name {
    flex: 1;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .selector-dropdown {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    width: 240px;
    max-height: 320px;
    overflow-y: auto;
    border-radius: var(--radius-md);
    padding: 4px;
    z-index: 100;
    animation: dropIn 150ms cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes dropIn {
    from {
      opacity: 0;
      transform: translateY(-4px) scale(0.98);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .provider-group {
    padding: 2px 0;
  }

  .provider-group + .provider-group {
    border-top: 1px solid var(--border-subtle);
    margin-top: 2px;
    padding-top: 4px;
  }

  .provider-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    padding: 4px 8px 2px;
  }

  .model-option {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 7px 8px;
    border: none;
    background: transparent;
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    transition: background var(--transition-fast);
    position: relative;
  }

  .model-option:hover {
    background: var(--bg-surface-hover);
  }

  .model-option.active {
    background: var(--accent-subtle);
  }

  .option-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .option-info {
    display: flex;
    flex-direction: column;
    min-width: 0;
    flex: 1;
  }

  .option-name {
    font-size: 12px;
    color: var(--text-primary);
    font-weight: 500;
  }

  .option-desc {
    font-size: 10px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .tier-badge {
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 10px;
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
  }
  .tier-badge.free {
    background: rgba(16, 185, 129, 0.08);
    border-color: rgba(16, 185, 129, 0.25);
    color: #10b981;
  }
  .tier-badge.paid {
    background: rgba(59, 130, 246, 0.08);
    border-color: rgba(59, 130, 246, 0.25);
    color: #3b82f6;
  }

  .footer {
    margin-top: 6px;
    padding: 6px 8px 4px;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: var(--text-secondary);
  }
</style>
