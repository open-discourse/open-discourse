CREATE OR REPLACE FUNCTION app_public.search_speeches (politician_id_query int8 DEFAULT -1, faction_id_query int8 DEFAULT -1, "position_short_query" text DEFAULT '', content_query text DEFAULT '', from_date date DEFAULT NULL, to_date date DEFAULT NULL)
  RETURNS TABLE (
    id int8,
    "position_short" varchar,
    "date" date,
    speech_content text,
    document_url varchar,
    rank float4,
    first_name varchar,
    last_name varchar,
    abbreviation varchar
  )
  AS $$
DECLARE
  has_politician_id boolean = politician_id_query > -1;
  DECLARE has_faction_id boolean = faction_id_query > -1;
  DECLARE has_content boolean = length(TRIM(content_query)) > 0;
  DECLARE has_position_short boolean = length(TRIM(position_short_query)) > 0;
  DECLARE position_short_tsquery tsquery = websearch_to_tsquery ('simple', position_short_query);
  DECLARE content_tsquery tsquery = websearch_to_tsquery ('german', content_query);
BEGIN
  RETURN QUERY
  SELECT
    s.id,
    s.position_short,
    s.date,
    s.speech_content,
    s.document_url,
    ts_rank(search_speech_content, content_tsquery) + ts_rank(search_position_short, position_short_tsquery) AS rank,
    p.first_name,
    p.last_name,
    f.abbreviation
  FROM
    app_public.speeches s
  LEFT JOIN app_public.politicians p ON p.id=s.politician_id
  LEFT JOIN app_public.factions f ON f.id=s.faction_id
  WHERE (
    CASE WHEN has_politician_id
      AND NOT has_faction_id
      AND NOT has_content THEN
      politician_id=politician_id_query
    WHEN has_politician_id
      AND has_position_short
      AND NOT has_content THEN
      politician_id=politician_id_query
      AND search_position_short @@ position_short_tsquery
    WHEN has_politician_id
      AND has_content
      AND NOT has_position_short THEN
      politician_id=politician_id_query
      AND search_speech_content @@ content_tsquery
    WHEN has_politician_id
      AND has_content
      AND has_position_short THEN
      politician_id=politician_id_query
      AND search_speech_content @@ content_tsquery
      AND search_position_short @@ position_short_tsquery
    WHEN has_content
      AND NOT has_politician_id
      AND NOT has_position_short THEN
      search_speech_content @@ content_tsquery
    WHEN has_content
      AND has_position_short
      AND NOT has_politician_id THEN
      search_speech_content @@ content_tsquery
      AND search_position_short @@ position_short_tsquery
    WHEN has_position_short
      AND NOT has_content
      AND NOT has_politician_id THEN
      search_position_short @@ position_short_tsquery
    ELSE
      s.id IS NOT NULL
    END)
    AND (
      CASE WHEN from_date IS NOT NULL
        AND to_date IS NOT NULL THEN
        s.date BETWEEN from_date
        AND to_date
      WHEN from_date IS NOT NULL
        AND to_date IS NULL THEN
        s.date > from_date
      WHEN to_date IS NOT NULL
        AND from_date IS NULL THEN
        s.date < to_date
      ELSE
        s.id IS NOT NULL
      END)
  ORDER BY
    rank DESC;
END;
$$
LANGUAGE 'plpgsql'
STABLE;
