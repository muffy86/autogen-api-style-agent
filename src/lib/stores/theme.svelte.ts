type Theme = 'dark' | 'light' | 'system';

interface AccentConfig {
  accent: string;
  glow: string;
  subtle: string;
  shadowGlow: string;
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? { r: parseInt(result[1], 16), g: parseInt(result[2], 16), b: parseInt(result[3], 16) }
    : null;
}

function lightenHex(hex: string, amount: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  const r = Math.min(255, rgb.r + Math.round((255 - rgb.r) * amount));
  const g = Math.min(255, rgb.g + Math.round((255 - rgb.g) * amount));
  const b = Math.min(255, rgb.b + Math.round((255 - rgb.b) * amount));
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function computeAccentConfig(hex: string): AccentConfig {
  const rgb = hexToRgb(hex);
  if (!rgb) return { accent: hex, glow: hex, subtle: `${hex}26`, shadowGlow: `0 0 20px ${hex}4d` };
  return {
    accent: hex,
    glow: lightenHex(hex, 0.3),
    subtle: `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.15)`,
    shadowGlow: `0 0 20px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.3)`,
  };
}

class ThemeStore {
  theme = $state<Theme>('dark');
  accentColor = $state('#8b5cf6');
  private osPrefersDark = $state(true);

  get resolved(): 'dark' | 'light' {
    if (this.theme === 'system') {
      return this.osPrefersDark ? 'dark' : 'light';
    }
    return this.theme;
  }

  constructor() {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('elysium-theme') as Theme | null;
      if (saved) this.theme = saved;
      const savedAccent = localStorage.getItem('elysium-accent');
      if (savedAccent) this.accentColor = savedAccent;

      const mql = window.matchMedia('(prefers-color-scheme: dark)');
      this.osPrefersDark = mql.matches;
      mql.addEventListener('change', (e) => {
        this.osPrefersDark = e.matches;
      });
    }
  }

  setTheme(t: Theme) {
    this.theme = t;
    if (typeof window !== 'undefined') {
      localStorage.setItem('elysium-theme', t);
    }
  }

  setAccent(hex: string) {
    this.accentColor = hex;
    if (typeof window !== 'undefined') {
      localStorage.setItem('elysium-accent', hex);
      this.applyAccent(hex);
    }
  }

  applyAccent(hex: string) {
    const config = computeAccentConfig(hex);
    const root = document.documentElement;
    root.style.setProperty('--accent', config.accent);
    root.style.setProperty('--accent-glow', config.glow);
    root.style.setProperty('--accent-subtle', config.subtle);
    root.style.setProperty('--shadow-glow', config.shadowGlow);
  }

  initAccent() {
    if (typeof window !== 'undefined' && this.accentColor !== '#8b5cf6') {
      this.applyAccent(this.accentColor);
    }
  }
}

export const themeStore = new ThemeStore();
