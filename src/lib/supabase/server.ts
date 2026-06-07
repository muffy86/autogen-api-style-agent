// PGlite server (Node.js) - replaces Supabase server client
import { PGlite } from '@electric-sql/pglite';

let _db: PGlite | null = null;
export async function getDb(): Promise<PGlite> {
  if (_db) return _db;
  _db = new PGlite(process.env.PGLITE_DATA_DIR || './data/pglite');
  await _db.waitReady;
  return _db;
}

// Express-style server client
export const createServerClient = () => {
  const dbGetter = getDb;
  return {
    from: (t: string) => ({
      select: async (c = '*') => {
        const d = await dbGetter();
        return { data: (await d.query(`SELECT ${c} FROM ${t}`)).rows, error: null };
      }
    })
  };
};
