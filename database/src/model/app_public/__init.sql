CREATE SCHEMA app_public;
GRANT USAGE ON SCHEMA app_public TO visitor;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app_public TO visitor;

CREATE OR REPLACE FUNCTION app_public.trigger_set_timestamp ()
  RETURNS TRIGGER
  AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE EXTENSION rum;
