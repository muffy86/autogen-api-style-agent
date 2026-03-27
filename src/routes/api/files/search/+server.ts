import { ragStore } from '$lib/server/rag';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
  const query = url.searchParams.get('q') ?? '';
  if (!query.trim()) {
    return new Response(JSON.stringify({ results: [] }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const results = ragStore.search(query, 5);
  return new Response(JSON.stringify({ results, query }), {
    headers: { 'Content-Type': 'application/json' },
  });
};
