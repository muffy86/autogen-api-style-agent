interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  duration: number;
  createdAt: number;
}

class NotificationStore {
  notifications = $state<Notification[]>([]);

  add(title: string, message: string, type: Notification['type'] = 'info', duration = 5000): string {
    const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
    this.notifications.push({ id, title, message, type, duration, createdAt: Date.now() });
    if (duration > 0) {
      setTimeout(() => this.dismiss(id), duration);
    }
    return id;
  }

  dismiss(id: string) {
    const idx = this.notifications.findIndex((n) => n.id === id);
    if (idx !== -1) this.notifications.splice(idx, 1);
  }

  clear() {
    this.notifications = [];
  }
}

export const notificationStore = new NotificationStore();
export type { Notification };
