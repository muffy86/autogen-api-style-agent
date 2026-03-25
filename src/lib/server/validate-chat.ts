const VALID_MODELS: Record<string, string[]> = {
  openai: ['gpt-4o', 'gpt-4o-mini'],
  anthropic: ['claude-sonnet-4-20250514', 'claude-3-5-haiku-20241022'],
  google: ['gemini-2.5-flash-preview-05-20'],
  xai: ['grok-3-mini'],
  groq: ['llama-3.3-70b-versatile'],
};

const MAX_MESSAGES = 100;
const MAX_MESSAGE_LENGTH = 32000;
const MAX_SYSTEM_PROMPT_LENGTH = 4000;

export interface ChatRequestBody {
  messages: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>;
  provider: string;
  modelId: string;
  systemPrompt?: string;
}

export function validateChatRequest(body: unknown): { valid: true; data: ChatRequestBody } | { valid: false; error: string } {
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Invalid request body' };
  }

  const { messages, provider, modelId, systemPrompt } = body as any;

  if (!provider || typeof provider !== 'string' || !VALID_MODELS[provider]) {
    return { valid: false, error: `Invalid provider. Must be one of: ${Object.keys(VALID_MODELS).join(', ')}` };
  }

  if (!modelId || typeof modelId !== 'string' || !VALID_MODELS[provider].includes(modelId)) {
    return { valid: false, error: `Invalid model for provider ${provider}. Must be one of: ${VALID_MODELS[provider].join(', ')}` };
  }

  if (!Array.isArray(messages) || messages.length === 0) {
    return { valid: false, error: 'Messages must be a non-empty array' };
  }

  if (messages.length > MAX_MESSAGES) {
    return { valid: false, error: `Too many messages (max ${MAX_MESSAGES})` };
  }

  for (const msg of messages) {
    if (!msg || typeof msg !== 'object' || Array.isArray(msg)) {
      return { valid: false, error: 'Each message must be an object with role and content' };
    }
    if (!msg.role || !['user', 'assistant', 'system'].includes(msg.role)) {
      return { valid: false, error: 'Each message must have a valid role (user, assistant, system)' };
    }
    if (typeof msg.content !== 'string') {
      return { valid: false, error: 'Each message content must be a string' };
    }
    if (msg.content.length > MAX_MESSAGE_LENGTH) {
      return { valid: false, error: `Message content too long (max ${MAX_MESSAGE_LENGTH} chars)` };
    }
  }

  if (systemPrompt !== undefined && systemPrompt !== null) {
    if (typeof systemPrompt !== 'string') {
      return { valid: false, error: 'System prompt must be a string' };
    }
    if (systemPrompt.length > MAX_SYSTEM_PROMPT_LENGTH) {
      return { valid: false, error: `System prompt too long (max ${MAX_SYSTEM_PROMPT_LENGTH} chars)` };
    }
  }

  return {
    valid: true,
    data: { messages, provider, modelId, systemPrompt: systemPrompt || undefined },
  };
}
