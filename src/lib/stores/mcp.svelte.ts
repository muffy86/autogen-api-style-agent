interface MCPServer {
  id: string;
  name: string;
  url: string;
  description: string;
  enabled: boolean;
  status: 'unknown' | 'connected' | 'error';
}

const STORAGE_KEY = 'elysium-mcp-servers';

class MCPStore {
  servers = $state<MCPServer[]>([]);

  constructor() {
    this.load();
  }

  addServer(name: string, url: string, description = '') {
    const id = `mcp-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    this.servers.push({
      id,
      name,
      url,
      description,
      enabled: true,
      status: 'unknown',
    });
    this.save();
    return id;
  }

  removeServer(id: string) {
    this.servers = this.servers.filter(s => s.id !== id);
    this.save();
  }

  toggleServer(id: string) {
    const server = this.servers.find(s => s.id === id);
    if (server) {
      server.enabled = !server.enabled;
      this.save();
    }
  }

  async testConnection(id: string): Promise<boolean> {
    const server = this.servers.find(s => s.id === id);
    if (!server) return false;
    try {
      const res = await fetch(server.url, {
        method: 'HEAD',
        mode: 'no-cors',
        signal: AbortSignal.timeout(5000),
      });
      server.status = 'connected';
    } catch {
      server.status = 'error';
    }
    this.save();
    return server.status === 'connected';
  }

  private save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.servers));
    } catch {}
  }

  private load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        this.servers = JSON.parse(raw);
      }
    } catch {}
  }
}

export const mcpStore = new MCPStore();
