CREATE TABLE app_public.speeches (
	id int8 NOT NULL,
	sitting int8 NOT NULL,
	wp int8 NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	people_id int8 NOT NULL,
	speech_content text NOT NULL,
	faction_id int8 NOT NULL,
	"position_short" varchar NOT NULL,
	"position_long" varchar NULL,
	"date" int8 NULL,
	CONSTRAINT speeches_pk PRIMARY KEY (id),
	CONSTRAINT speeches_fk FOREIGN KEY (people_id) REFERENCES app_public.people(id),
	CONSTRAINT speeches_fk_1 FOREIGN KEY (faction_id) REFERENCES app_public.factions(id),
	CONSTRAINT speeches_fk_2 FOREIGN KEY (wp) REFERENCES app_public.election_periods(id)
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_public.speeches TO visitor;
