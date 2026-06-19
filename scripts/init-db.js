// scripts/init-db.js
import { PGlite } from '@electric-sql/pglite';
const db = new PGlite('./data/pglite');
await db.waitReady;
// Apply the schema from supabase/migrations/001_initial_schema.sql here
await db.exec(`
  CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT, created_at TIMESTAMP DEFAULT NOW());
  CREATE TABLE IF NOT EXISTS projects (id SERIAL PRIMARY KEY, name TEXT NOT NULL, owner_id INT REFERENCES users(id), created_at TIMESTAMP DEFAULT NOW());
  CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, project_id INT REFERENCES projects(id), title TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT NOW());
`);
console.log('PGlite initialized at ./data/pglite');
await db.close();
