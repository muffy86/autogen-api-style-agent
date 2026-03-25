import type { Notification } from '$lib/types';

class NotificationStore {
  notifications = $state<Notification[]>([]);

  push(notif: Omit<Notification, 'id' | 'createdAt' | 'timerId'>): string {
    const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const duration = notif.duration ?? 5000;

    const full: Notification = {
      ...notif,
      id,
      duration,
      createdAt: new Date()
    };

    if (duration > 0) {
      full.timerId = setTimeout(() => {
        this.dismiss(id);
      }, duration);
    }

    const combined = [full, ...this.notifications];
    const kept = combined.slice(0, 5);
    const evicted = combined.slice(5);

    for (const n of evicted) {
      if (n.timerId) {
        clearTimeout(n.timerId);
        n.timerId = undefined;
      }
    }

    this.notifications = kept;
    return id;
  }

  dismiss(id: string): void {
    const notif = this.notifications.find((n) => n.id === id);
    if (notif?.timerId) {
      clearTimeout(notif.timerId);
      notif.timerId = undefined;
    }
    this.notifications = this.notifications.filter((n) => n.id !== id);
  }

  clear(): void {
    for (const n of this.notifications) {
      if (n.timerId) {
        clearTimeout(n.timerId);
        n.timerId = undefined;
      }
    }
    this.notifications = [];
  }
}

export const notificationStore = new NotificationStore();
