# This is the official Readme of Open Discourse

## Project Info: TODO

## Roadmap?: TODO

### ...

## Repository Structure

This Repo is structured in three different parts.

- database:

  - Docker-Container for the Postgres Database
  - Contains Scripts that update the Database

- graphql:

  - Docker-Container for the GraphQL Endpoint

- src:

  - Includes every python script in different subsections, sorted by execution order

## How to setup

Required software:
[python3](https://www.python.org/downloads/),
[yarn](https://yarnpkg.com/),
[docker-compose](https://docs.docker.com/compose/),
[node version 12](https://nodejs.org/dist/latest-v12.x/docs/api/) - ideally installed via node version manager (nvm)

- run `yarn` in following directories:
  - `graphql`
  - `database`
- in project root run `sh setup.sh` and `docker-compose build`

Most of the following steps require you to have activated the virtual environment via `source .venv/bin/activate`.

### Start the Database

#### Database: Normal Start

You can easily start the Database via docker-compose.

```Shell
// run from repository root
docker-compose up -d database
```

#### Database: Initial Start / Reset

For the initial start of the Database, you will also need to upload the schema.

```Shell
// run from database folder
yarn run db:update:local
```

### Start the GraphQL Endpoint

This step starts the GraphiQL interface on `http://localhost:5000/graphiql`. This tool is very useful for simply querying data.
You can skip this step if you are if not interested in the interface.

#### GraphQL: Normal Start

You can easily start the GraphQL Endpoint via docker-compose

```Shell
// run from repository root
docker-compose up -d database
```

### Generate Data

Generate the OpenDiscourse-Database from the ground up. The Database has to be started for this script to finish.

This script is just a pipeline executing all scripts in `src`. You can also manually run every script seperatly. For Documentation on this, please visit the [README in src](./src/README.md)

```Shell
// run from python folder
sh build.sh
```

## Further Documentation

- Documentation of every python-script can be found in the [README in src](./src/README.md)
- Documentation of Database commands can be found in the [README in database](./database/README.md)

## Notes

- We use [Python 3.7.4](https://www.python.org/downloads/release/python-374/) during development of the project
