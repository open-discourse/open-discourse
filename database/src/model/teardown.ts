/* eslint-disable no-console */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
import { getPoolByName } from './setup';
import { DATABASE } from './dbUpdate';

export = async () => {
  console.log('>> teardown test suite');
  const testPool = getPoolByName(DATABASE.test);
  const rootPool = getPoolByName(DATABASE.root);
  await testPool.end();
  await rootPool.query(`DROP DATABASE IF EXISTS ${DATABASE.test};`);
  await rootPool.end();
};
