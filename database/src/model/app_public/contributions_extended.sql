CREATE TABLE app_public.contributions_extended (
	id int8 NOT NULL,
	"type" varchar NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	politician_id int8 NULL,
	"content" text NULL,
	speech_id int8 NOT NULL,
	text_position int8 NOT NULL,
	faction_id int8 NULL,
	CONSTRAINT contributions_extended_pk PRIMARY KEY (id),
	CONSTRAINT contributions_extended_fk FOREIGN KEY (faction_id) REFERENCES app_public.factions(id),
	CONSTRAINT contributions_extended_fk_1 FOREIGN KEY (speech_id) REFERENCES app_public.speeches(id),
	CONSTRAINT contributions_extended_fk_2 FOREIGN KEY (politician_id) REFERENCES app_public.politicians(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.contributions_extended TO visitor;
