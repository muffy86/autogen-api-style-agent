import type { Notification } from '$lib/types';

class NotificationStore {
  notifications = $state<Notification[]>([]);
  private timers = new Map<string, ReturnType<typeof setTimeout>>();

  push(notif: Omit<Notification, 'id' | 'createdAt'>): string {
    const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const full: Notification = {
      ...notif,
      id,
      duration: notif.duration ?? 5000,
      createdAt: new Date()
    };

    const combined = [full, ...this.notifications];
    const kept = combined.slice(0, 5);
    const evicted = combined.slice(5);

    for (const n of evicted) {
      const timer = this.timers.get(n.id);
      if (timer) {
        clearTimeout(timer);
        this.timers.delete(n.id);
      }
    }

    this.notifications = kept;

    if (full.duration && full.duration > 0) {
      const timer = setTimeout(() => {
        this.dismiss(id);
      }, full.duration);
      this.timers.set(id, timer);
    }

    return id;
  }

  dismiss(id: string): void {
    const timer = this.timers.get(id);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(id);
    }
    this.notifications = this.notifications.filter((n) => n.id !== id);
  }

  clear(): void {
    for (const timer of this.timers.values()) {
      clearTimeout(timer);
    }
    this.timers.clear();
    this.notifications = [];
  }
}

export const notificationStore = new NotificationStore();
