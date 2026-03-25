import type { AIModel, Conversation, ChatMessage } from '$lib/types';

export const AVAILABLE_MODELS: AIModel[] = [
  // Free-first options
  { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', provider: 'groq', modelId: 'llama-3.3-70b-versatile', description: 'Fast open-source via Groq', maxTokens: 131072, color: '#f97316', tier: 'free' },
  { id: 'or-llama-8b-free', name: 'Llama 3.1 8B (OR Free)', provider: 'openrouter', modelId: 'meta-llama/llama-3.1-8b-instruct:free', description: 'OpenRouter free tier', maxTokens: 131072, color: '#6b7280', tier: 'free' },
  { id: 'or-gemma-9b-free', name: 'Gemma 2 9B (OR Free)', provider: 'openrouter', modelId: 'google/gemma-2-9b-it:free', description: 'OpenRouter free tier', maxTokens: 8192, color: '#6366f1', tier: 'free' },
  { id: 'or-mistral-7b-free', name: 'Mistral 7B (OR Free)', provider: 'openrouter', modelId: 'mistralai/mistral-7b-instruct:free', description: 'OpenRouter free tier', maxTokens: 32768, color: '#8b5cf6', tier: 'free' },

  // Paid fallbacks
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', modelId: 'gpt-4o', description: 'Most capable OpenAI model', maxTokens: 128000, color: '#10a37f', tier: 'paid' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', modelId: 'gpt-4o-mini', description: 'Fast and affordable', maxTokens: 128000, color: '#10a37f', tier: 'paid' },
  { id: 'or-gpt-4o-mini', name: 'GPT-4o Mini (OR)', provider: 'openrouter', modelId: 'openai/gpt-4o-mini', description: 'OpenRouter paid', maxTokens: 128000, color: '#0ea5e9', tier: 'paid' },
  { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', provider: 'anthropic', modelId: 'claude-sonnet-4-20250514', description: 'Balanced Claude model', maxTokens: 200000, color: '#d97706', tier: 'paid' },
  { id: 'claude-3.5-haiku', name: 'Claude 3.5 Haiku', provider: 'anthropic', modelId: 'claude-3-5-haiku-20241022', description: 'Fast Anthropic model', maxTokens: 200000, color: '#d97706', tier: 'paid' },
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', provider: 'google', modelId: 'gemini-2.5-flash-preview-05-20', description: 'Google multimodal', maxTokens: 1000000, color: '#4285f4', tier: 'paid' },
  { id: 'grok-3-mini', name: 'Grok 3 Mini', provider: 'xai', modelId: 'grok-3-mini', description: 'xAI reasoning model', maxTokens: 131072, color: '#ef4444', tier: 'paid' },
];

const STORAGE_KEY_CONVERSATIONS = 'elysium-conversations';
const STORAGE_KEY_MODEL = 'elysium-selected-model';
const STORAGE_KEY_ALLOW_PAID = 'elysium-allow-paid';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

class ChatStore {
  conversations = $state<Conversation[]>([]);
  activeConversationId = $state<string | null>(null);
  selectedModel = $state<string>('llama-3.3-70b');
  allowPaid = $state(false);
  initialized = $state(false);

  get activeConversation(): Conversation | null {
    return this.conversations.find(c => c.id === this.activeConversationId) ?? null;
  }

  constructor() {
    this.load();
  }

  createConversation(): string {
    const model = AVAILABLE_MODELS.find(m => m.id === this.selectedModel) ?? AVAILABLE_MODELS[0];
    const id = generateId();
    const conversation: Conversation = {
      id,
      title: 'New Chat',
      messages: [],
      model: this.selectedModel,
      systemPrompt: '',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.conversations.unshift(conversation);
    this.activeConversationId = id;
    this.save();
    return id;
  }

  deleteConversation(id: string) {
    const idx = this.conversations.findIndex(c => c.id === id);
    if (idx !== -1) {
      this.conversations.splice(idx, 1);
    }
    if (this.activeConversationId === id) {
      this.activeConversationId = this.conversations[0]?.id ?? null;
    }
    this.save();
  }

  setActive(id: string) {
    this.activeConversationId = id;
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      const modelInfo = AVAILABLE_MODELS.find(m => m.id === conv.model);
      if (!this.allowPaid && modelInfo && modelInfo.tier === 'paid') {
        const free = AVAILABLE_MODELS.find(m => m.tier === 'free');
        if (free) {
          conv.model = free.id;
          this.selectedModel = free.id;
          this.save();
          return;
        }
      }
      this.selectedModel = conv.model;
    }
  }

  setModel(modelId: string) {
    this.selectedModel = modelId;
    if (this.activeConversation) {
      this.activeConversation.model = modelId;
    }
    this.save();
  }

  setAllowPaid(allow: boolean) {
    this.allowPaid = allow;
    // Ensure a free model is selected when paid is disabled
    if (!this.allowPaid) {
      const current = AVAILABLE_MODELS.find(m => m.id === this.selectedModel);
      let fallback = current && current.tier === 'free' ? current : undefined;
      if (!fallback) fallback = AVAILABLE_MODELS.find(m => m.tier === 'free');
      if (fallback) {
        // Switch selected and active conversation to free
        this.selectedModel = fallback.id;
        if (this.activeConversation) {
          this.activeConversation.model = fallback.id;
        }
        // Migrate ALL conversations that are on paid models to the chosen free fallback
        for (const c of this.conversations) {
          const info = AVAILABLE_MODELS.find(m => m.id === c.model);
          if (!info || info.tier === 'paid') {
            c.model = fallback.id;
          }
        }
      }
    }
    this.save();
  }

  addMessage(conversationId: string, message: ChatMessage) {
    const conv = this.conversations.find(c => c.id === conversationId);
    if (!conv) return;
    conv.messages.push(message);
    conv.updatedAt = new Date();
    if (message.role === 'user' && conv.messages.filter(m => m.role === 'user').length === 1) {
      conv.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
    }
    this.save();
  }

  updateConversationTitle(id: string, title: string) {
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      conv.title = title;
      this.save();
    }
  }

  updateSystemPrompt(id: string, prompt: string) {
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      conv.systemPrompt = prompt;
      this.save();
    }
  }

  save() {
    if (typeof window === 'undefined') return;
    try {
      const data = this.conversations.map(c => ({
        ...c,
        createdAt: c.createdAt instanceof Date ? c.createdAt.toISOString() : c.createdAt,
        updatedAt: c.updatedAt instanceof Date ? c.updatedAt.toISOString() : c.updatedAt,
        messages: c.messages.map(m => ({
          ...m,
          createdAt: m.createdAt instanceof Date ? m.createdAt.toISOString() : m.createdAt,
        })),
      }));
      localStorage.setItem(STORAGE_KEY_CONVERSATIONS, JSON.stringify(data));
      localStorage.setItem(STORAGE_KEY_MODEL, this.selectedModel);
      localStorage.setItem(STORAGE_KEY_ALLOW_PAID, String(this.allowPaid));
    } catch {}
  }

  load() {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY_CONVERSATIONS);
      if (raw) {
        const parsed = JSON.parse(raw) as any[];
        this.conversations = parsed.map(c => ({
          ...c,
          createdAt: new Date(c.createdAt),
          updatedAt: new Date(c.updatedAt),
          messages: (c.messages ?? []).map((m: any) => ({
            ...m,
            createdAt: new Date(m.createdAt),
          })),
        }));
        if (this.conversations.length > 0) {
          this.activeConversationId = this.conversations[0].id;
        }
      }
      const model = localStorage.getItem(STORAGE_KEY_MODEL);
      if (model && AVAILABLE_MODELS.some(m => m.id === model)) {
        this.selectedModel = model;
      }
      const allow = localStorage.getItem(STORAGE_KEY_ALLOW_PAID);
      this.allowPaid = allow === 'true';
      if (!this.allowPaid) {
        const sel = AVAILABLE_MODELS.find(m => m.id === this.selectedModel);
        if (!sel || sel.tier === 'paid') {
          const free = AVAILABLE_MODELS.find(m => m.tier === 'free');
          if (free) {
            this.selectedModel = free.id;
            if (this.activeConversation) {
              this.activeConversation.model = free.id;
            }
          }
        }
      }
    } catch {}
    this.initialized = true;
  }
}

export const chatStore = new ChatStore();
