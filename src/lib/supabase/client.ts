// PGlite client (browser) - replaces Supabase
import { PGlite } from '@electric-sql/pglite';

let _db: PGlite | null = null;
export async function getDb(): Promise<PGlite> {
  if (_db) return _db;
  _db = new PGlite('idb://autogen-api-db');
  await _db.waitReady;
  await _db.exec(`
    CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT, created_at TIMESTAMP DEFAULT NOW());
    CREATE TABLE IF NOT EXISTS projects (id SERIAL PRIMARY KEY, name TEXT NOT NULL, owner_id INT REFERENCES users(id), created_at TIMESTAMP DEFAULT NOW());
    CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, project_id INT REFERENCES projects(id), title TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT NOW());
  `);
  return _db;
}
export const supabase = {
  from: (t: string) => ({
    select: async (c = '*') => {
      const d = await getDb();
      return { data: (await d.query(`SELECT ${c} FROM ${t}`)).rows, error: null };
    },
    insert: async (rows: any) => {
      const d = await getDb();
      const list = Array.isArray(rows) ? rows : [rows];
      const cols = Object.keys(list[0]);
      const values = list.map(r => cols.map(c => r[c]));
      const placeholders = values.map((_, i) => `(${cols.map((_, j) => `$${i*cols.length+j+1}`).join(',')})`).join(',');
      const r = await d.query(`INSERT INTO ${t} (${cols.join(',')}) VALUES ${placeholders}`, values.flat());
      return { data: r.rows, error: null };
    }
  })
};
