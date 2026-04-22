const STORAGE_KEY = 'elysium-settings';

interface GeneralSettings {
  defaultTeam: string;
  defaultProvider: string;
  maxTurns: number;
  sessionTimeoutMinutes: number;
  streamResponses: boolean;
  showNotifications: boolean;
  soundEnabled: boolean;
}

const DEFAULTS: GeneralSettings = {
  defaultTeam: 'productivity',
  defaultProvider: 'auto',
  maxTurns: 30,
  sessionTimeoutMinutes: 60,
  streamResponses: true,
  showNotifications: true,
  soundEnabled: false,
};

class SettingsStore {
  settings = $state<GeneralSettings>({ ...DEFAULTS });

  constructor() {
    this.load();
  }

  update<K extends keyof GeneralSettings>(key: K, value: GeneralSettings[K]) {
    this.settings[key] = value;
    this.save();
  }

  reset() {
    this.settings = { ...DEFAULTS };
    this.save();
  }

  private save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.settings));
    } catch {}
  }

  private load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data = JSON.parse(raw);
        this.settings = { ...DEFAULTS, ...data };
      }
    } catch {}
  }
}

export const settingsStore = new SettingsStore();
