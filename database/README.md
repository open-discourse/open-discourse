# Database

- db schemas are stored in `src/model`
- each schema defines it's own tables with one `.sql` file per table
- in the development process those `.sql` files always reflect the true state of the database, regardless of any migration files

## Commands

- To Recreate and Update the Database, please run `yarn run db:update:local`
- To dump the Schmea, please run `yarn run db:dump:schema`
- To dump the Data, please run `yarn run db:dump:data`
