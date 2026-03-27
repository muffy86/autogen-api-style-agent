import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createXai } from '@ai-sdk/xai';
import { createGroq } from '@ai-sdk/groq';
import { streamText } from 'ai';
import { elysiumTools } from '$lib/server/tools';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

interface AttachmentPayload {
  name: string;
  type: string;
  mimeType: string;
  content?: string;
  dataUrl?: string;
}

function getModel(provider: string, modelId: string) {
  switch (provider) {
    case 'openai': {
      const key = env.OPENAI_API_KEY;
      if (!key) throw new Error('OPENAI_API_KEY not configured');
      const baseURL = env.OPENAI_BASE_URL;
      return createOpenAI({ apiKey: key, ...(baseURL ? { baseURL } : {}) })(modelId);
    }
    case 'openrouter': {
      const key = env.OPENROUTER_API_KEY ?? env.OPENAI_API_KEY;
      if (!key) throw new Error('OPENROUTER_API_KEY or OPENAI_API_KEY not configured');
      const baseURL = env.OPENROUTER_BASE_URL ?? 'https://openrouter.ai/api/v1';
      return createOpenAI({ apiKey: key, baseURL })(modelId);
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

function buildTextFilePrompt(attachments: AttachmentPayload[]): string {
  const textFiles = attachments.filter(a => a.content);
  const otherFiles = attachments.filter(a => !a.content && !a.dataUrl);
  if (textFiles.length === 0 && otherFiles.length === 0) return '';

  const parts: string[] = [];
  for (const f of textFiles) {
    parts.push(`[File: ${f.name}]\n\`\`\`\n${f.content}\n\`\`\``);
  }
  for (const f of otherFiles) {
    parts.push(`[Attached: ${f.name} (${f.mimeType})]`);
  }
  return '\n\nThe user has attached the following files:\n' + parts.join('\n\n');
}

function injectImageAttachments(messages: any[], attachments: AttachmentPayload[]): any[] {
  const imageAtts = attachments.filter(a => a.dataUrl && a.mimeType.startsWith('image/'));
  if (imageAtts.length === 0) return messages;

  let lastUserIdx = -1;
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === 'user') {
      lastUserIdx = i;
      break;
    }
  }
  if (lastUserIdx === -1) return messages;

  const result = messages.map((msg, i) => {
    if (i !== lastUserIdx) return msg;

    const existingContent = msg.content;
    const contentParts: any[] = [];

    if (typeof existingContent === 'string') {
      contentParts.push({ type: 'text', text: existingContent });
    } else if (Array.isArray(existingContent)) {
      contentParts.push(...existingContent);
    }

    for (const img of imageAtts) {
      contentParts.push({ type: 'image', image: img.dataUrl });
    }

    return { ...msg, content: contentParts };
  });

  return result;
}

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { messages, provider, modelId, systemPrompt, memoryContext, attachments } = await request.json();
    const model = getModel(provider, modelId);

    const basePrompt = systemPrompt || `You are Elysium, a helpful AI assistant running inside Elysium AI OS.

You have access to these tools:
- **calculator**: Evaluate math expressions
- **webSearch**: Search the web for current information
- **urlFetch**: Fetch and read web page content
- **codeExec**: Execute JavaScript code snippets
- **knowledgeSearch**: Search through uploaded documents in the Knowledge Base
- **saveMemory**: Save important facts or preferences about the user for future conversations

Use tools proactively when they would help answer the user's question. You can chain multiple tool calls.
When the user shares personal preferences or important facts, use saveMemory to remember them.
When the user asks about their documents or uploaded files, use knowledgeSearch to find relevant information.`;

    const filePrompt = attachments?.length ? buildTextFilePrompt(attachments) : '';
    const processedMessages = attachments?.length ? injectImageAttachments(messages, attachments) : messages;

    const result = streamText({
      model,
      messages: processedMessages,
      system: basePrompt + filePrompt + (memoryContext || ''),
      tools: elysiumTools,
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
