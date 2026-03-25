interface RateLimitEntry {
  timestamps: number[];
}

const store = new Map<string, RateLimitEntry>();
const WINDOW_MS = 60 * 1000;
const MAX_REQUESTS = 30;

setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of store) {
    entry.timestamps = entry.timestamps.filter(t => now - t < WINDOW_MS);
    if (entry.timestamps.length === 0) store.delete(key);
  }
}, 5 * 60 * 1000);

export function checkRateLimit(userId: string): { allowed: boolean; remaining: number; resetMs: number } {
  const now = Date.now();
  let entry = store.get(userId);

  if (!entry) {
    entry = { timestamps: [] };
    store.set(userId, entry);
  }

  entry.timestamps = entry.timestamps.filter(t => now - t < WINDOW_MS);

  if (entry.timestamps.length >= MAX_REQUESTS) {
    const oldestInWindow = entry.timestamps[0];
    return {
      allowed: false,
      remaining: 0,
      resetMs: WINDOW_MS - (now - oldestInWindow),
    };
  }

  entry.timestamps.push(now);
  return {
    allowed: true,
    remaining: MAX_REQUESTS - entry.timestamps.length,
    resetMs: WINDOW_MS,
  };
}
