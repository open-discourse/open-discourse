CREATE TABLE app_public.speeches (
	id int8 NOT NULL,
	session int8 NOT NULL,
	electoral_term int8 NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	politician_id int8 NOT NULL,
	speech_content text NOT NULL,
	faction_id int8 NOT NULL,
	document_url varchar NOT NULL,
	"position_short" varchar NOT NULL,
	"position_long" varchar NULL,
	"date" date NULL,
	CONSTRAINT speeches_pk PRIMARY KEY (id),
	CONSTRAINT speeches_fk FOREIGN KEY (politician_id) REFERENCES app_public.politicians(id),
	CONSTRAINT speeches_fk_1 FOREIGN KEY (faction_id) REFERENCES app_public.factions(id),
	CONSTRAINT speeches_fk_2 FOREIGN KEY (electoral_term) REFERENCES app_public.electoral_terms(id),
	search_speech_content tsvector GENERATED always AS ((to_tsvector('german', app_public.speeches.speech_content))) stored
);

CREATE INDEX politician_id_index ON app_public.speeches(politician_id);

CREATE INDEX search_faction_id_rumidx ON app_public.speeches(faction_id);

CREATE INDEX search_position_short_rumidx ON app_public.speeches(position_short);

CREATE INDEX search_speech_content_rumidx ON app_public.speeches USING rum ("search_speech_content" rum_tsvector_ops);

CREATE INDEX date_index ON app_public.speeches USING spgist (tsrange("date", "date", '[]'));

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.speeches TO visitor;
