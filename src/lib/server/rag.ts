interface DocumentChunk {
  id: string;
  fileId: string;
  fileName: string;
  content: string;
  vector: number[];
}

class RAGStore {
  chunks: DocumentChunk[] = [];
  vocabulary: Map<string, number> = new Map();
  idfCache: Map<string, number> = new Map();

  addDocument(fileId: string, fileName: string, content: string) {
    const chunkSize = 500;
    const overlap = 100;
    const chunks: string[] = [];

    for (let i = 0; i < content.length; i += chunkSize - overlap) {
      const chunk = content.slice(i, i + chunkSize).trim();
      if (chunk.length > 20) {
        chunks.push(chunk);
      }
    }

    if (chunks.length === 0 && content.trim().length > 0) {
      chunks.push(content.trim());
    }

    this.chunks = this.chunks.filter(c => c.fileId !== fileId);
    this.rebuildVocabulary();

    for (const chunk of chunks) {
      this.addToVocabulary(chunk);
    }
    this.computeIdf();

    for (const chunk of this.chunks) {
      chunk.vector = this.computeTfIdf(chunk.content);
    }

    for (const chunk of chunks) {
      this.chunks.push({
        id: `chunk-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        fileId,
        fileName,
        content: chunk,
        vector: this.computeTfIdf(chunk),
      });
    }
  }

  removeDocument(fileId: string) {
    this.chunks = this.chunks.filter(c => c.fileId !== fileId);
    this.rebuildVocabulary();
    this.computeIdf();
    for (const chunk of this.chunks) {
      chunk.vector = this.computeTfIdf(chunk.content);
    }
  }

  getChunkCount(fileId: string): number {
    return this.chunks.filter(c => c.fileId === fileId).length;
  }

  search(query: string, topK = 3): { content: string; fileName: string; score: number }[] {
    if (this.chunks.length === 0) return [];

    this.addToVocabulary(query);
    this.computeIdf();
    const queryVector = this.computeTfIdf(query);

    const scored = this.chunks.map(chunk => ({
      content: chunk.content,
      fileName: chunk.fileName,
      score: this.cosineSimilarity(queryVector, chunk.vector),
    }));

    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)
      .filter(r => r.score > 0.05);
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(t => t.length > 1);
  }

  private addToVocabulary(text: string) {
    const tokens = this.tokenize(text);
    for (const token of tokens) {
      if (!this.vocabulary.has(token)) {
        this.vocabulary.set(token, this.vocabulary.size);
      }
    }
  }

  private rebuildVocabulary() {
    this.vocabulary.clear();
    this.idfCache.clear();
    for (const chunk of this.chunks) {
      this.addToVocabulary(chunk.content);
    }
  }

  private computeIdf() {
    this.idfCache.clear();
    const n = this.chunks.length || 1;
    const docFreq = new Map<string, number>();

    for (const chunk of this.chunks) {
      const uniqueTokens = new Set(this.tokenize(chunk.content));
      for (const token of uniqueTokens) {
        docFreq.set(token, (docFreq.get(token) || 0) + 1);
      }
    }

    for (const [token, freq] of docFreq) {
      this.idfCache.set(token, Math.log((n + 1) / (freq + 1)) + 1);
    }
  }

  private computeTfIdf(text: string): number[] {
    const tokens = this.tokenize(text);
    const tf = new Map<string, number>();
    const totalTokens = tokens.length || 1;

    for (const token of tokens) {
      tf.set(token, (tf.get(token) || 0) + 1);
    }

    const vector = new Array(this.vocabulary.size).fill(0);
    for (const [token, count] of tf) {
      const idx = this.vocabulary.get(token);
      if (idx !== undefined) {
        const termFreq = count / totalTokens;
        const idf = this.idfCache.get(token) || 1;
        vector[idx] = termFreq * idf;
      }
    }

    return vector;
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const len = Math.max(a.length, b.length);
    let dot = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < len; i++) {
      const va = a[i] || 0;
      const vb = b[i] || 0;
      dot += va * vb;
      normA += va * va;
      normB += vb * vb;
    }

    const denom = Math.sqrt(normA) * Math.sqrt(normB);
    return denom === 0 ? 0 : dot / denom;
  }
}

export const ragStore = new RAGStore();
