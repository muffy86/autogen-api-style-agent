import type { AIModel, Conversation, ChatMessage } from '$lib/types';

export const AVAILABLE_MODELS: AIModel[] = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', modelId: 'gpt-4o', description: 'Most capable OpenAI model', maxTokens: 128000, color: '#10a37f' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', modelId: 'gpt-4o-mini', description: 'Fast and affordable', maxTokens: 128000, color: '#10a37f' },
  { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', provider: 'anthropic', modelId: 'claude-sonnet-4-20250514', description: 'Balanced Claude model', maxTokens: 200000, color: '#d97706' },
  { id: 'claude-3.5-haiku', name: 'Claude 3.5 Haiku', provider: 'anthropic', modelId: 'claude-3-5-haiku-20241022', description: 'Fast Anthropic model', maxTokens: 200000, color: '#d97706' },
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', provider: 'google', modelId: 'gemini-2.5-flash-preview-05-20', description: 'Google multimodal', maxTokens: 1000000, color: '#4285f4' },
  { id: 'grok-3-mini', name: 'Grok 3 Mini', provider: 'xai', modelId: 'grok-3-mini', description: 'xAI reasoning model', maxTokens: 131072, color: '#ef4444' },
  { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', provider: 'groq', modelId: 'llama-3.3-70b-versatile', description: 'Fast open-source via Groq', maxTokens: 131072, color: '#f97316' },
];

const STORAGE_KEY_CONVERSATIONS = 'elysium-conversations';
const STORAGE_KEY_MODEL = 'elysium-selected-model';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

class ChatStore {
  conversations = $state<Conversation[]>([]);
  activeConversationId = $state<string | null>(null);
  selectedModel = $state<string>('gpt-4o');
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
    } catch {}
    this.initialized = true;
  }
}

export const chatStore = new ChatStore();
