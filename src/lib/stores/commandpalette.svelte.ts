import type { PaletteCommand } from '$lib/types';

class CommandPaletteStore {
  visible = $state(false);
  commands = $state<PaletteCommand[]>([]);
  query = $state('');

  get filtered(): PaletteCommand[] {
    if (!this.query.trim()) return this.commands.slice(0, 8);
    const q = this.query.toLowerCase();
    return this.commands
      .filter(
        (c) =>
          c.title.toLowerCase().includes(q) ||
          (c.description && c.description.toLowerCase().includes(q))
      )
      .slice(0, 8);
  }

  get grouped(): Record<string, PaletteCommand[]> {
    const groups: Record<string, PaletteCommand[]> = {};
    for (const cmd of this.filtered) {
      if (!groups[cmd.category]) groups[cmd.category] = [];
      groups[cmd.category].push(cmd);
    }
    return groups;
  }

  register(commands: PaletteCommand[]): void {
    this.commands = commands;
  }

  open(): void {
    this.visible = true;
    this.query = '';
  }

  close(): void {
    this.visible = false;
    this.query = '';
  }

  toggle(): void {
    if (this.visible) this.close();
    else this.open();
  }

  execute(cmd: PaletteCommand): void {
    cmd.action();
    this.close();
  }
}

export const commandPaletteStore = new CommandPaletteStore();
