import type { AIModel, Conversation, ChatMessage } from '$lib/types';
import type { SupabaseClient } from '@supabase/supabase-js';

export const AVAILABLE_MODELS: AIModel[] = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'openai', modelId: 'gpt-4o', description: 'Most capable OpenAI model', maxTokens: 128000, color: '#10a37f' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'openai', modelId: 'gpt-4o-mini', description: 'Fast and affordable', maxTokens: 128000, color: '#10a37f' },
  { id: 'claude-4-sonnet', name: 'Claude 4 Sonnet', provider: 'anthropic', modelId: 'claude-sonnet-4-20250514', description: 'Balanced Claude model', maxTokens: 200000, color: '#d97706' },
  { id: 'claude-3.5-haiku', name: 'Claude 3.5 Haiku', provider: 'anthropic', modelId: 'claude-3-5-haiku-20241022', description: 'Fast Anthropic model', maxTokens: 200000, color: '#d97706' },
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', provider: 'google', modelId: 'gemini-2.5-flash-preview-05-20', description: 'Google multimodal', maxTokens: 1000000, color: '#4285f4' },
  { id: 'grok-3-mini', name: 'Grok 3 Mini', provider: 'xai', modelId: 'grok-3-mini', description: 'xAI reasoning model', maxTokens: 131072, color: '#ef4444' },
  { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', provider: 'groq', modelId: 'llama-3.3-70b-versatile', description: 'Fast open-source via Groq', maxTokens: 131072, color: '#f97316' },
];

const STORAGE_KEY_MODEL = 'elysium-selected-model';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

class ChatStore {
  conversations = $state<Conversation[]>([]);
  activeConversationId = $state<string | null>(null);
  selectedModel = $state<string>('gpt-4o');
  initialized = $state(false);
  loading = $state(false);

  private supabase: SupabaseClient | null = null;

  get activeConversation(): Conversation | null {
    return this.conversations.find(c => c.id === this.activeConversationId) ?? null;
  }

  constructor() {
    if (typeof window !== 'undefined') {
      try {
        const model = localStorage.getItem(STORAGE_KEY_MODEL);
        if (model && AVAILABLE_MODELS.some(m => m.id === model)) {
          this.selectedModel = model;
        }
      } catch {}
    }
  }

  async init(supabase: SupabaseClient) {
    if (this.initialized && this.supabase === supabase) return;
    this.supabase = supabase;
    this.loading = true;

    try {
      const { data: convRows, error: convError } = await supabase
        .from('conversations')
        .select('*')
        .order('updated_at', { ascending: false });

      if (convError) {
        console.error('Failed to load conversations:', convError.message);
        this.initialized = true;
        this.loading = false;
        return;
      }

      const conversations: Conversation[] = [];

      if (convRows && convRows.length > 0) {
        const convIds = convRows.map(c => c.id);
        const { data: msgRows, error: msgError } = await supabase
          .from('messages')
          .select('*')
          .in('conversation_id', convIds)
          .order('created_at', { ascending: true });

        if (msgError) {
          console.error('Failed to load messages:', msgError.message);
        }

        const messagesByConv = new Map<string, ChatMessage[]>();
        if (msgRows) {
          for (const m of msgRows) {
            const list = messagesByConv.get(m.conversation_id) ?? [];
            list.push({
              id: m.id,
              role: m.role as 'user' | 'assistant' | 'system',
              content: m.content,
              model: m.model ?? undefined,
              createdAt: new Date(m.created_at),
            });
            messagesByConv.set(m.conversation_id, list);
          }
        }

        for (const row of convRows) {
          conversations.push({
            id: row.id,
            title: row.title,
            messages: messagesByConv.get(row.id) ?? [],
            model: row.model,
            systemPrompt: row.system_prompt ?? '',
            createdAt: new Date(row.created_at),
            updatedAt: new Date(row.updated_at),
          });
        }
      }

      this.conversations = conversations;
      if (this.conversations.length > 0) {
        this.activeConversationId = this.conversations[0].id;
      }
    } catch (err) {
      console.error('Failed to initialize chat store:', err);
    }

    this.initialized = true;
    this.loading = false;
  }

  createConversation(): string {
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

    if (this.supabase) {
      this.supabase
        .from('conversations')
        .insert({
          id,
          user_id: undefined,
          title: 'New Chat',
          model: this.selectedModel,
          system_prompt: '',
        })
        .then(async ({ error }) => {
          if (error) {
            if (error.message?.includes('user_id')) {
              const { data: { user } } = await this.supabase!.auth.getUser();
              if (user) {
                const { error: retryError } = await this.supabase!
                  .from('conversations')
                  .insert({
                    id,
                    user_id: user.id,
                    title: 'New Chat',
                    model: this.selectedModel,
                    system_prompt: '',
                  });
                if (retryError) {
                  console.error('Failed to create conversation:', retryError.message);
                }
              }
            } else {
              console.error('Failed to create conversation:', error.message);
            }
          }
        });
    }

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

    if (this.supabase) {
      this.supabase
        .from('conversations')
        .delete()
        .eq('id', id)
        .then(({ error }) => {
          if (error) console.error('Failed to delete conversation:', error.message);
        });
    }
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

      if (this.supabase) {
        this.supabase
          .from('conversations')
          .update({ model: modelId })
          .eq('id', this.activeConversation.id)
          .then(({ error }) => {
            if (error) console.error('Failed to update model:', error.message);
          });
      }
    }

    try {
      localStorage.setItem(STORAGE_KEY_MODEL, modelId);
    } catch {}
  }

  addMessage(conversationId: string, message: ChatMessage) {
    const conv = this.conversations.find(c => c.id === conversationId);
    if (!conv) return;
    conv.messages.push(message);
    conv.updatedAt = new Date();

    let titleUpdated = false;
    if (message.role === 'user' && conv.messages.filter(m => m.role === 'user').length === 1) {
      conv.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
      titleUpdated = true;
    }

    if (this.supabase) {
      this.supabase
        .from('messages')
        .insert({
          id: message.id,
          conversation_id: conversationId,
          role: message.role,
          content: message.content,
          model: message.model ?? null,
        })
        .then(({ error }) => {
          if (error) console.error('Failed to save message:', error.message);
        });

      if (titleUpdated) {
        this.supabase
          .from('conversations')
          .update({ title: conv.title })
          .eq('id', conversationId)
          .then(({ error }) => {
            if (error) console.error('Failed to update title:', error.message);
          });
      }
    }
  }

  updateConversationTitle(id: string, title: string) {
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      conv.title = title;

      if (this.supabase) {
        this.supabase
          .from('conversations')
          .update({ title })
          .eq('id', id)
          .then(({ error }) => {
            if (error) console.error('Failed to update title:', error.message);
          });
      }
    }
  }

  updateSystemPrompt(id: string, prompt: string) {
    const conv = this.conversations.find(c => c.id === id);
    if (conv) {
      conv.systemPrompt = prompt;

      if (this.supabase) {
        this.supabase
          .from('conversations')
          .update({ system_prompt: prompt })
          .eq('id', id)
          .then(({ error }) => {
            if (error) console.error('Failed to update system prompt:', error.message);
          });
      }
    }
  }
}

export const chatStore = new ChatStore();
