import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { messages } = await request.json();
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return json({ suggestions: [] });
    }

    const last6 = messages.slice(-6);
    const conversationContext = last6
      .map((m: any) => `${m.role}: ${(m.content ?? '').slice(0, 300)}`)
      .join('\n');

    const systemPrompt =
      'Based on this conversation, suggest 3 natural follow-up questions the user might ask. Return only the questions, one per line, no numbering or bullet points. Keep each under 80 characters.';

    let apiKey: string | undefined;
    let apiUrl: string;
    let body: any;

    if (env.GROQ_API_KEY) {
      apiKey = env.GROQ_API_KEY;
      apiUrl = 'https://api.groq.com/openai/v1/chat/completions';
      body = {
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: conversationContext },
        ],
        max_tokens: 200,
        temperature: 0.7,
      };
    } else if (env.OPENAI_API_KEY) {
      apiKey = env.OPENAI_API_KEY;
      apiUrl = 'https://api.openai.com/v1/chat/completions';
      body = {
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: conversationContext },
        ],
        max_tokens: 200,
        temperature: 0.7,
      };
    } else {
      return json({ suggestions: [] });
    }

    const res = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      return json({ suggestions: [] });
    }

    const data = await res.json();
    const text = data.choices?.[0]?.message?.content ?? '';
    const suggestions = text
      .split('\n')
      .map((s: string) => s.trim())
      .filter((s: string) => s.length > 5 && s.length < 120)
      .slice(0, 4);

    return json({ suggestions });
  } catch {
    return json({ suggestions: [] });
  }
};
