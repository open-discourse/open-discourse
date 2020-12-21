CREATE TABLE open_discourse.factions (
	id int8 NOT NULL,
	abbreviation varchar NOT NULL,
	full_name varchar NOT NULL,
	CONSTRAINT factions_pk PRIMARY KEY (id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE open_discourse.factions TO visitor;
