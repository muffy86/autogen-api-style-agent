import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  favicon?: string;
}

async function searchWithTavily(query: string): Promise<{ results: SearchResult[]; provider: string }> {
  const res = await fetch('https://api.tavily.com/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      api_key: env.TAVILY_API_KEY,
      query,
      max_results: 6,
      include_answer: false,
    }),
  });
  if (!res.ok) throw new Error('Tavily search failed');
  const data = await res.json();
  return {
    provider: 'tavily',
    results: (data.results ?? []).map((r: any) => ({
      title: r.title ?? '',
      url: r.url ?? '',
      snippet: r.content ?? '',
      favicon: `https://www.google.com/s2/favicons?domain=${new URL(r.url).hostname}&sz=32`,
    })),
  };
}

async function searchWithSerper(query: string): Promise<{ results: SearchResult[]; provider: string }> {
  const res = await fetch('https://google.serper.dev/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-KEY': env.SERPER_API_KEY!,
    },
    body: JSON.stringify({ q: query, num: 6 }),
  });
  if (!res.ok) throw new Error('Serper search failed');
  const data = await res.json();
  return {
    provider: 'serper',
    results: (data.organic ?? []).map((r: any) => ({
      title: r.title ?? '',
      url: r.link ?? '',
      snippet: r.snippet ?? '',
      favicon: `https://www.google.com/s2/favicons?domain=${new URL(r.link).hostname}&sz=32`,
    })),
  };
}

async function searchWithBrave(query: string): Promise<{ results: SearchResult[]; provider: string }> {
  const res = await fetch(`https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=6`, {
    headers: {
      Accept: 'application/json',
      'Accept-Encoding': 'gzip',
      'X-Subscription-Token': env.BRAVE_SEARCH_API_KEY!,
    },
  });
  if (!res.ok) throw new Error('Brave search failed');
  const data = await res.json();
  return {
    provider: 'brave',
    results: (data.web?.results ?? []).map((r: any) => ({
      title: r.title ?? '',
      url: r.url ?? '',
      snippet: r.description ?? '',
      favicon: r.profile?.img ?? `https://www.google.com/s2/favicons?domain=${new URL(r.url).hostname}&sz=32`,
    })),
  };
}

function getMockResults(query: string): { results: SearchResult[]; provider: string } {
  return {
    provider: 'mock',
    results: [
      {
        title: `Search results for "${query}"`,
        url: `https://example.com/search?q=${encodeURIComponent(query)}`,
        snippet: 'No search API is configured. Set TAVILY_API_KEY, SERPER_API_KEY, or BRAVE_SEARCH_API_KEY in your environment to enable live web search.',
        favicon: 'https://www.google.com/s2/favicons?domain=example.com&sz=32',
      },
    ],
  };
}

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { query } = await request.json();
    if (!query || typeof query !== 'string') {
      return json({ results: [], query: '', provider: 'none' }, { status: 400 });
    }

    if (env.TAVILY_API_KEY) {
      const data = await searchWithTavily(query);
      return json({ ...data, query });
    }

    if (env.SERPER_API_KEY) {
      const data = await searchWithSerper(query);
      return json({ ...data, query });
    }

    if (env.BRAVE_SEARCH_API_KEY) {
      const data = await searchWithBrave(query);
      return json({ ...data, query });
    }

    return json({ ...getMockResults(query), query });
  } catch (err: any) {
    return json(
      { results: [], query: '', provider: 'error', error: err?.message ?? 'Search failed' },
      { status: 500 }
    );
  }
};
