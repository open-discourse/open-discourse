/* eslint-disable import/no-default-export */
/* eslint-disable no-console */
/* eslint-disable no-useless-catch */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
import { Pool } from 'pg';
import { DATABASE, importModels } from './dbUpdate';

const config = {
  idleTimeoutMillis: 10, // defaults to 10 sec before client really gets released
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: DATABASE.next,
  password: process.env.DB_PASSWORD,
  port: Number(process.env.DB_PORT) || 5432,
};

const pools: any = {};

export const getPoolByName = (name: DATABASE) => {
  if (!pools[name]) {
    return new Pool({ ...config, database: name });
  }
  return pools[name];
};

export const withDB = async (fn: any) => {
  const client = await getPoolByName(DATABASE.test).connect();
  await client.query('BEGIN ISOLATION LEVEL SERIALIZABLE;');

  try {
    await fn(client);
  } catch (e) {
    throw e;
  } finally {
    await client.query('ROLLBACK;');
    await client.release();
  }
};

const setup = async () => {
  console.log('>> setup test suite');
  const rootPool = getPoolByName(DATABASE.root);
  const testPool = getPoolByName(DATABASE.test);
  try {
    await rootPool.query(`DROP DATABASE IF EXISTS ${DATABASE.test};`);
    await rootPool.query(`CREATE DATABASE ${DATABASE.test};`);
    await importModels(testPool);
  } catch (e) {
    console.error('>> failed to create database', e);
  }
};

export default setup;
