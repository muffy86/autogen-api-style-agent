import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createXai } from '@ai-sdk/xai';
import { createGroq } from '@ai-sdk/groq';
import { streamText } from 'ai';
import { elysiumTools } from '$lib/server/tools';
import { env } from '$env/dynamic/private';
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

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { messages, provider, modelId, systemPrompt } = await request.json();
    const model = getModel(provider, modelId);

    const result = streamText({
      model,
      messages,
      system: systemPrompt || `You are Elysium, a helpful AI assistant running inside Elysium AI OS.

You have access to these tools:
- **calculator**: Evaluate math expressions
- **webSearch**: Search the web for current information
- **urlFetch**: Fetch and read web page content

Use tools proactively when they would help answer the user's question. You can chain multiple tool calls.`,
      tools: elysiumTools,
      maxSteps: 5,
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
    return new Response(JSON.stringify({ error: message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
