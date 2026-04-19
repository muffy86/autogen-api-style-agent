const STORAGE_KEY = 'elysium-api-keys';

interface ProviderKey {
  provider: string;
  label: string;
  model: string;
  key: string;
}

const PROVIDERS: Omit<ProviderKey, 'key'>[] = [
  { provider: 'openai', label: 'OpenAI', model: 'gpt-4o' },
  { provider: 'anthropic', label: 'Anthropic', model: 'claude-sonnet-4' },
  { provider: 'google', label: 'Google Gemini', model: 'gemini-2.0-flash' },
  { provider: 'xai', label: 'xAI (Grok)', model: 'grok-3' },
  { provider: 'groq', label: 'Groq', model: 'llama-3.3-70b' },
  { provider: 'together', label: 'Together.ai', model: 'Meta-Llama-3.1-70B' },
  { provider: 'openrouter', label: 'OpenRouter', model: 'anthropic/claude-sonnet-4' },
  { provider: 'mistral', label: 'Mistral', model: 'mistral-large-latest' },
  { provider: 'moonshot', label: 'Kimi (Moonshot)', model: 'kimi-k2.5' },
];

class ApiKeyStore {
  keys = $state<Record<string, string>>({});

  get providers() {
    return PROVIDERS;
  }

  constructor() {
    this.load();
  }

  getKey(provider: string): string {
    return this.keys[provider] ?? '';
  }

  setKey(provider: string, key: string) {
    if (key.trim()) {
      this.keys[provider] = key.trim();
    } else {
      delete this.keys[provider];
      this.keys = { ...this.keys };
    }
    this.save();
  }

  isConfigured(provider: string): boolean {
    return !!this.keys[provider];
  }

  get configuredCount(): number {
    return Object.values(this.keys).filter(Boolean).length;
  }

  maskKey(key: string): string {
    if (!key || key.length <= 8) return key ? '••••••••' : '';
    return key.slice(0, 4) + '••••••••' + key.slice(-4);
  }

  private save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.keys));
    } catch {}
  }

  private load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        this.keys = JSON.parse(raw);
      }
    } catch {}
  }
}

export const apiKeyStore = new ApiKeyStore();
