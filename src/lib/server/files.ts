import { ragStore } from '$lib/server/rag';

interface StoredFile {
  id: string;
  name: string;
  type: string;
  size: number;
  content: string;
  uploadedAt: string;
}

export const fileStore = new Map<string, StoredFile>();

export function addFile(file: StoredFile) {
  fileStore.set(file.id, file);
  ragStore.addDocument(file.id, file.name, file.content);
}

export function removeFile(id: string) {
  fileStore.delete(id);
  ragStore.removeDocument(id);
}

export function getFile(id: string) {
  return fileStore.get(id);
}

export function listFiles() {
  return Array.from(fileStore.values()).map(f => ({
    id: f.id,
    name: f.name,
    size: f.size,
    type: f.type,
    uploadedAt: f.uploadedAt,
    chunkCount: ragStore.getChunkCount(f.id),
  }));
}

export type { StoredFile };
