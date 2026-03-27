import type { ContextMenuItem } from '$lib/types';

class ContextMenuStore {
  visible = $state(false);
  x = $state(0);
  y = $state(0);
  items = $state<ContextMenuItem[]>([]);

  open(x: number, y: number, items: ContextMenuItem[]): void {
    if (typeof window === 'undefined') return;

    const menuWidth = 220;
    const padding = 8;
    const separatorCount = items.filter((i) => i.separator).length;
    const menuHeight = (items.length - separatorCount) * 36 + separatorCount * 9 + 10;

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let posX = x;
    let posY = y;

    if (posX + menuWidth > viewportWidth - padding) {
      posX = viewportWidth - menuWidth - padding;
    }
    if (posX < padding) {
      posX = padding;
    }

    if (posY + menuHeight > viewportHeight - padding) {
      posY = viewportHeight - menuHeight - padding;
    }
    if (posY < padding) {
      posY = padding;
    }

    this.x = posX;
    this.y = posY;
    this.items = items;
    this.visible = true;
  }

  close(): void {
    this.visible = false;
    this.items = [];
  }
}

export const contextMenuStore = new ContextMenuStore();
