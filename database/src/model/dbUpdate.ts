import * as path from "path";
import fs from "fs";
import { Client, Pool } from "pg";

const isTestMode = process.env.NODE_ENV === "test";

export enum DATABASE {
  root = "postgres",
  next = "next",
  test = "test",
}

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: DATABASE.next,
  password: process.env.DB_PASSWORD,
  port: Number(process.env.DB_PORT) || 5432,
});

// FIXME: order matters. Create dependency handling
const FILES = [
  ["__init.sql"],
  ["open_discourse", "__init.sql"],
  ["open_discourse", "electoral_terms.sql"],
  ["open_discourse", "factions.sql"],
  ["open_discourse", "politicians.sql"],
  ["open_discourse", "speeches.sql"],
  ["open_discourse", "search_speeches.sql"],
  ["open_discourse", "contributions_extended.sql"],
  ["open_discourse", "contributions_simplified.sql"],
  ["misc", "__init.sql"],
  ["misc", "fts_tracking.sql"],
  ["misc", "topic_tracking.sql"],
  ["lda_group", "__init.sql"],
  ["lda_person", "__init.sql"],
];

export const closeAllOtherConnections = async (
  client: Client,
  dbName: DATABASE,
): Promise<unknown> => {
  return client.query(`
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '${dbName}'
    AND pid <> pg_backend_pid();
  `);
};

const resetDB = async (dbName: DATABASE): Promise<unknown> => {
  const client = new Client({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: DATABASE.root,
    password: process.env.DB_PASSWORD,
    port: Number(process.env.DB_PORT) || 5432,
  });
  client.connect();
  // Drop all other connections except ours
  // https://stackoverflow.com/questions/5408156/how-to-drop-a-postgresql-database-if-there-are-active-connections-to-it
  await closeAllOtherConnections(client, dbName);
  await client.query(`DROP DATABASE IF EXISTS ${dbName};`);
  const response = await client.query(`CREATE DATABASE ${dbName};`);
  client.end();
  return response;
};

export const importModels = async (pool: Pool): Promise<unknown> => {
  // eslint-disable-next-line no-async-promise-executor
  return new Promise<void>(async (resolve, reject) => {
    try {
      for (const file of FILES) {
        const filepath = path.join(__dirname, ...file);
        const data = fs.readFileSync(filepath, { encoding: "utf-8" });
        if (!isTestMode) {
          console.log(`execute: ${filepath}: \n`, data);
        }
        await pool.query(data);
        if (FILES.indexOf(file) === FILES.length - 1) {
          resolve();
        }
      }
    } catch (e) {
      reject(e);
    }
  });
};

const setupDB = async (dbName: DATABASE): Promise<void> => {
  await resetDB(dbName);
  await importModels(pool);
  pool.end();
};

if (!isTestMode) {
  setupDB(DATABASE.next);
}
