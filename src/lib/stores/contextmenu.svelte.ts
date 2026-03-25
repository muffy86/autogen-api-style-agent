import type { ContextMenuItem } from '$lib/types';

class ContextMenuStore {
  visible = $state(false);
  x = $state(0);
  y = $state(0);
  items = $state<ContextMenuItem[]>([]);

  open(x: number, y: number, items: ContextMenuItem[]): void {
    const menuWidth = 220;
    const separators = items.filter((i) => i.separator).length;
    const menuHeight = (items.length - separators) * 36 + separators * 9 + 10;
    const vw = typeof window !== 'undefined' ? window.innerWidth : 1920;
    const vh = typeof window !== 'undefined' ? window.innerHeight : 1080;
    const margin = 8;

    let posX = x + menuWidth > vw - margin ? x - menuWidth : x;
    let posY = y + menuHeight > vh - margin ? y - menuHeight : y;
    this.x = Math.max(margin, Math.min(posX, vw - menuWidth - margin));
    this.y = Math.max(margin, Math.min(posY, vh - menuHeight - margin));
    this.items = items;
    this.visible = true;
  }

  close(): void {
    this.visible = false;
    this.items = [];
  }
}

export const contextMenuStore = new ContextMenuStore();
