CREATE TABLE open_discourse.contributions (
	id int8 NOT NULL,
	"type" varchar NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	politician_id int8 NULL,
	"content" text NULL,
	speech_id int8 NOT NULL,
	text_position int8 NOT NULL,
	faction_id int8 NULL,
	CONSTRAINT contributions_pk PRIMARY KEY (id),
	CONSTRAINT contributions_fk FOREIGN KEY (faction_id) REFERENCES open_discourse.factions(id),
	CONSTRAINT contributions_fk_1 FOREIGN KEY (speech_id) REFERENCES open_discourse.speeches(id),
	CONSTRAINT contributions_fk_2 FOREIGN KEY (politician_id) REFERENCES open_discourse.politicians(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE open_discourse.contributions TO visitor;
