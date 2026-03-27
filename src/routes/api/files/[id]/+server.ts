import { ragStore } from '$lib/server/rag';
import { getFile, removeFile } from '$lib/server/files';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params }) => {
  const file = getFile(params.id);
  if (!file) {
    return new Response(JSON.stringify({ error: 'File not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  return new Response(JSON.stringify({
    id: file.id,
    name: file.name,
    size: file.size,
    type: file.type,
    content: file.content,
    uploadedAt: file.uploadedAt,
    chunkCount: ragStore.getChunkCount(file.id),
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
};

export const DELETE: RequestHandler = async ({ params }) => {
  const file = getFile(params.id);
  if (!file) {
    return new Response(JSON.stringify({ error: 'File not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  removeFile(params.id);

  return new Response(JSON.stringify({ deleted: true, id: params.id }), {
    headers: { 'Content-Type': 'application/json' },
  });
};
