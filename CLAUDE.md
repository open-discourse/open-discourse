# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open Discourse is a non-profit platform that democratizes access to political debates from the German Bundestag. The project extracts, processes, and analyzes parliamentary speeches and contributions to support data-based journalism and research.

## Repository Structure

This is a multi-service architecture with four main components:

- **python/**: Data processing pipeline using doit task runner
- **database/**: PostgreSQL database container and schema management
- **proxy/**: Express.js API server that protects the database
- **frontend/**: Next.js web application for full-text search

## Development Commands

### Python Data Pipeline

```bash
cd python
make install-dev          # Install dependencies with uv
make lint                 # Run ruff linting
make format               # Format code with ruff
make test                 # Run pytest tests
make database             # Start database and initialize schema
make list-tasks           # List all doit pipeline tasks
uv run doit               # Run the full data processing pipeline
```

### Frontend (Next.js)

```bash
cd frontend
yarn install             # Install dependencies
yarn dev                 # Development server
yarn build               # Production build
yarn lint                # ESLint
yarn format              # Prettier formatting
```

### Database Management

```bash
cd database
yarn install             # Install dependencies
yarn run db:update:local # Update database schema (requires local DB)
yarn run typecheck       # TypeScript checking
```

### Proxy Server

```bash
cd proxy
yarn install             # Install dependencies
yarn dev                 # Development server with nodemon
yarn build               # Build TypeScript
yarn start               # Production server
yarn typecheck           # TypeScript checking
```

### Docker Operations

```bash
# From project root
docker-compose up -d database        # Start database only
docker-compose up -d database proxy  # Start database and proxy
docker-compose up -d                 # Start all services
docker-compose build                 # Build all containers
```

## Architecture Overview

### Data Processing Pipeline (Python)

The Python package uses the doit task runner to orchestrate a complex data processing pipeline:

1. **Data Download**: Fetches XML files from Bundestag APIs
2. **Preprocessing**: Splits and cleans XML documents
3. **Entity Extraction**: Extracts politicians, factions, and speeches
4. **Matching**: Links speeches to politicians and factions
5. **Database Upload**: Loads processed data into PostgreSQL

Tasks are defined in `python/dodo.py` and organized by processing steps. The pipeline processes multiple electoral terms (1-20) with different approaches for different periods.

### Database Schema

- PostgreSQL database with schemas for speeches, politicians, factions, contributions
- Schema updates handled via TypeScript scripts in `database/src/model/`
- Database initialization requires running `yarn run db:update:local`

### API Layer (Proxy)

- Express.js server that provides rate-limited access to the database
- Handles caching, request filtering, and database protection
- Serves as middleware between frontend and database

### Frontend Application

- Next.js application providing full-text search interface
- Uses Chakra UI for components and styling
- Connects to backend via the proxy API

## Development Workflow

1. **Database Setup**: Start with `make database` from python/ directory
2. **Data Generation**: Run `uv run doit` to process data (requires substantial time)
3. **Service Development**: Use `docker-compose up -d database proxy` + `yarn dev` in frontend/
4. **Full Stack**: Use `docker-compose up -d` for complete environment

## Important Notes

- The project uses Python 3.10+ and requires `uv` package manager
- Data processing pipeline is compute-intensive and may take hours
- Electoral term 20 requires manual session updates
- Topic modeling features are work-in-progress
- Node.js version ^20 required for all JavaScript services
