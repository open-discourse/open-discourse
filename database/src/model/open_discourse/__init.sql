CREATE SCHEMA open_discourse;
GRANT USAGE ON SCHEMA open_discourse TO visitor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA open_discourse TO visitor;

CREATE OR REPLACE FUNCTION open_discourse.trigger_set_timestamp ()
  RETURNS TRIGGER
  AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE EXTENSION rum;
