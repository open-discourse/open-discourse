#!/bin/bash
set -o pipefail

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Generate the OpenDiscourse database from raw Bundestag data.

This script executes the complete pipeline (21 stages) to download, process,
and upload parliamentary data into the database. The database must be running.

OPTIONS:
    --force             Clear all stage markers and re-run every stage from scratch
                        (normally skips stages that already succeeded)

    --term TERM(S)      Reprocess only the specified electoral term(s). Accepts a
                        single term or comma-separated list (e.g., "19" or "19,20,21").
                        Skips the DB reset and performs a delta load (replaces only
                        these terms in the DB). Assumes the schema already exists.

    -h, --help          Display this help message and exit

EXAMPLES:
    $(basename "$0")                    # Full pipeline run (all terms, ~4h)
    $(basename "$0") --force            # Force re-run all stages from scratch
    $(basename "$0") --term 19          # Reprocess only electoral term 19
    $(basename "$0") --term 19,20,21    # Reprocess terms 19, 20, and 21

NOTES:
    - Stages that already completed are skipped (unless --force is used)
    - Logs are written to logs/<stage>_log.log
    - Stage completion markers are stored in logs/.status/
    - A database dump is created in ../database/dumps/ after successful completion

For detailed documentation, see python/src/README.md

EOF
}

FORCE=0
TERM=""
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --force)
            FORCE=1
            ;;
        --term)
            shift
            # Accept a comma-separated list ("--term 19,20,21") and turn it
            # into space-separated words, so it expands to multiple argv
            # entries when passed unquoted to a script further down.
            TERM=$(echo "$1" | tr ',' ' ')
            ;;
        *)
            echo "Unbekanntes Argument: $1" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
    shift
done

TERM_FORCE=0
if [ -n "$TERM" ]; then
    TERM_FORCE=1
    echo "--term $TERM: nur Wahlperiode(n) [$TERM] werden in den periodenübergreifenden Contributions-Stufen neu verarbeitet."
    echo "Delta-Load: DB-Reset wird uebersprungen, nur diese Periode(n) werden in der DB ersetzt (setzt voraus, dass das Schema bereits existiert)."
fi

docker-compose down
sleep 5
docker-compose up -d database

echo "Waiting for database to become healthy..."
for i in $(seq 1 60); do
    status=$(docker inspect --format='{{.State.Health.Status}}' od-database 2>/dev/null)
    if [ "$status" = "healthy" ]; then
        echo "Database is healthy."
        break
    fi
    sleep 2
done
if [ "$status" != "healthy" ]; then
    echo "Database did not become healthy in time (last status: $status)." >&2
    exit 1
fi

cd ../database
if [ "$TERM_FORCE" = "1" ]; then
    echo "--term: skipping full DB reset (delta load expects the schema to already exist)."
else
    yarn --ignore-engines run db:update:local
fi
cd ../python
if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
else
    . .venv/Scripts/activate
fi
export PYTHONUTF8=1
mkdir -p logs

STATUS_DIR=logs/.status
mkdir -p "$STATUS_DIR"

if [ "$FORCE" = "1" ]; then
    echo "--force: clearing stage status, all stages will re-run."
    rm -f "$STATUS_DIR"/*.done
fi

python_exe=python
if ! command -v $python_exe &> /dev/null
then
    python_exe=python3
fi
src_path=src/od_lib
preprocessing_path=$src_path/01_preprocessing
factions_path=$src_path/02_factions
politicians_path=$src_path/03_politicians
speech_content_path=$src_path/04_speech_content
electoral_term_19_20_path=$src_path/05_electoral_term_19_20
contributions_path=$src_path/06_contributions
database_path=$src_path/07_database

# Staged Run:
#   - skipped if already succeeded (unless --force)
#   - stops on first failure (no cascading errors)
#   - logs to logs/<stage>_<script>.log (e.g. logs/01_01_download_raw_data_01_download_raw_data.py.log)
#
# Optional 3rd arg: extra CLI argument passed to the script (used for
# --term filtering).
# Optional 4th arg "1": --force = ignore an existing marker and
# always re-run (used together with --term, since we deliberately want
# to reprocess that one term even if the stage already succeeded before).
run_stage () {
    name="$1"
    script="$2"
    extra_arg="$3"
    force_this="$4"
    log="logs/${name}_log.log"
    marker="$STATUS_DIR/${name}.done"

    if [ -f "$marker" ] && [ "$force_this" != "1" ]; then
        echo "[skip] $name (already completed - use --force to re-run everything)"
        return 0
    fi

    echo "[run ] $name"
    if [ -n "$extra_arg" ]; then
        # Intentionally unquoted: extra_arg may hold multiple
        # space-separated terms ("19 20 21") that must expand into
        # separate argv entries, not one combined string.
        $python_exe "$script" $extra_arg 2>&1 | tee "$log"
    else
        $python_exe "$script" 2>&1 | tee "$log"
    fi
    status=${PIPESTATUS[0]}
    if [ "$status" -eq 0 ]; then
        touch "$marker"
        echo "[ ok ] $name"
    else
        echo "[FAIL] $name (exit $status) - see $log" >&2
        exit 1
    fi
}

run_stage "01_01_download_raw_data" "$preprocessing_path/01_download_raw_data.py"
# Always re-run under --term: covers WP19-21, and cheap to redo in full
# (download skips already-fetched sessions itself; split takes ~12s for
# all three terms combined) - this is how new WP21 sessions get picked up.
run_stage "01_02_download_raw_data_electoral_term_19_20" "$preprocessing_path/02_download_raw_data_electoral_term_19_20.py" "" "$TERM_FORCE"
run_stage "01_03_split_xml" "$preprocessing_path/03_split_xml.py"
run_stage "01_04_split_xml_electoral_term_1_and_2" "$preprocessing_path/04_split_xml_electoral_term_1_and_2.py"
run_stage "01_05_split_xml_electoral_term_19_20" "$preprocessing_path/05_split_xml_electoral_term_19_20.py" "" "$TERM_FORCE"
run_stage "01_06_extract_mps_from_mp_base_data" "$preprocessing_path/06_extract_mps_from_mp_base_data.py"
# Its output (electoral_terms.csv) is a hardcoded list of terms and feeds
# a DB foreign key that "speeches"/"contributions_*" reference - must be
# re-run under --term whenever a not-yet-listed term is being uploaded.
run_stage "01_07_create_electoral_terms" "$preprocessing_path/07_create_electoral_terms.py" "" "$TERM_FORCE"
run_stage "02_01_create_factions" "$factions_path/01_create_factions.py"
run_stage "02_02_add_abbreviations_and_ids" "$factions_path/02_add_abbreviations_and_ids.py"
run_stage "03_01_add_faction_id_to_mps" "$politicians_path/01_add_faction_id_to_mps.py"
run_stage "03_02_scrape_mgs" "$politicians_path/02_scrape_mgs.py"
run_stage "03_03_merge_politicians" "$politicians_path/03_merge_politicians.py"
run_stage "04_01_extract_speeches" "$speech_content_path/01_extract_speeches.py"
run_stage "04_02_clean_speeches" "$speech_content_path/02_clean_speeches.py"
run_stage "04_03_match_names_speeches" "$speech_content_path/03_match_names_speeches.py"
run_stage "05_01_extract_speeches_and_contributions_electoral_term_19_20" "$electoral_term_19_20_path/01_extract_speeches_and_contributions_electoral_term_19_20.py" "" "$TERM_FORCE"
run_stage "06_01_extract_contributions" "$contributions_path/01_extract_contributions.py"
# These two run across ALL electoral terms (1-21+) in one pass, and are
# by far the most expensive stages (~2h combined of a ~4h full build).
# They're the only stages that actually filter BY term (--term is passed
# as an extra arg) - the WP1-18-only stages above never see later terms
# anyway, so there's nothing for them to filter.
run_stage "06_02_clean_contributions_extended" "$contributions_path/02_clean_contributions_extended.py" "$TERM" "$TERM_FORCE"
run_stage "06_03_match_contributions_extended" "$contributions_path/03_match_contributions_extended.py" "$TERM" "$TERM_FORCE"
# Always processes ALL terms (no per-term filtering) and must pick up
# whatever 06_02/06_03 just (re-)produced, so force it to re-run under
# --term even though it may already carry a .done marker.
run_stage "07_01_concat_everything" "$database_path/01_concat_everything.py" "" "$TERM_FORCE"
# Passing $TERM here switches the upload script into delta mode: it deletes
# and re-inserts only these terms' speeches/contributions instead of
# expecting an empty schema (see ideas.md for the id-rebasing this relies on).
run_stage "07_02_upload_data_to_database" "$database_path/02_upload_data_to_database.py" "$TERM" "$TERM_FORCE"

dump_dir=../database/dumps
mkdir -p "$dump_dir"
dump_file="$dump_dir/next_$(date +%Y%m%d_%H%M%S).sql.gz"
echo "Dumping database to $dump_file ..."
if docker exec od-database pg_dump -U postgres next | gzip > "$dump_file"; then
    echo "[ ok ] dump written to $dump_file"
else
    echo "[FAIL] dump failed - build data is uploaded but no backup was written" >&2
fi

echo "Build finished successfully."
