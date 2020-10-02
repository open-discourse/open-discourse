DO $$
BEGIN
  CREATE ROLE visitor WITH NOLOGIN;
  EXCEPTION WHEN DUPLICATE_OBJECT THEN
  RAISE NOTICE 'not creating role my_role -- it already exists';
END
$$;

CREATE EXTENSION pgcrypto;
