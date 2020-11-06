CREATE OR REPLACE FUNCTION app_public.search_speeches (politician_id_query int8 DEFAULT -2, faction_id_query int8 DEFAULT -2, "position_short_query" text DEFAULT '', content_query text DEFAULT '', from_date date DEFAULT NULL, to_date date DEFAULT NULL)
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
  has_politician_id boolean = politician_id_query > -2;
  DECLARE has_faction_id boolean = faction_id_query > -2;
  DECLARE has_content boolean = length(TRIM(content_query)) > 0;
  DECLARE has_position_short boolean = length(TRIM(position_short_query)) > 0;
  DECLARE content_tsquery tsquery = websearch_to_tsquery ('german', content_query);
BEGIN
  RETURN QUERY
  SELECT
    s.id,
    s.position_short,
    s.date,
    s.speech_content,
    s.document_url,
    ts_rank(search_speech_content, content_tsquery) AS rank,
    p.first_name,
    p.last_name,
    f.abbreviation
  FROM
    app_public.speeches s
  LEFT JOIN app_public.politicians p ON p.id=s.politician_id
  LEFT JOIN app_public.factions f ON f.id=s.faction_id
  WHERE (
        ((NOT has_politician_id) OR politician_id = politician_id_query)
    AND ((NOT has_faction_id) OR faction_id = faction_id_query)
    AND ((NOT has_content) OR search_speech_content @@ content_tsquery)
    AND ((NOT has_position_short) OR position_short = position_short_query)

    AND ((from_date IS NULL) OR s.date > from_date)
    AND ((to_date IS NULL) OR s.date < to_date)
  )
  ORDER BY
    rank DESC;
END;
$$
LANGUAGE 'plpgsql'
STABLE;
