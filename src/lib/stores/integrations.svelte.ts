import type { SupabaseClient } from '@supabase/supabase-js';

export interface Integration {
  provider: string;
  username: string;
  avatar_url: string;
  connected: boolean;
}

class IntegrationsStore {
  integrations = $state<Integration[]>([]);
  loading = $state(false);
  private supabase: SupabaseClient | null = null;

  async init(supabase: SupabaseClient) {
    this.supabase = supabase;
    this.loading = true;
    try {
      const { data } = await supabase
        .from('integrations')
        .select('provider, username, avatar_url');
      this.integrations = (data || []).map(d => ({
        ...d,
        connected: true,
      }));
    } catch {
      // Fail silently
    }
    this.loading = false;
  }

  isConnected(provider: string): boolean {
    return this.integrations.some(i => i.provider === provider && i.connected);
  }

  getIntegration(provider: string): Integration | undefined {
    return this.integrations.find(i => i.provider === provider);
  }

  async disconnect(provider: string) {
    const resp = await fetch(`/api/integrations/${provider}/disconnect`, { method: 'POST' });
    if (resp.ok) {
      this.integrations = this.integrations.filter(i => i.provider !== provider);
    }
  }
}

export const integrationsStore = new IntegrationsStore();
