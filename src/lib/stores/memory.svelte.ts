interface MemoryEntry {
  id: string;
  content: string;
  source: string;
  createdAt: string;
  importance: number;
}

const STORAGE_KEY = 'elysium-memory';
const MAX_MEMORIES = 50;

class MemoryStore {
  memories = $state<MemoryEntry[]>([]);
  enabled = $state(true);

  constructor() {
    this.load();
  }

  add(content: string, source: string, importance = 3) {
    const id = `mem-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    this.memories.push({ id, content, source, createdAt: new Date().toISOString(), importance });
    if (this.memories.length > MAX_MEMORIES) {
      this.memories.sort((a, b) => b.importance - a.importance);
      this.memories = this.memories.slice(0, MAX_MEMORIES);
    }
    this.save();
  }

  remove(id: string) {
    this.memories = this.memories.filter(m => m.id !== id);
    this.save();
  }

  clear() {
    this.memories = [];
    this.save();
  }

  toggleEnabled() {
    this.enabled = !this.enabled;
    this.save();
  }

  getRelevantContext(): string {
    if (!this.enabled || this.memories.length === 0) return '';
    const sorted = [...this.memories].sort((a, b) => b.importance - a.importance);
    const top = sorted.slice(0, 10);
    return '\n\n<user_memory>\nThings you remember about this user:\n' +
      top.map(m => `- ${m.content}`).join('\n') +
      '\n</user_memory>';
  }

  private save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        memories: this.memories,
        enabled: this.enabled,
      }));
    } catch {}
  }

  private load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data = JSON.parse(raw);
        this.memories = data.memories ?? [];
        this.enabled = data.enabled ?? true;
      }
    } catch {}
  }
}

export const memoryStore = new MemoryStore();
