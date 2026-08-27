set shell := ["bash", "-uc"]

# yarn engines checks fail on this host (Node 24 vs. required ^20) -
# baked in everywhere instead of remembering the flag each time.
yarn := "yarn --ignore-engines"

# Show all available recipes.
default:
    @just --list

# --- primary interface --------------------------------------------------

# Bring up the backend (database + proxy) and make sure data exists.
# Safe to re-run: a DB that already has speeches is left untouched, only an
# empty one triggers a full pipeline run.
init:
    #!/usr/bin/env bash
    set -euo pipefail
    docker-compose up -d database proxy
    just db-update
    count=$(docker exec od-database psql -U postgres -d next -tAc "SELECT count(*) FROM open_discourse.speeches" 2>/dev/null || echo 0)
    if [ "${count:-0}" = "0" ]; then
        echo ">> DB ist leer - starte vollen Pipeline-Lauf (~4h)..."
        just pipeline
    else
        echo ">> DB enthaelt bereits $count Reden - Import uebersprungen."
    fi
    docker-compose up -d proxy

# Reprocess/reimport only the given electoral term(s), e.g. `just update 19,20,21`.
# Restarts the proxy afterwards (the pipeline's docker-compose down takes it out).
update TERM:
    just pipeline-term {{TERM}}
    docker-compose up -d proxy

# Bring up the full stack (database, proxy, frontend) and print the URL.
serve:
    docker-compose up -d database proxy frontend
    @echo "Frontend: http://localhost:3000"

# Full reset: wipe the DB schema, then re-initialize from scratch (runs
# the full pipeline if that leaves the DB empty - see `init`).
force:
    just db-update --force
    just init

# --- docker-compose -----------------------------------------------------

# Start every service in the background.
up:
    docker-compose up -d

# Stop everything.
down:
    docker-compose down

# Rebuild and (re)start one service, e.g. `just rebuild proxy`.
rebuild SERVICE:
    docker-compose up -d --build {{SERVICE}}

# Container status.
ps:
    docker ps --filter "name=od-" --format "table {{{{.Names}}\t{{{{.Status}}\t{{{{.Ports}}"

# Tail a container's logs, e.g. `just logs proxy`.
logs SERVICE="proxy" LINES="100":
    docker logs od-{{SERVICE}} --tail {{LINES}}

# --- database -------------------------------------------------------------

# Install database package deps.
db-install:
    cd database && {{yarn}} install

# Create/refresh schema in "next". No-op if it already exists - pass
# `--force` to actually drop and rebuild it (deletes all data).
db-update *ARGS:
    cd database && {{yarn}} run db:update:local {{ARGS}}

db-update-digitalocean *ARGS:
    cd database && {{yarn}} run db:update:digitalocean {{ARGS}}

db-typecheck:
    cd database && {{yarn}} run typecheck

db-lint:
    cd database && {{yarn}} run lint

db-format:
    cd database && {{yarn}} run format

# Gzipped full dump of "next" via the running container (no local pg_dump needed).
# Optional NAME is appended to the filename, e.g. `just dump-db wp19-20-21`.
dump-db NAME="":
    mkdir -p database/dumps
    docker exec od-database pg_dump -U postgres next | gzip > "database/dumps/next_$(date +%Y%m%d_%H%M%S){{ if NAME != "" { "_" + NAME } else { "" } }}.sql.gz"

# Restore a gzipped dump produced by `dump-db`, e.g. `just restore-db database/dumps/next_....sql.gz`.
restore-db FILE:
    gunzip -c {{FILE}} | docker exec -i od-database psql -U postgres next

# --- proxy ------------------------------------------------------------------

proxy-install:
    cd proxy && {{yarn}} install

proxy-dev:
    cd proxy && {{yarn}} run dev

proxy-build:
    cd proxy && {{yarn}} run build

proxy-typecheck:
    cd proxy && {{yarn}} run typecheck

proxy-lint:
    cd proxy && {{yarn}} run lint

proxy-format:
    cd proxy && {{yarn}} run format

# --- frontend ---------------------------------------------------------------

frontend-install:
    cd frontend && {{yarn}} install

frontend-dev:
    cd frontend && {{yarn}} run dev

frontend-build:
    cd frontend && {{yarn}} run build

frontend-lint:
    cd frontend && {{yarn}} run lint

frontend-format:
    cd frontend && {{yarn}} run format

# --- python pipeline ---------------------------------------------------------

# Full pipeline run (all 21 terms, ~4h). Add args e.g. `just pipeline --force`.
pipeline *ARGS:
    cd python && sh build.sh {{ARGS}}

# Reprocess/upload only the given electoral term(s), e.g. `just pipeline-term 19` or `just pipeline-term 19,20,21`.
pipeline-term TERM:
    cd python && sh build.sh --term {{TERM}}

# Tail the top-level pipeline log written by build.sh. Ctrl+C to stop
# (does not affect the running build). Pass LINES to change the backlog,
# e.g. `just watch 200`.
watch LINES="40":
    tail -n {{LINES}} -F python/logs/build_run.log

# Upload already-processed final data (python/data/03_final/*) for one or more
# terms straight into the DB, skipping the pipeline entirely - fast path for
# "the DB is empty/partial but the final pickles from a previous run are still there".
# Skips terms that already match the pickles; append `--force` to delete+reinsert anyway.
upload-term +TERMS:
    cd python && { source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate; } && export PYTHONUTF8=1 && python src/od_lib/07_database/02_upload_data_to_database.py {{TERMS}}

# Drop+recreate the schema, then re-upload ALL terms from the existing final
# pipeline output (python/data/03_final/*) - fast, since scraping/processing
# stages stay cached and only get skipped. Use this after `db-update --force`
# would otherwise leave the DB empty until the next full `pipeline --force`.
reimport-all:
    just db-update --force
    rm -f python/logs/.status/07_02_upload_data_to_database.done
    just pipeline

# Read-only: checks every term's raw session XML for gaps in the session
# numbering (catches issues like a pagination bug silently skipping a batch
# of sessions - the download stage itself reports success either way).
# Never downloads or deletes anything - safe to run anytime.
check-raw-data:
    cd python && { source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate; } && python -m od_lib.check_raw_data_completeness

# Nuclear option: wipe the DB schema, every downloaded/cached/processed
# pipeline file, and every stage marker, then run the entire pipeline for
# all 21 terms from a completely clean slate (~4h+, re-downloads everything
# from bundestag.de). Prefer `check-raw-data` first - it catches the same
# class of silent gap for free, without discarding already-crawled pages or
# re-hitting the source. Only reach for this if the check itself is in
# doubt (e.g. you don't trust the cached files' *content*, not just their
# presence).
full-reset:
    just db-update --force
    rm -rf python/data
    rm -rf python/logs
    just pipeline
