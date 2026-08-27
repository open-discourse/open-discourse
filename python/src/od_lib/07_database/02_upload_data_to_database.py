from sqlalchemy import create_engine, text, table as sa_table, column as sa_column
from sqlalchemy.dialects.postgresql import insert as pg_insert
from concurrent.futures import ThreadPoolExecutor
import od_lib.definitions.path_definitions as path_definitions
from od_lib.helper_functions.progressbar import progressbar
import pandas as pd
import ctypes
import datetime
import io
import platform
import sys


def _prevent_system_sleep():
    """Keep host awake while this process runs (auto-clears on exit)."""
    if platform.system() != "Windows":
        return
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)


_prevent_system_sleep()


def _log_stage(msg):
    """Timestamped stage marker."""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")


UPLOAD_CHUNK_SIZE = 25000
SCHEMA = "open_discourse"

# CLI: electoral_term numbers -> delta mode (delete+reinsert only those terms).
# `--force`: skip match checks, always delete+reinsert.
_cli_args = sys.argv[1:]
FORCE_DELETE = "--force" in _cli_args
_term_args = [a for a in _cli_args if a != "--force"]
DELTA_TERMS = [int(t) for t in _term_args] if _term_args else None

_integer_columns_cache = {}


def _integer_columns(engine, schema, table_name):
    """DB int-typed columns, cached. Pandas float64 (e.g. via NaN) would be
    written as "0.0" to CSV - COPY rejects that for bigint."""
    key = (schema, table_name)
    if key not in _integer_columns_cache:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = :schema AND table_name = :table_name "
                    "AND data_type IN ('bigint', 'integer', 'smallint')"
                ),
                {"schema": schema, "table_name": table_name},
            ).fetchall()
        _integer_columns_cache[key] = {r[0] for r in rows}
    return _integer_columns_cache[key]


def upload_with_progress(df, table_name, engine, schema, chunk_size=UPLOAD_CHUNK_SIZE, label=None):
    """Chunked COPY upload (copy_expert), ~5-10x faster than to_sql()."""
    label = label or f"Upload {table_name}..."
    int_cols = _integer_columns(engine, schema, table_name) & set(df.columns)
    float_int_cols = [c for c in int_cols if pd.api.types.is_float_dtype(df[c])]
    if float_int_cols:
        df = df.copy()
        for c in float_int_cols:
            # Int64 (nullable) so NULL survives (no silent 0, no crash).
            df[c] = df[c].astype("Int64")
    cols = list(df.columns)
    col_list = ", ".join(f'"{c}"' for c in cols)
    # NULL marker '\N' instead of '': speech_content holds genuine empty
    # strings (NOT NULL) - NULL '' would collapse them into SQL NULL.
    NULL_MARKER = "\\N"
    copy_sql = f"COPY \"{schema}\".\"{table_name}\" ({col_list}) FROM STDIN WITH (FORMAT csv, NULL '{NULL_MARKER}')"

    def copy_chunk(chunk):
        buf = io.StringIO()
        chunk.to_csv(buf, index=False, header=False, columns=cols, na_rep=NULL_MARKER)
        buf.seek(0)
        raw = engine.raw_connection()
        try:
            with raw.cursor() as cur:
                cur.copy_expert(copy_sql, buf)
            raw.commit()
        finally:
            raw.close()

    if len(df) <= chunk_size:
        print(label, end="", flush=True)
        copy_chunk(df)
        print(" Done.")
        return
    chunk_starts = range(0, len(df), chunk_size)
    for start in progressbar(chunk_starts, label):
        copy_chunk(df.iloc[start : start + chunk_size])


def upload_by_period(df, table_name, engine, schema, periods, chunk_size=UPLOAD_CHUNK_SIZE):
    """Upload per Wahlperiode. `periods`: row-aligned Series mit dem Term
    jeder Zeile (contributions_* tragen nur speech_id)."""
    total_rows = len(df)
    rows_done = 0
    unique_periods = sorted(periods.unique())
    for i, period in enumerate(unique_periods, start=1):
        subset = df[(periods == period).values]
        label = (
            f"Upload {table_name} (Wahlperiode {period}, {i}/{len(unique_periods)}, "
            f"Zeile {rows_done + 1}-{rows_done + len(subset)}/{total_rows})..."
        )
        upload_with_progress(subset, table_name, engine, schema, chunk_size=chunk_size, label=label)
        rows_done += len(subset)


def upsert_dataframe(df, table_name, engine, schema, pk_cols=("id",), chunk_size=UPLOAD_CHUNK_SIZE):
    """ON CONFLICT DO UPDATE for the small reference tables - must not be
    truncated in delta mode (FKs from untouched terms)."""
    if len(df) == 0:
        return
    print(f"Upsert {table_name}...", end="", flush=True)
    # astype(object) first: float64 columns cast None back to NaN otherwise.
    df = df.astype(object).where(pd.notnull(df), None)
    tbl = sa_table(table_name, *[sa_column(c) for c in df.columns], schema=schema)
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            stmt = pg_insert(tbl).values(chunk)
            update_cols = {c: stmt.excluded[c] for c in df.columns if c not in pk_cols}
            stmt = stmt.on_conflict_do_update(index_elements=list(pk_cols), set_=update_cols)
            conn.execute(stmt)
    print(" Done.")


def delete_rows(
    engine,
    schema,
    table_name,
    where_sql=None,
    params=None,
    batch_size=5000,
    partitions=4,
    max_workers=4,
    id_bounds=None,
):
    """Batched, parallel partitioned delete (each batch commits on its own).

    `id_bounds` (min,max): partition by contiguous id range ->
    PK index range scan. Without: fallback `id % N` (not sargable ->
    seq scan, fine for smaller tables).
    """
    where_clause = f"AND {where_sql}" if where_sql else ""

    if id_bounds is not None:
        id_min, id_max = id_bounds
        span = id_max - id_min + 1
        edges = [id_min + i * span // partitions for i in range(partitions)] + [id_max + 1]
        range_bounds = list(zip(edges[:-1], edges[1:]))

    def delete_partition(p):
        if id_bounds is not None:
            lo, hi = range_bounds[p]
            range_clause = "id >= :lo AND id < :hi"
            range_params = {"lo": lo, "hi": hi}
        else:
            range_clause = "id % :partitions = :p"
            range_params = {"partitions": partitions, "p": p}
        select_ids_sql = (
            f'SELECT id FROM "{schema}"."{table_name}" '
            f"WHERE {range_clause} {where_clause} LIMIT :batch_size"
        )
        delete_sql = (
            f'DELETE FROM "{schema}"."{table_name}" WHERE id IN ({select_ids_sql})'
        )
        partition_params = {**(params or {}), **range_params, "batch_size": batch_size}
        deleted_total = 0
        while True:
            with engine.begin() as conn:
                result = conn.execute(text(delete_sql), partition_params)
                deleted = result.rowcount
            deleted_total += deleted
            if deleted == 0:
                break
        return deleted_total

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return sum(pool.map(delete_partition, range(partitions)))


def delete_rows_if_needed(engine, schema, table_name, where_sql, params, needs_work, id_bounds=None):
    """delete_rows() only when needs_work, else prints a skip message.
    Returns whether a delete ran. Start/done timestamps, since
    delete_rows() itself is silent."""
    if not needs_work:
        print(f">> {table_name} for this scope already matches - skipping.")
        return False
    _log_stage(f"Delete {table_name}: start")
    deleted = delete_rows(engine, schema, table_name, where_sql, params, id_bounds=id_bounds)
    _log_stage(f"Delete {table_name}: done ({deleted} rows)")
    return True


def db_matches_pickle(engine, schema, table_name, where_sql, params, expected_ids):
    """Proxy check: count/min(id)/max(id) against the expected id set."""
    if len(expected_ids) == 0:
        return True
    with engine.connect() as conn:
        db_count, db_min, db_max = conn.execute(
            text(f'SELECT count(*), min(id), max(id) FROM "{schema}"."{table_name}" WHERE {where_sql}'),
            params,
        ).one()
    return (
        db_count == len(expected_ids)
        and db_min == min(expected_ids)
        and db_max == max(expected_ids)
    )


def load_id_term_index(pickle_path, id_col="id", term_col="electoral_term"):
    """(id, term) columns from the pickle, via mtime-validated sidecar cache.
    Avoids the 1.6GB load when only the match check is needed."""
    index_path = pickle_path.parent / (pickle_path.stem + "_id_term_index.pkl")
    if index_path.exists() and index_path.stat().st_mtime >= pickle_path.stat().st_mtime:
        return pd.read_pickle(index_path)
    index = pd.read_pickle(pickle_path)[[id_col, term_col]].copy()
    index.to_pickle(index_path)
    return index


# Non-PK indexes from speeches.sql (kept in sync by hand). The RUM index
# dominates write cost on INSERT+DELETE -> drop before bulk writes, one
# CREATE INDEX afterwards. Delta-mode trade-off: search on the WHOLE
# table is unavailable during the drop-rebuild window.
SPEECH_INDEXES = [
    ("politician_id_index", 'CREATE INDEX politician_id_index ON "{schema}".speeches(politician_id)'),
    ("search_faction_id_rumidx", 'CREATE INDEX search_faction_id_rumidx ON "{schema}".speeches(faction_id)'),
    ("search_position_short_rumidx", 'CREATE INDEX search_position_short_rumidx ON "{schema}".speeches(position_short)'),
    ("search_speech_content_rumidx", 'CREATE INDEX search_speech_content_rumidx ON "{schema}".speeches USING rum ("search_speech_content" rum_tsvector_ops)'),
    ("date_index", 'CREATE INDEX date_index ON "{schema}".speeches USING spgist (tsrange("date", "date", \'[]\'))'),
]


def drop_speech_indexes(engine, schema):
    print("Dropping speeches indexes for bulk insert...", end="", flush=True)
    with engine.begin() as conn:
        for name, _ in SPEECH_INDEXES:
            conn.execute(text(f'DROP INDEX IF EXISTS "{schema}"."{name}"'))
    print(" Done.")


def create_speech_indexes(engine, schema):
    for name, ddl in SPEECH_INDEXES:
        _log_stage(f"  {name}: start")
        with engine.begin() as conn:
            conn.execute(text(ddl.format(schema=schema)))
        _log_stage(f"  {name}: done")


def next_id_start(engine, schema, table_name, id_col="id"):
    with engine.connect() as conn:
        max_id = conn.execute(
            text(f'SELECT MAX("{id_col}") FROM "{schema}"."{table_name}"')
        ).scalar()
    return 0 if max_id is None else max_id + 1


engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/next",
    # pre_ping: multi-hour runs, otherwise PendingRollbackError on silently
    # dropped connections (Docker Desktop/Windows).
    pool_pre_ping=True,
    # Headroom for parallel delete partitions/upload chunks.
    pool_size=10,
    max_overflow=5,
)

# Load Final Data

CONTRIBUTIONS_EXTENDED = path_definitions.DATA_FINAL / "contributions_extended.pkl"
SPOKEN_CONTENT = path_definitions.DATA_FINAL / "speech_content.pkl"
PEOPLE = path_definitions.DATA_FINAL / "politicians.csv"
CONTRIBUTIONS_SIMPLIFIED = path_definitions.CONTRIBUTIONS_SIMPLIFIED \
    / "contributions_simplified.pkl"
ELECTORAL_TERMS = path_definitions.ELECTORAL_TERMS / "electoral_terms.csv"

# Load data
electoral_terms = pd.read_csv(ELECTORAL_TERMS)

politicians = pd.read_csv(PEOPLE)
politicians = politicians.drop_duplicates(subset=["ui"], keep="first")
politicians = politicians.drop(
    [
        "electoral_term",
        "faction_id",
        "institution_type",
        "institution_name",
        "constituency",
    ],
    axis=1,
)

politicians.columns = [
    "id",
    "first_name",
    "last_name",
    "birth_place",
    "birth_country",
    "birth_date",
    "death_date",
    "gender",
    "profession",
    "aristocracy",
    "academic_title",
]

series = {
    "id": -1,
    "first_name": "Not found",
    "last_name": "",
    "birth_place": None,
    "birth_country": None,
    "birth_date": None,
    "death_date": None,
    "gender": None,
    "profession": None,
    "aristocracy": None,
    "academic_title": None,
}

politicians = pd.concat([politicians, pd.DataFrame([series])], ignore_index=True)

# Set, not per-row .tolist(): runs once per speech (~1M calls).
POLITICIAN_IDS = set(politicians["id"])


def check_politicians(row):
    speaker_id = row["politician_id"]
    return speaker_id if speaker_id in POLITICIAN_IDS else -1


def convert_date_politicians(date):
    try:
        date = datetime.datetime.strptime(date, "%d.%m.%Y")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date
    except (ValueError, TypeError):
        return None


def convert_date_speeches(date):
    try:
        date = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=date)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        return date
    except (ValueError, TypeError) as e:
        print(e)
        return None


# Upsert - non-period-scoped tables with referenced keys
_log_stage("Upsert reference tables: start")
upsert_dataframe(electoral_terms, "electoral_terms", engine, SCHEMA)

politicians["birth_date"] = politicians["birth_date"].apply(convert_date_politicians)
politicians["death_date"] = politicians["death_date"].apply(convert_date_politicians)

upsert_dataframe(politicians, "politicians", engine, SCHEMA)

# list of all factions in the form ["abbreviation", "full_name"]
factions = [
    ["not found", "not found"],
    ["AfD", "Alternative für Deutschland"],
    ["BHE", "Block der Heimatvertriebenen und Entrechteten"],
    ["BP", "Bayernpartei"],
    ["BSW", "Bündnis Sahra Wagenknecht"],
    ["Grüne", "Bündnis 90/Die Grünen"],
    ["CDU/CSU", "Christlich Demokratische Union Deutschlands/Christlich-Soziale Union in Bayern"],
    ["DA", "Demokratische Arbeitsgemeinschaft"],
    ["DIE LINKE.", "DIE LINKE."],
    ["DP", "Deutsche Partei"],
    ["DP/DPB", "Deutsche Partei/Deutsche Partei Bayern"],
    ["DP/FVP", "Deutsche Partei/Freie Volkspartei"],
    ["DPB", "Deutsche Partei Bayern"],
    ["DRP", "Deutsche Reformpartei"],
    ["DRP/NR", "Deutsche Reichspartei/Nationale Rechte"],
    ["DSU", "Deutsche Soziale Union"],
    ["FDP", "Freie Demokratische Partei"],
    ["FU", "Föderalistische Union"],
    ["FVP", "Freie Volkspartei"],
    ["Fraktionslos", "Fraktionslos"],
    ["GB/BHE", "Gesamtdeutscher Block/Bund der Heimatvertriebenen und Entrechteten"],
    ["Gast", "Gast"],
    ["KO", "Kraft/Oberländer-Gruppe"],
    ["KPD", "Kommunistische Partei Deutschlands"],
    ["NR", "Nationale Rechte"],
    ["PDS", "Partei des Demokratischen Sozialismus"],
    ["SPD", "Sozialdemokratische Partei Deutschlands"],
    ["SSW", "Südschleswigscher Wählerverband"],
    ["WAV", "Wirtschaftliche Aufbau-Vereinigung"],
    ["Z", "Deutsche Zentrumspartei"],
]

# convert to dataframe and add id-field
factions = pd.DataFrame(
    [[idx-1, *entry] for idx, entry in enumerate(factions)],
    columns=["id", "abbreviation", "full_name"],
)
factions["id"] = factions["id"].astype(int)

upsert_dataframe(factions, "factions", engine, SCHEMA)
_log_stage("Upsert reference tables: done")

# Cheap (id, term) index - for match checks and speech_id->term mapping.
speech_index = load_id_term_index(SPOKEN_CONTENT)
speech_term_by_id = speech_index.set_index("id")["electoral_term"]


def _speeches_term_ids(term):
    return set(speech_index.loc[speech_index["electoral_term"] == term, "id"])


def _speeches_needs_work(term, term_ids):
    """Match check per term (not combined - one mismatching term would
    otherwise force all others too). Cheap, fine to call repeatedly."""
    return FORCE_DELETE or not db_matches_pickle(
        engine, SCHEMA, "speeches", "electoral_term = :term", {"term": term}, term_ids
    )


def _upload_term(df, table_name, term):
    """Upload a frame already scoped to one term; empty (skipped) frames
    are ignored."""
    if len(df) > 0:
        upload_with_progress(
            df, table_name, engine, SCHEMA,
            label=f"Upload {table_name} (Wahlperiode {term}, {len(df)} rows)...",
        )


any_speeches_work = DELTA_TERMS is not None and any(
    _speeches_needs_work(term, _speeches_term_ids(term)) for term in DELTA_TERMS
)

if DELTA_TERMS is not None and not any_speeches_work:
    print(f">> speeches for term(s) {DELTA_TERMS} already match - skipping the full 1.6GB load+transform.")
    speeches = speech_index.iloc[0:0].reindex(
        columns=[
            "id", "session", "electoral_term", "first_name", "last_name",
            "faction_id", "position_short", "position_long", "politician_id",
            "speech_content", "date",
        ]
    )
else:
    _log_stage("Load speeches pickle (1.6GB) + transform: start")
    speeches = pd.read_pickle(SPOKEN_CONTENT)

    speeches["date"] = speeches["date"].apply(convert_date_speeches)

    speeches = speeches.where((pd.notnull(speeches)), None)
    speeches["position_long"] = speeches["position_long"].replace(
        [r"^\s*$"], [None], regex=True
    )
    speeches["politician_id"] = speeches.apply(check_politicians, axis=1)
    _log_stage("Load speeches pickle + transform: done")

_log_stage("Load contributions_extended pickle + transform: start")
contributions_extended = pd.read_pickle(CONTRIBUTIONS_EXTENDED)

contributions_extended = contributions_extended.where(
    (pd.notnull(contributions_extended)), None
)
_log_stage("Load contributions_extended pickle + transform: done")

_log_stage("Load contributions_simplified pickles + transform: start")
contributions_simplified_parts = [pd.read_pickle(CONTRIBUTIONS_SIMPLIFIED)]
for folder_path in sorted(path_definitions.CONTRIBUTIONS_SIMPLIFIED.iterdir()):
    if not folder_path.is_dir() or not folder_path.name.startswith("electoral_term_"):
        continue
    contributions_simplified_parts.append(
        pd.read_pickle(folder_path / "contributions_simplified.pkl")
    )

contributions_simplified = pd.concat(contributions_simplified_parts, sort=False)

contributions_simplified = contributions_simplified.where(
    (pd.notnull(contributions_simplified)), None
)
_log_stage("Load contributions_simplified pickles + transform: done")

if DELTA_TERMS is None:
    # FULL REBUILD
    # init id from pipeline 1:1 (0-based for WP1-18, incr 1_000_000 for WP19+)
    contributions_simplified["id"] = range(len(contributions_simplified.content))

    _log_stage("Drop speeches indexes: start")
    drop_speech_indexes(engine, SCHEMA)
    _log_stage("Drop speeches indexes: done")

    _log_stage("Upload speeches: start")
    upload_by_period(speeches, "speeches", engine, SCHEMA, speeches["electoral_term"])
    _log_stage("Upload speeches: done")

    _log_stage("Rebuild speeches indexes: start")
    create_speech_indexes(engine, SCHEMA)
    _log_stage("Rebuild speeches indexes: done")

    _log_stage("Upload contributions_extended: start")
    upload_by_period(
        contributions_extended,
        "contributions_extended",
        engine,
        SCHEMA,
        contributions_extended["speech_id"].map(speech_term_by_id),
    )
    _log_stage("Upload contributions_extended: done")

    _log_stage("Upload contributions_simplified: start")
    upload_by_period(
        contributions_simplified,
        "contributions_simplified",
        engine,
        SCHEMA,
        contributions_simplified["speech_id"].map(speech_term_by_id),
    )
    _log_stage("Upload contributions_simplified: done")
else:
    # DELTA - term by term (each term = one contiguous id block).
    print(
        f"Delta load for electoral term(s): {DELTA_TERMS}"
        + (" [--force]" if FORCE_DELETE else "")
    )

    # Index drop/rebuild brackets the WHOLE loop (RUM rebuild ~15min,
    # at most once per run).
    if any_speeches_work:
        drop_speech_indexes(engine, SCHEMA)

    term_filter_sql = "electoral_term = :term"
    speech_scope_sql = (
        f"speech_id IN (SELECT id FROM {SCHEMA}.speeches WHERE {term_filter_sql})"
    )

    def _simplified_db_count(scope_params):
        with engine.connect() as conn:
            return conn.execute(
                text(
                    f'SELECT count(*) FROM "{SCHEMA}"."contributions_simplified" WHERE {speech_scope_sql}'
                ),
                scope_params,
            ).scalar()

    for term in DELTA_TERMS:
        term_ids = _speeches_term_ids(term)
        if len(term_ids) == 0:
            print(f"No speeches found for term {term} - nothing to do.")
            continue

        scope_params = {"term": term}

        term_speeches = speeches[speeches["electoral_term"] == term].copy()
        term_contrib_ext = contributions_extended[
            contributions_extended["speech_id"].isin(term_ids)
        ].copy()
        term_contrib_simplified = contributions_simplified[
            contributions_simplified["speech_id"].isin(term_ids)
        ].copy()

        # Checks BEFORE the deletes (scope subqueries need speeches intact).
        # Replacing speeches forces replacing contributions (ids shift ->
        # FK). FORCE_DELETE is folded into _speeches_needs_work.
        speeches_needs_work = _speeches_needs_work(term, term_ids)
        ext_needs_work = speeches_needs_work or not db_matches_pickle(
            engine, SCHEMA, "contributions_extended", speech_scope_sql, scope_params,
            set(term_contrib_ext["id"]),
        )
        simplified_needs_work = (
            speeches_needs_work
            or _simplified_db_count(scope_params) != len(term_contrib_simplified)
        )

        # Delete order: contributions_* first (FK on speeches.id),
        # insert order below is the reverse.
        ext_deleted = delete_rows_if_needed(
            engine, SCHEMA, "contributions_extended", speech_scope_sql, scope_params, ext_needs_work,
        )
        simplified_deleted = delete_rows_if_needed(
            engine, SCHEMA, "contributions_simplified", speech_scope_sql, scope_params, simplified_needs_work,
        )
        if delete_rows_if_needed(
            engine, SCHEMA, "speeches", term_filter_sql, scope_params,
            speeches_needs_work, id_bounds=(min(term_ids), max(term_ids)),
        ):
            speeches_offset = next_id_start(engine, SCHEMA, "speeches") - min(term_ids)
            term_speeches["id"] += speeches_offset
        else:
            speeches_offset = 0
            term_speeches = term_speeches.iloc[0:0]

        # speech_id references move along (0 if speeches unchanged).
        term_contrib_ext["speech_id"] += speeches_offset
        term_contrib_simplified["speech_id"] += speeches_offset

        # ext.id: own PK space, same offset rebase as speeches.
        if ext_deleted:
            if len(term_contrib_ext) > 0:
                ext_offset = (
                    next_id_start(engine, SCHEMA, "contributions_extended")
                    - term_contrib_ext["id"].min()
                )
                term_contrib_ext["id"] += ext_offset
        else:
            term_contrib_ext = term_contrib_ext.iloc[0:0]

        # simplified.id: no stable pipeline id -> always freshly assigned.
        if simplified_deleted:
            simplified_next_id = next_id_start(engine, SCHEMA, "contributions_simplified")
            term_contrib_simplified = term_contrib_simplified.reset_index(drop=True)
            term_contrib_simplified["id"] = range(
                simplified_next_id, simplified_next_id + len(term_contrib_simplified)
            )
        else:
            term_contrib_simplified = term_contrib_simplified.iloc[0:0]

        # Insert order: speeches first (FK target).
        _upload_term(term_speeches, "speeches", term)
        _upload_term(term_contrib_ext, "contributions_extended", term)
        _upload_term(term_contrib_simplified, "contributions_simplified", term)

    if any_speeches_work:
        create_speech_indexes(engine, SCHEMA)
