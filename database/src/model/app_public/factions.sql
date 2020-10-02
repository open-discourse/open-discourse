CREATE TABLE app_public.factions (
	id int8 NOT NULL,
	abbreviation varchar NOT NULL,
	full_name varchar NOT NULL,
	CONSTRAINT factions_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.factions TO visitor;
