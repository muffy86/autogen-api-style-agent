import { ragStore } from '$lib/server/rag';
import { addFile, listFiles } from '$lib/server/files';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  const formData = await request.formData();
  const file = formData.get('file') as File;
  if (!file) {
    return new Response(JSON.stringify({ error: 'No file provided' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const allowedExtensions = ['.txt', '.md', '.json', '.csv', '.js', '.ts', '.py', '.html', '.css', '.xml', '.yaml', '.yml', '.toml', '.env', '.sh', '.sql', '.svelte'];
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!allowedExtensions.includes(ext)) {
    return new Response(JSON.stringify({ error: `Unsupported file type: ${ext}. Supported: ${allowedExtensions.join(', ')}` }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const id = `file-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const text = await file.text();

  addFile({
    id,
    name: file.name,
    type: file.type || 'text/plain',
    size: file.size,
    content: text,
    uploadedAt: new Date().toISOString(),
  });

  return new Response(JSON.stringify({
    id,
    name: file.name,
    size: file.size,
    type: file.type || 'text/plain',
    uploadedAt: new Date().toISOString(),
    chunkCount: ragStore.getChunkCount(id),
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const GET: RequestHandler = async () => {
  return new Response(JSON.stringify({ files: listFiles() }), {
    headers: { 'Content-Type': 'application/json' },
  });
};
