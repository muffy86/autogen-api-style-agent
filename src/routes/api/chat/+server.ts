import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createXai } from '@ai-sdk/xai';
import { createGroq } from '@ai-sdk/groq';
import { streamText } from 'ai';
import { env } from '$env/dynamic/private';
import { checkRateLimit } from '$lib/server/rate-limit';
import { validateChatRequest } from '$lib/server/validate-chat';
import { getGitHubContext } from '$lib/server/github-context';
import type { RequestHandler } from './$types';

function getModel(provider: string, modelId: string) {
  switch (provider) {
    case 'openai': {
      const key = env.OPENAI_API_KEY;
      if (!key) throw new Error('OPENAI_API_KEY not configured');
      return createOpenAI({ apiKey: key })(modelId);
    }
    case 'anthropic': {
      const key = env.ANTHROPIC_API_KEY;
      if (!key) throw new Error('ANTHROPIC_API_KEY not configured');
      return createAnthropic({ apiKey: key })(modelId);
    }
    case 'google': {
      const key = env.GOOGLE_GENERATIVE_AI_API_KEY;
      if (!key) throw new Error('GOOGLE_GENERATIVE_AI_API_KEY not configured');
      return createGoogleGenerativeAI({ apiKey: key })(modelId);
    }
    case 'xai': {
      const key = env.XAI_API_KEY;
      if (!key) throw new Error('XAI_API_KEY not configured');
      return createXai({ apiKey: key })(modelId);
    }
    case 'groq': {
      const key = env.GROQ_API_KEY;
      if (!key) throw new Error('GROQ_API_KEY not configured');
      return createGroq({ apiKey: key })(modelId);
    }
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.session || !locals.user) {
    return new Response(JSON.stringify({ error: 'Authentication required' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const rateLimit = checkRateLimit(locals.user.id);
  if (!rateLimit.allowed) {
    return new Response(JSON.stringify({
      error: 'Rate limit exceeded. Please wait before sending more messages.',
      retryAfterMs: rateLimit.resetMs,
    }), {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        'Retry-After': Math.ceil(rateLimit.resetMs / 1000).toString(),
      },
    });
  }

  try {
    const body = await request.json();
    const validation = validateChatRequest(body);
    if (!validation.valid) {
      return new Response(JSON.stringify({ error: validation.error }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { messages, provider, modelId, systemPrompt } = validation.data;

    let enhancedSystemPrompt = systemPrompt || 'You are Elysium, a helpful AI assistant running inside Elysium AI OS.';

    const lastUserMessage = messages.filter((m: any) => m.role === 'user').pop()?.content?.toLowerCase() || '';
    const githubKeywords = ['github', 'repo', 'repository', 'issue', 'pull request', 'pr', 'commit', 'branch'];
    const isGitHubQuery = githubKeywords.some(kw => lastUserMessage.includes(kw));

    if (isGitHubQuery) {
      const { data: ghIntegration } = await locals.supabase
        .from('integrations')
        .select('access_token')
        .eq('user_id', locals.user.id)
        .eq('provider', 'github')
        .single();

      if (ghIntegration) {
        const context = await getGitHubContext(ghIntegration.access_token);
        if (context) {
          enhancedSystemPrompt += context;
        }
      }
    }

    const model = getModel(provider, modelId);
    const result = streamText({
      model,
      messages,
      system: enhancedSystemPrompt,
      maxOutputTokens: 4096,
    });

    return result.toUIMessageStreamResponse();
  } catch (err: any) {
    const message = err?.message ?? 'Unknown error';
    if (message.includes('not configured')) {
      return new Response(JSON.stringify({ error: message }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    console.error('Chat API error:', err);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
