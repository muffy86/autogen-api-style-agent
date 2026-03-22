import type { ContextMenuItem, ContextMenuState } from '$lib/types';

class ContextMenuStore {
  visible = $state(false);
  x = $state(0);
  y = $state(0);
  items = $state<ContextMenuItem[]>([]);

  open(x: number, y: number, items: ContextMenuItem[]): void {
    const menuWidth = 220;
    const menuHeight = items.length * 36;
    const vw = typeof window !== 'undefined' ? window.innerWidth : 1920;
    const vh = typeof window !== 'undefined' ? window.innerHeight : 1080;

    this.x = x + menuWidth > vw ? x - menuWidth : x;
    this.y = y + menuHeight > vh ? y - menuHeight : y;
    this.items = items;
    this.visible = true;
  }

  close(): void {
    this.visible = false;
    this.items = [];
  }
}

export const contextMenuStore = new ContextMenuStore();
