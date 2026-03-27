import { ragStore } from '$lib/server/rag';
import { addFile, listFiles } from '$lib/server/files';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid form data' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const field = formData.get('file');

  if (field === null || field === undefined) {
    return new Response(JSON.stringify({ error: 'No file field provided' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (!(field instanceof File)) {
    return new Response(JSON.stringify({ error: 'Invalid file field: expected a File upload' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (field.size === 0) {
    return new Response(JSON.stringify({ error: 'File is empty' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const file = field;
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
