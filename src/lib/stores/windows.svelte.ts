import type { WindowState } from '$lib/types';
import { appRegistry } from './apps.svelte';

export type SnapZone = 'top' | 'left' | 'right' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | null;

export interface SnapPreview {
  x: number;
  y: number;
  w: number;
  h: number;
}

const TOPBAR_H = 36;
const DOCK_H = 80;
const SNAP_THRESHOLD = 20;

function getSnapBounds(zone: SnapZone): SnapPreview | null {
  if (!zone || typeof window === 'undefined') return null;
  const w = window.innerWidth;
  const h = window.innerHeight - TOPBAR_H - DOCK_H;
  const halfW = Math.floor(w / 2);
  const halfH = Math.floor(h / 2);

  switch (zone) {
    case 'top':
      return { x: 0, y: TOPBAR_H, w, h };
    case 'left':
      return { x: 0, y: TOPBAR_H, w: halfW, h };
    case 'right':
      return { x: halfW, y: TOPBAR_H, w: w - halfW, h };
    case 'top-left':
      return { x: 0, y: TOPBAR_H, w: halfW, h: halfH };
    case 'top-right':
      return { x: halfW, y: TOPBAR_H, w: w - halfW, h: halfH };
    case 'bottom-left':
      return { x: 0, y: TOPBAR_H + halfH, w: halfW, h: h - halfH };
    case 'bottom-right':
      return { x: halfW, y: TOPBAR_H + halfH, w: w - halfW, h: h - halfH };
    default:
      return null;
  }
}

export function detectSnapZone(mouseX: number, mouseY: number): SnapZone {
  if (typeof window === 'undefined') return null;
  const w = window.innerWidth;
  const h = window.innerHeight;

  const nearLeft = mouseX <= SNAP_THRESHOLD;
  const nearRight = mouseX >= w - SNAP_THRESHOLD;
  const nearTop = mouseY <= SNAP_THRESHOLD + TOPBAR_H;
  const nearBottom = mouseY >= h - SNAP_THRESHOLD - DOCK_H;

  if (nearTop && nearLeft) return 'top-left';
  if (nearTop && nearRight) return 'top-right';
  if (nearBottom && nearLeft) return 'bottom-left';
  if (nearBottom && nearRight) return 'bottom-right';
  if (nearTop) return 'top';
  if (nearLeft) return 'left';
  if (nearRight) return 'right';
  return null;
}

class WindowStore {
  windows = $state<WindowState[]>([]);
  nextZIndex = $state(100);
  currentSnapZone = $state<SnapZone>(null);

  get snapPreview(): SnapPreview | null {
    return getSnapBounds(this.currentSnapZone);
  }

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

  closeAll(): void {
    this.windows = [];
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
    win.y = TOPBAR_H;
    win.width = window.innerWidth;
    win.height = window.innerHeight - TOPBAR_H - DOCK_H;
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

  snap(id: string, zone: SnapZone): void {
    if (!zone) return;
    const win = this.windows.find((w) => w.id === id);
    if (!win) return;

    const bounds = getSnapBounds(zone);
    if (!bounds) return;

    if (!win.preMaximizeBounds) {
      win.preMaximizeBounds = { x: win.x, y: win.y, width: win.width, height: win.height };
    }

    win.x = bounds.x;
    win.y = bounds.y;
    win.width = bounds.w;
    win.height = bounds.h;
    win.isMaximized = zone === 'top';
    this.currentSnapZone = null;
  }

  setSnapZone(zone: SnapZone): void {
    this.currentSnapZone = zone;
  }

  clearSnapZone(): void {
    this.currentSnapZone = null;
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
}

export const windowStore = new WindowStore();
