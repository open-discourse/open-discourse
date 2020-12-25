# Database

The database service contains the postgres database which acts as the storage

## Folders

- db schemas are stored in `src/model`
- each schema defines it's own tables with one `.sql` file per table
- in the development process those `.sql` files always reflect the true state of the database, regardless of any migration files

## Commands

- To recreate and update the database, please run `yarn run db:update:local`
- To dump the schema, please run `yarn run db:dump:schema`
- To dump the data, please run `yarn run db:dump:data`
