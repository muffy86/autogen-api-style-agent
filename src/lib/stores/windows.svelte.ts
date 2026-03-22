import type { WindowState, SnapZone } from '$lib/types';
import { appRegistry } from './apps.svelte';

class WindowStore {
  windows = $state<WindowState[]>([]);
  nextZIndex = $state(100);
  snapPreview = $state<SnapZone | null>(null);

  get activeWindow(): WindowState | undefined {
    return this.windows
      .filter((w) => !w.isMinimized)
      .sort((a, b) => b.zIndex - a.zIndex)[0];
  }

  get visibleWindows(): WindowState[] {
    return this.windows.filter((w) => !w.isMinimized);
  }

  hasOpenWindow(appId: string): boolean {
    return this.windows.some((w) => w.appId === appId);
  }

  open(appId: string): void {
    const app = appRegistry.getApp(appId);
    if (!app) return;

    if (app.singleton) {
      const existing = this.windows.find((w) => w.appId === appId);
      if (existing) {
        if (existing.isMinimized) {
          existing.isMinimized = false;
        }
        this.focus(existing.id);
        return;
      }
    }

    const offsetCount = this.windows.filter((w) => w.appId === appId).length;
    const offset = offsetCount * 30;

    const x = Math.max(60, (window.innerWidth - app.defaultWidth) / 2 + offset);
    const y = Math.max(50, (window.innerHeight - app.defaultHeight) / 2 + offset);

    const id = `${appId}-${Date.now()}`;
    this.nextZIndex++;

    this.windows.push({
      id,
      appId,
      title: app.name,
      x,
      y,
      width: app.defaultWidth,
      height: app.defaultHeight,
      minWidth: app.minWidth,
      minHeight: app.minHeight,
      isMinimized: false,
      isMaximized: false,
      isFocused: true,
      zIndex: this.nextZIndex
    });

    this.windows.forEach((w) => {
      if (w.id !== id) w.isFocused = false;
    });
  }

  close(id: string): void {
    const idx = this.windows.findIndex((w) => w.id === id);
    if (idx !== -1) {
      this.windows.splice(idx, 1);
    }
  }

  focus(id: string): void {
    this.nextZIndex++;
    this.windows.forEach((w) => {
      if (w.id === id) {
        w.isFocused = true;
        w.zIndex = this.nextZIndex;
      } else {
        w.isFocused = false;
      }
    });
  }

  minimize(id: string): void {
    const win = this.windows.find((w) => w.id === id);
    if (win) {
      win.isMinimized = true;
      win.isFocused = false;
    }
  }

  maximize(id: string): void {
    const win = this.windows.find((w) => w.id === id);
    if (!win) return;

    if (win.isMaximized) {
      this.restore(id);
      return;
    }

    win.preMaximizeBounds = { x: win.x, y: win.y, width: win.width, height: win.height };
    win.x = 0;
    win.y = 36;
    win.width = window.innerWidth;
    win.height = window.innerHeight - 36 - 80;
    win.isMaximized = true;
  }

  restore(id: string): void {
    const win = this.windows.find((w) => w.id === id);
    if (!win || !win.preMaximizeBounds) return;

    win.x = win.preMaximizeBounds.x;
    win.y = win.preMaximizeBounds.y;
    win.width = win.preMaximizeBounds.width;
    win.height = win.preMaximizeBounds.height;
    win.isMaximized = false;
    win.preMaximizeBounds = undefined;
  }

  move(id: string, x: number, y: number): void {
    const win = this.windows.find((w) => w.id === id);
    if (win) {
      win.x = Math.max(0, Math.min(x, window.innerWidth - 100));
      win.y = Math.max(0, Math.min(y, window.innerHeight - 50));
    }
  }

  resize(id: string, width: number, height: number, x?: number, y?: number): void {
    const win = this.windows.find((w) => w.id === id);
    if (!win) return;
    win.width = Math.max(win.minWidth, width);
    win.height = Math.max(win.minHeight, height);
    if (x !== undefined) win.x = x;
    if (y !== undefined) win.y = y;
  }

  unfocusAll(): void {
    this.windows.forEach((w) => {
      w.isFocused = false;
    });
  }

  checkSnap(mouseX: number, mouseY: number): void {
    const threshold = 20;
    const topBarHeight = 36;
    const dockHeight = 80;
    const vw = typeof window !== 'undefined' ? window.innerWidth : 1920;
    const vh = typeof window !== 'undefined' ? window.innerHeight : 1080;

    if (mouseX <= threshold) {
      this.snapPreview = {
        region: 'left',
        bounds: { x: 0, y: topBarHeight, width: vw / 2, height: vh - topBarHeight - dockHeight }
      };
    } else if (mouseX >= vw - threshold) {
      this.snapPreview = {
        region: 'right',
        bounds: { x: vw / 2, y: topBarHeight, width: vw / 2, height: vh - topBarHeight - dockHeight }
      };
    } else if (mouseY <= threshold + topBarHeight) {
      this.snapPreview = {
        region: 'maximize',
        bounds: { x: 0, y: topBarHeight, width: vw, height: vh - topBarHeight - dockHeight }
      };
    } else {
      this.snapPreview = null;
    }
  }

  applySnap(id: string): void {
    if (!this.snapPreview) return;
    const b = this.snapPreview.bounds;
    const win = this.windows.find((w) => w.id === id);
    if (win) {
      win.preMaximizeBounds = { x: win.x, y: win.y, width: win.width, height: win.height };
      win.x = b.x;
      win.y = b.y;
      win.width = b.width;
      win.height = b.height;
      win.isMaximized = this.snapPreview.region === 'maximize';
    }
    this.snapPreview = null;
  }

  clearSnap(): void {
    this.snapPreview = null;
  }

  closeAll(appId?: string): void {
    if (appId) {
      this.windows = this.windows.filter((w) => w.appId !== appId);
    } else {
      this.windows = [];
    }
  }
}

export const windowStore = new WindowStore();
