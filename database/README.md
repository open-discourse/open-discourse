# Database

The database service contains the postgres database which acts as the storage

## Folders

- db schemas are stored in `src/model`
- each schema defines it's own tables with one `.sql` file per table
- in the development process those `.sql` files always reflect the true state of the database, regardless of any migration files

## Commands

- To update the database, please run `yarn run db:update:local` — if `next` already exists it is left untouched (no data loss); pass `--force` to drop and rebuild it from scratch
- `python/build.sh` writes a gzipped `pg_dump` of `next` to `database/dumps/` after every successful data upload, as a restore point in case the schema ever needs a `--force` rebuild
- To dump the schema, please run `yarn run db:dump:schema`
- To dump the data, please run `yarn run db:dump:data`
