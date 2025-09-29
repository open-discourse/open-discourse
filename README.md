<!-- markdownlint-disable MD033 -->
<p align="center">
  <a href="https://opendiscourse.de/">
    <img
      alt="Open Discourse"
      src="https://opendiscourse.de/images/github/open-discourse_full_black_transparent.png"
      width="400"
    />
  </a>
</p>

# Table of Content

- [Project Status](#project-status)
- [Project Info](#project-info)
- [Repository Structure](#repository-structure)
- [Docker Setup](#docker-setup)
- [Local Setup](#local-setup)
  - [Start the Database](#start-the-database)
    - [Database: Normal Start](#database-normal-start)
    - [Database: Initial Start / Reset](#database-initial-start--reset)
  - [Generate Data](#generate-data)
  - [Start the Full Text Search](#start-the-full-text-search)
    - [Run Frontend with Docker](#run-frontend-with-docker)
    - [Run Frontend locally](#run-frontend-locally)
- [Further Documentation](#further-documentation)
- [Notes](#notes)

## Project Status

**Note:** This repository is currently **not under active development**. We hope to resume development in the future if we can secure funding through the following platforms:

- [GitHub Sponsors](https://github.com/sponsors/open-discourse)
- [Patreon](https://www.patreon.com/opendiscourse)
- Grants or institutional funding

We sincerely appreciate any financial support which will help us continue improving this project.

### Contributing

While we are not actively developing at the moment, contributions from the open-source community are incredibly valuable and encouraged. If you have ideas, bug fixes, or improvements, please feel free create an issue or open a pull request!

Thank you for your support and contributions! Together, we can keep this project moving forward.

## Project Info

The platform is our contribution to democratizing access to political debates and issues.

Open Discourse is a non-profit project of the employees of Limebit GmbH. The idea emerged from the skills and motivations of the employees, in break conversations and from the common ideas of democracy.

We hope that through our preliminary work, data-based journalism, science and civil society will benefit and that the facilitated access to data will encourage to analyze the political history of the Bundestag based on the language used by politicians.

We are happy for every financial support via: <https://www.patreon.com/opendiscourse/> or <https://github.com/sponsors/open-discourse>

## Repository Structure

This Repo is structured in four different parts:

- [database](./database):
  - Docker-Container for the Postgres Database
  - Contains Scripts that update the Database
- [frontend](./frontend):
  - Frontend for the Full Text Search
- [proxy](./proxy):
  - Docker-Container for the Proxy, which protects the database
- [python](./python):
  - Includes every python script in different subsections, sorted by execution order

## Docker Setup

For a quick setup using Docker, please read the [DOCKER_SETUP](./DOCKER_SETUP.md)

## Local Setup

Required software:
[python3](https://www.python.org/downloads/),
[yarn](https://yarnpkg.com/),
[docker-compose](https://docs.docker.com/compose/),
[node version 12](https://nodejs.org/dist/latest-v12.x/docs/api/) - ideally installed via node version manager (nvm)

- run `yarn` in following directories:
  - `database`
  - `frontend`
- run `sh setup.sh` in the `python` directory
- run `docker-compose build` in the `root` folder

### Start the Database

These steps will guide you through starting the Database

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

### Generate Data

Generate the OpenDiscourse-Database from the ground up. The Database has to be started for this script to finish.

This script is just a pipeline executing all scripts in `src`. You can also manually run every script seperatly. For Documentation on this, please visit the [README in src](./python/src/README.md)

```Shell
// run from python folder
sh build.sh
```

### Start the Full Text Search

_Note:_ All of the previous steps have to be completed at least once for the Full Text Search to work properly.

If you want to setup the Full Text Search, follow these steps:

- run `yarn` in following directories:
  - `frontend`
  - `proxy`

Choose one of the following ways to start the Frontend:

#### Run Frontend with Docker

- run `docker-compose up -d` in the `root` folder

#### Run Frontend locally

- run `docker-compose up -d database proxy`in the `root` folder
- run `yarn dev` in the `frontend` folder

## Further Documentation

- Documentation of the database can be found in the [README in database](./database/README.md)
- Documentation of the frontend can be found in the [README in frontend](./frontend/README.md)
- Documentation of the proxy can be found in the [README in proxy](./proxy/README.md)
- Documentation of the python service can be found in the [README in python](./python/README.md)
- Documentation of every python-script can be found in the [README in python/src](./python/src/README.md)

## Notes

- We use [Python 3.7.4](https://www.python.org/downloads/release/python-374/) [d](https://bit.ly/2KE5DFm)uring development of the project
- The graphql endpoint was deprecated and removed by version 1.1.0
